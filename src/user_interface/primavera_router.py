"""FastAPI router for Primavera P6 integration with CSCSC AI Agent."""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.integration.primavera_connector import PrimaveraConnector
from src.integration.primavera_data_processor import PrimaveraDataProcessor
from src.integration.primavera_database import PrimaveraDatabase

# Create router for Primavera P6 integration
router = APIRouter(
    prefix="/api/v1/primavera",
    tags=["primavera"],
    responses={404: {"description": "Not found"}},
)

# Initialize components
P6_PATH = os.environ.get('P6_INSTALLATION_PATH', r"C:\Program Files\Oracle\Primavera P6\P6 Professional\21.12.0")
connector = PrimaveraConnector()
data_processor = PrimaveraDataProcessor(connector, P6_PATH)
database = PrimaveraDatabase()

# Pydantic models for request/response validation
class StatusResponse(BaseModel):
    status: str
    connection: str
    p6_path: str
    p6_exists: bool

class ErrorResponse(BaseModel):
    status: str
    message: str

class ProjectResponse(BaseModel):
    id: str
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    progress: float = 0

class ProjectsResponse(BaseModel):
    status: str
    projects: List[ProjectResponse]
    source: str

class ImportRequest(BaseModel):
    type: str = "api"  # 'api', 'database', or 'file'
    source: str = "user-initiated"

class ImportResponse(BaseModel):
    status: str
    import_id: Optional[int] = None
    project_count: int = 0
    activity_count: int = 0

class QueryRequest(BaseModel):
    query: str


@router.get("/status", response_model=StatusResponse, responses={500: {"model": ErrorResponse}})
async def get_status():
    """Get status of Primavera P6 integration."""
    try:
        connection_status = connector.connect()
        return {
            "status": "success",
            "connection": "active" if connection_status else "inactive",
            "p6_path": P6_PATH,
            "p6_exists": os.path.exists(P6_PATH)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": str(e)
        })


@router.get("/projects", response_model=ProjectsResponse, responses={500: {"model": ErrorResponse}})
async def get_projects():
    """Get all projects from Primavera P6."""
    try:
        # First check database
        db_projects = database.get_projects()
        
        if db_projects:
            # Use projects from database
            projects = [{
                "id": p.get("proj_id"),
                "name": p.get("proj_name"),
                "start_date": p.get("act_start_date") or p.get("target_start_date"),
                "end_date": p.get("act_end_date") or p.get("target_end_date"),
                "progress": p.get("progress", 0)
            } for p in db_projects]
            
            return {
                "status": "success",
                "projects": projects,
                "source": "database"
            }
        
        # If no projects in database, try to get from P6
        connector.connect()
        p6_projects = connector.get_projects()
        
        if p6_projects:
            # Store projects in database
            database.store_projects(p6_projects)
            
            # Format projects for response
            projects = [{
                "id": p.get("proj_id"),
                "name": p.get("proj_name"),
                "start_date": p.get("act_start_date") or p.get("target_start_date"),
                "end_date": p.get("act_end_date") or p.get("target_end_date"),
                "progress": 0  # Default progress
            } for p in p6_projects]
            
            return {
                "status": "success",
                "projects": projects,
                "source": "primavera"
            }
        
        # If no projects in P6, generate demo data
        demo_projects = generate_demo_projects()
        
        return {
            "status": "success",
            "projects": demo_projects,
            "source": "demo"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": str(e)
        })


@router.get("/projects/{proj_id}/details", responses={500: {"model": ErrorResponse}})
async def get_project_details(proj_id: str = Path(..., title="Project ID")):
    """Get detailed information for a specific project."""
    try:
        # Get project data
        project_data = data_processor.get_project_data(proj_id)
        
        if not project_data:
            # Try to generate demo data for project
            return generate_demo_project_details(proj_id)
        
        # Process data for visualization
        visualization_data = data_processor.prepare_for_visualization(project_data)
        
        return {
            "status": "success",
            "project_id": proj_id,
            "gantt_data": visualization_data.get("gantt_data", [])[0] if visualization_data.get("gantt_data") else None,
            "resource_data": visualization_data.get("resource_data", [])[0] if visualization_data.get("resource_data") else None,
            "progress_data": visualization_data.get("progress_data", [])[0] if visualization_data.get("progress_data") else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": str(e)
        })


@router.post("/query", responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def query_primavera_data(query_req: QueryRequest):
    """Query Primavera P6 data using natural language."""
    try:
        query = query_req.query
        
        if not query:
            raise HTTPException(status_code=400, detail={
                "status": "error",
                "message": "Query is required"
            })
        
        # Process query using simple keyword matching
        query_lower = query.lower()
        
        # Determine query intent
        if any(keyword in query_lower for keyword in ["late", "behind", "delay", "overdue"]):
            # Query for late activities
            result = query_late_activities()
            text_result = "Here are the activities that are behind schedule:"
            visualization = create_late_activities_visualization(result)
        elif any(keyword in query_lower for keyword in ["progress", "status", "completion", "percent"]):
            # Query for project progress
            result = query_project_progress()
            text_result = "Here is the current progress status of all projects:"
            visualization = create_progress_visualization(result)
        elif any(keyword in query_lower for keyword in ["resource", "allocation", "utilization"]):
            # Query for resource allocation
            result = query_resource_allocation()
            text_result = "Here is the current resource allocation across projects:"
            visualization = create_resource_visualization(result)
        elif any(keyword in query_lower for keyword in ["critical", "path", "key activities"]):
            # Query for critical path
            result = query_critical_path()
            text_result = "Here are the activities on the critical path:"
            visualization = create_critical_path_visualization(result)
        else:
            # Default response for unknown queries
            return {
                "status": "success",
                "result": f"I'm not sure how to answer: '{query}'. Try asking about late activities, project progress, resource allocation, or critical path."
            }
        
        return {
            "status": "success",
            "text_result": text_result,
            "result": result,
            "visualization": visualization
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": str(e)
        })


@router.post("/import", response_model=ImportResponse, responses={500: {"model": ErrorResponse}})
async def import_primavera_data(import_req: ImportRequest):
    """Import data from Primavera P6."""
    try:
        import_type = import_req.type
        source = import_req.source
        
        # Connect to Primavera
        connector.connection_type = import_type
        connection_success = connector.connect()
        
        if not connection_success:
            raise HTTPException(status_code=500, detail={
                "status": "error",
                "message": f"Failed to connect to Primavera using {import_type} connection"
            })
        
        # Import projects
        projects = connector.get_projects()
        project_count = database.store_projects(projects)
        
        # Import activities for each project
        activity_count = 0
        for project in projects:
            activities = connector.get_activities(project.get("proj_id"))
            activity_count += database.store_activities(activities)
        
        # Log import
        import_id = database.store_import_log(
            import_type=import_type,
            source=source,
            status="success",
            message=f"Imported {project_count} projects and {activity_count} activities",
            metadata={"project_count": project_count, "activity_count": activity_count}
        )
        
        return {
            "status": "success",
            "import_id": import_id,
            "project_count": project_count,
            "activity_count": activity_count
        }
    except HTTPException:
        raise
    except Exception as e:
        # Log import error
        database.store_import_log(
            import_type=import_req.type,
            source=import_req.source,
            status="error",
            message=str(e)
        )
        
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": str(e)
        })


# Helper functions for generating demo data
def generate_demo_projects():
    """Generate demo projects when no real data is available."""
    return [
        {
            "id": "DEMO-001",
            "name": "Office Building Construction",
            "start_date": "2025-01-15",
            "end_date": "2025-10-30",
            "progress": 35.8
        },
        {
            "id": "DEMO-002",
            "name": "Highway Infrastructure Project",
            "start_date": "2024-11-10",
            "end_date": "2026-05-20",
            "progress": 15.2
        },
        {
            "id": "DEMO-003",
            "name": "Solar Farm Installation",
            "start_date": "2025-02-01",
            "end_date": "2025-08-15",
            "progress": 42.5
        }
    ]


def generate_demo_project_details(proj_id):
    """Generate detailed demo project data."""
    # Generate activities based on the project ID
    activities = [
        {
            "id": f"{proj_id}-ACT-001",
            "name": "Project Planning & Design",
            "start_date": "2025-01-15" if proj_id == "DEMO-001" else ("2024-11-10" if proj_id == "DEMO-002" else "2025-02-01"),
            "end_date": "2025-03-01" if proj_id == "DEMO-001" else ("2025-01-15" if proj_id == "DEMO-002" else "2025-03-10"),
            "status": "Completed" if proj_id == "DEMO-001" else "In Progress",
            "progress": 100 if proj_id == "DEMO-001" else 75,
            "resources": ["Design Team", "Project Manager"],
            "predecessors": [],
            "critical": True
        },
        {
            "id": f"{proj_id}-ACT-002",
            "name": "Procurement & Mobilization",
            "start_date": "2025-03-02" if proj_id == "DEMO-001" else ("2025-01-16" if proj_id == "DEMO-002" else "2025-03-11"),
            "end_date": "2025-04-15" if proj_id == "DEMO-001" else ("2025-03-20" if proj_id == "DEMO-002" else "2025-04-15"),
            "status": "Completed" if proj_id == "DEMO-001" else "Not Started",
            "progress": 100 if proj_id == "DEMO-001" else 0,
            "resources": ["Procurement Team", "Operations"],
            "predecessors": [f"{proj_id}-ACT-001"],
            "critical": True
        },
        {
            "id": f"{proj_id}-ACT-003",
            "name": "Foundation Work",
            "start_date": "2025-04-16" if proj_id == "DEMO-001" else ("2025-03-21" if proj_id == "DEMO-002" else "2025-04-16"),
            "end_date": "2025-06-10" if proj_id == "DEMO-001" else ("2025-07-15" if proj_id == "DEMO-002" else "2025-05-30"),
            "status": "In Progress" if proj_id == "DEMO-001" else "Not Started",
            "progress": 60 if proj_id == "DEMO-001" else 0,
            "resources": ["Construction Crew A", "Engineers"],
            "predecessors": [f"{proj_id}-ACT-002"],
            "critical": True
        },
        {
            "id": f"{proj_id}-ACT-004",
            "name": "Structural Framework",
            "start_date": "2025-06-11" if proj_id == "DEMO-001" else ("2025-07-16" if proj_id == "DEMO-002" else "2025-05-31"),
            "end_date": "2025-08-20" if proj_id == "DEMO-001" else ("2025-12-30" if proj_id == "DEMO-002" else "2025-07-10"),
            "status": "Not Started",
            "progress": 0,
            "resources": ["Construction Crew B", "Structural Engineers"],
            "predecessors": [f"{proj_id}-ACT-003"],
            "critical": True
        },
        {
            "id": f"{proj_id}-ACT-005",
            "name": "Exterior Finishes",
            "start_date": "2025-08-21" if proj_id == "DEMO-001" else ("2026-01-01" if proj_id == "DEMO-002" else "2025-07-11"),
            "end_date": "2025-09-30" if proj_id == "DEMO-001" else ("2026-03-30" if proj_id == "DEMO-002" else "2025-08-05"),
            "status": "Not Started",
            "progress": 0,
            "resources": ["Construction Crew C", "Specialists"],
            "predecessors": [f"{proj_id}-ACT-004"],
            "critical": False
        },
        {
            "id": f"{proj_id}-ACT-006",
            "name": "Interior Work & Finishes",
            "start_date": "2025-09-01" if proj_id == "DEMO-001" else ("2026-02-15" if proj_id == "DEMO-002" else "2025-07-20"),
            "end_date": "2025-10-20" if proj_id == "DEMO-001" else ("2026-04-30" if proj_id == "DEMO-002" else "2025-08-10"),
            "status": "Not Started",
            "progress": 0,
            "resources": ["Interior Specialists", "Construction Crew D"],
            "predecessors": [f"{proj_id}-ACT-004"],
            "critical": True
        },
        {
            "id": f"{proj_id}-ACT-007",
            "name": "Testing & Commissioning",
            "start_date": "2025-10-21" if proj_id == "DEMO-001" else ("2026-05-01" if proj_id == "DEMO-002" else "2025-08-06"),
            "end_date": "2025-10-30" if proj_id == "DEMO-001" else ("2026-05-20" if proj_id == "DEMO-002" else "2025-08-15"),
            "status": "Not Started",
            "progress": 0,
            "resources": ["QA Team", "Engineers", "Project Manager"],
            "predecessors": [f"{proj_id}-ACT-005", f"{proj_id}-ACT-006"],
            "critical": True
        }
    ]
    
    # Generate resource data
    resource_allocation = [
        {"resource": "Project Manager", "allocation": 100},
        {"resource": "Design Team", "allocation": 85},
        {"resource": "Engineers", "allocation": 90},
        {"resource": "Construction Crew A", "allocation": 100},
        {"resource": "Construction Crew B", "allocation": 75},
        {"resource": "Construction Crew C", "allocation": 50},
        {"resource": "Construction Crew D", "allocation": 25},
        {"resource": "Procurement Team", "allocation": 60},
        {"resource": "QA Team", "allocation": 30},
        {"resource": "Specialists", "allocation": 40},
        {"resource": "Structural Engineers", "allocation": 80},
        {"resource": "Interior Specialists", "allocation": 20}
    ]
    
    # Generate progress data (S-curve)
    progress_data = {
        "dates": [
            "2025-01-15", "2025-02-15", "2025-03-15", "2025-04-15", 
            "2025-05-15", "2025-06-15", "2025-07-15", "2025-08-15", 
            "2025-09-15", "2025-10-30"
        ] if proj_id == "DEMO-001" else [
            "2024-11-10", "2024-12-10", "2025-01-10", "2025-02-10", 
            "2025-03-10", "2025-04-10", "2025-05-10", "2025-06-10", 
            "2025-07-10", "2025-08-10", "2025-09-10", "2025-10-10", 
            "2025-11-10", "2025-12-10", "2026-01-10", "2026-02-10", 
            "2026-03-10", "2026-04-10", "2026-05-20"
        ] if proj_id == "DEMO-002" else [
            "2025-02-01", "2025-03-01", "2025-04-01", "2025-05-01", 
            "2025-06-01", "2025-07-01", "2025-08-15"
        ],
        "planned": [
            0, 5, 15, 30, 45, 60, 75, 85, 95, 100
        ] if proj_id == "DEMO-001" else [
            0, 3, 7, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 85, 90, 95, 98, 100
        ] if proj_id == "DEMO-002" else [
            0, 10, 30, 50, 70, 90, 100
        ],
        "actual": [
            0, 3, 12, 29, 42, 36
        ] if proj_id == "DEMO-001" else [
            0, 2, 5, 8, 12, 15
        ] if proj_id == "DEMO-002" else [
            0, 8, 25, 42
        ]
    }
    
    # Prepare data for visualization
    gantt_data = {
        "tasks": activities,
        "project_name": "Office Building Construction" if proj_id == "DEMO-001" else 
                      ("Highway Infrastructure Project" if proj_id == "DEMO-002" else 
                       "Solar Farm Installation"),
        "start_date": "2025-01-15" if proj_id == "DEMO-001" else 
                     ("2024-11-10" if proj_id == "DEMO-002" else "2025-02-01"),
        "end_date": "2025-10-30" if proj_id == "DEMO-001" else 
                    ("2026-05-20" if proj_id == "DEMO-002" else "2025-08-15"),
        "critical_path": [activity["id"] for activity in activities if activity["critical"]]
    }
    
    resource_data = {
        "resources": resource_allocation
    }
    
    return {
        "status": "success",
        "project_id": proj_id,
        "project_info": {
            "name": "Office Building Construction" if proj_id == "DEMO-001" else 
                  ("Highway Infrastructure Project" if proj_id == "DEMO-002" else 
                   "Solar Farm Installation"),
            "start_date": "2025-01-15" if proj_id == "DEMO-001" else 
                         ("2024-11-10" if proj_id == "DEMO-002" else "2025-02-01"),
            "end_date": "2025-10-30" if proj_id == "DEMO-001" else 
                        ("2026-05-20" if proj_id == "DEMO-002" else "2025-08-15"),
            "progress": 35.8 if proj_id == "DEMO-001" else 
                        (15.2 if proj_id == "DEMO-002" else 42.5),
            "status": "In Progress"
        },
        "gantt_data": gantt_data,
        "resource_data": resource_data,
        "progress_data": progress_data
    }


def query_late_activities():
    """Query for late activities across projects."""
    # In a real implementation, this would query the database
    # For demo purposes, generate some sample data
    late_activities = [
        {
            "project_id": "DEMO-001",
            "project_name": "Office Building Construction",
            "activity_id": "DEMO-001-ACT-003",
            "activity_name": "Foundation Work",
            "planned_end_date": "2025-06-01",
            "forecasted_end_date": "2025-06-10",
            "delay": 9,  # Days
            "impact": "Medium"
        },
        {
            "project_id": "DEMO-002",
            "project_name": "Highway Infrastructure Project",
            "activity_id": "DEMO-002-ACT-002",
            "activity_name": "Procurement & Mobilization",
            "planned_end_date": "2025-03-10",
            "forecasted_end_date": "2025-03-20",
            "delay": 10,  # Days
            "impact": "High"
        }
    ]
    return late_activities


def create_late_activities_visualization(late_activities):
    """Create visualization data for late activities."""
    return {
        "type": "bar",
        "data": {
            "labels": [activity["activity_name"] for activity in late_activities],
            "datasets": [{
                "label": "Delay (Days)",
                "data": [activity["delay"] for activity in late_activities],
                "backgroundColor": ["#dc3545" if activity["impact"] == "High" else 
                                  ("#ffc107" if activity["impact"] == "Medium" else "#28a745") 
                                  for activity in late_activities]
            }]
        }
    }


def query_project_progress():
    """Query for progress status of all projects."""
    # In a real implementation, this would query the database
    progress_data = [
        {
            "project_id": "DEMO-001",
            "project_name": "Office Building Construction",
            "planned_progress": 60,
            "actual_progress": 35.8,
            "variance": -24.2,
            "status": "Behind Schedule"
        },
        {
            "project_id": "DEMO-002",
            "project_name": "Highway Infrastructure Project",
            "planned_progress": 20,
            "actual_progress": 15.2,
            "variance": -4.8,
            "status": "Slightly Behind"
        },
        {
            "project_id": "DEMO-003",
            "project_name": "Solar Farm Installation",
            "planned_progress": 40,
            "actual_progress": 42.5,
            "variance": 2.5,
            "status": "On Track"
        }
    ]
    return progress_data


def create_progress_visualization(progress_data):
    """Create visualization data for project progress."""
    return {
        "type": "bar",
        "data": {
            "labels": [project["project_name"] for project in progress_data],
            "datasets": [
                {
                    "label": "Planned Progress (%)",
                    "data": [project["planned_progress"] for project in progress_data],
                    "backgroundColor": "rgba(54, 162, 235, 0.5)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 1
                },
                {
                    "label": "Actual Progress (%)",
                    "data": [project["actual_progress"] for project in progress_data],
                    "backgroundColor": "rgba(255, 99, 132, 0.5)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 1
                }
            ]
        }
    }


def query_resource_allocation():
    """Query for resource allocation across projects."""
    # In a real implementation, this would query the database
    resource_data = [
        {"resource": "Project Manager", "utilization": 85, "overallocation": False},
        {"resource": "Design Team", "utilization": 95, "overallocation": False},
        {"resource": "Engineers", "utilization": 110, "overallocation": True},
        {"resource": "Construction Crew A", "utilization": 100, "overallocation": False},
        {"resource": "Construction Crew B", "utilization": 120, "overallocation": True},
        {"resource": "Procurement Team", "utilization": 75, "overallocation": False},
        {"resource": "QA Team", "utilization": 50, "overallocation": False},
        {"resource": "Specialists", "utilization": 90, "overallocation": False}
    ]
    return resource_data


def create_resource_visualization(resource_data):
    """Create visualization data for resource allocation."""
    return {
        "type": "horizontalBar",
        "data": {
            "labels": [resource["resource"] for resource in resource_data],
            "datasets": [{
                "label": "Resource Utilization (%)",
                "data": [resource["utilization"] for resource in resource_data],
                "backgroundColor": [
                    "rgba(220, 53, 69, 0.7)" if resource["overallocation"] else "rgba(40, 167, 69, 0.7)"
                    for resource in resource_data
                ]
            }]
        }
    }


def query_critical_path():
    """Query for activities on the critical path."""
    # In a real implementation, this would query the database
    critical_activities = [
        {
            "project_id": "DEMO-001",
            "project_name": "Office Building Construction",
            "activity_id": "DEMO-001-ACT-001",
            "activity_name": "Project Planning & Design",
            "duration": 45,  # Days
            "float": 0,
            "status": "Completed"
        },
        {
            "project_id": "DEMO-001",
            "project_name": "Office Building Construction",
            "activity_id": "DEMO-001-ACT-002",
            "activity_name": "Procurement & Mobilization",
            "duration": 44,  # Days
            "float": 0,
            "status": "Completed"
        },
        {
            "project_id": "DEMO-001",
            "project_name": "Office Building Construction",
            "activity_id": "DEMO-001-ACT-003",
            "activity_name": "Foundation Work",
            "duration": 55,  # Days
            "float": 0,
            "status": "In Progress"
        },
        {
            "project_id": "DEMO-001",
            "project_name": "Office Building Construction",
            "activity_id": "DEMO-001-ACT-004",
            "activity_name": "Structural Framework",
            "duration": 70,  # Days
            "float": 0,
            "status": "Not Started"
        },
        {
            "project_id": "DEMO-001",
            "project_name": "Office Building Construction",
            "activity_id": "DEMO-001-ACT-006",
            "activity_name": "Interior Work & Finishes",
            "duration": 50,  # Days
            "float": 0,
            "status": "Not Started"
        },
        {
            "project_id": "DEMO-001",
            "project_name": "Office Building Construction",
            "activity_id": "DEMO-001-ACT-007",
            "activity_name": "Testing & Commissioning",
            "duration": 10,  # Days
            "float": 0,
            "status": "Not Started"
        }
    ]
    return critical_activities


def create_critical_path_visualization(critical_activities):
    """Create visualization data for critical path."""
    return {
        "type": "timeline",
        "data": {
            "activities": [
                {
                    "id": activity["activity_id"],
                    "name": activity["activity_name"],
                    "duration": activity["duration"],
                    "status": activity["status"]
                } for activity in critical_activities
            ]
        }
    }
