"""Primavera P6 API Module for CSCSC AI Agent.

Provides API endpoints for interacting with Primavera P6 data.
"""

from flask import Blueprint, jsonify, request
import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

from .primavera_connector import PrimaveraConnector
from .primavera_data_processor import PrimaveraDataProcessor
from .primavera_database import PrimaveraDatabase

# Create Blueprint for Primavera API routes
primavera_api = Blueprint('primavera_api', __name__)

# Initialize components
P6_PATH = os.environ.get('P6_INSTALLATION_PATH', r"C:\Program Files\Oracle\Primavera P6\P6 Professional\21.12.0")
connector = PrimaveraConnector()
data_processor = PrimaveraDataProcessor(connector, P6_PATH)
database = PrimaveraDatabase()

@primavera_api.route('/api/v1/primavera/status', methods=['GET'])
def get_status():
    """Get status of Primavera P6 integration."""
    try:
        connection_status = connector.connect()
        return jsonify({
            'status': 'success',
            'connection': 'active' if connection_status else 'inactive',
            'p6_path': P6_PATH,
            'p6_exists': os.path.exists(P6_PATH)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'p6_path': P6_PATH
        }), 500

@primavera_api.route('/api/v1/primavera/projects', methods=['GET'])
def get_projects():
    """Get all projects from Primavera P6."""
    try:
        # First check database
        db_projects = database.get_projects()
        
        if db_projects:
            # Use projects from database
            projects = [{
                'id': p.get('proj_id'),
                'name': p.get('proj_name'),
                'start_date': p.get('act_start_date') or p.get('target_start_date'),
                'end_date': p.get('act_end_date') or p.get('target_end_date'),
                'progress': p.get('progress', 0)
            } for p in db_projects]
            
            return jsonify({
                'status': 'success',
                'projects': projects,
                'source': 'database'
            })
        
        # If no projects in database, try to get from P6
        connector.connect()
        p6_projects = connector.get_projects()
        
        if p6_projects:
            # Store projects in database
            database.store_projects(p6_projects)
            
            # Format projects for response
            projects = [{
                'id': p.get('proj_id'),
                'name': p.get('proj_name'),
                'start_date': p.get('act_start_date') or p.get('target_start_date'),
                'end_date': p.get('act_end_date') or p.get('target_end_date'),
                'progress': 0  # Default progress
            } for p in p6_projects]
            
            return jsonify({
                'status': 'success',
                'projects': projects,
                'source': 'primavera'
            })
        
        # If no projects in P6, generate demo data
        demo_projects = generate_demo_projects()
        
        return jsonify({
            'status': 'success',
            'projects': demo_projects,
            'source': 'demo'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@primavera_api.route('/api/v1/primavera/projects/<proj_id>/details', methods=['GET'])
def get_project_details(proj_id):
    """Get detailed information for a specific project."""
    try:
        # Get project data
        project_data = data_processor.get_project_data(proj_id)
        
        if not project_data:
            # Try to generate demo data for project
            return jsonify(generate_demo_project_details(proj_id))
        
        # Process data for visualization
        visualization_data = data_processor.prepare_for_visualization(project_data)
        
        return jsonify({
            'status': 'success',
            'project_id': proj_id,
            'gantt_data': visualization_data.get('gantt_data', [])[0] if visualization_data.get('gantt_data') else None,
            'resource_data': visualization_data.get('resource_data', [])[0] if visualization_data.get('resource_data') else None,
            'progress_data': visualization_data.get('progress_data', [])[0] if visualization_data.get('progress_data') else None
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@primavera_api.route('/api/v1/primavera/query', methods=['POST'])
def query_primavera_data():
    """Query Primavera P6 data using natural language."""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Query is required'
            }), 400
        
        # Process query using simple keyword matching
        query_lower = query.lower()
        
        # Determine query intent
        if any(keyword in query_lower for keyword in ['late', 'behind', 'delay', 'overdue']):
            # Query for late activities
            result = query_late_activities()
            text_result = "Here are the activities that are behind schedule:"
            visualization = create_late_activities_visualization(result)
        elif any(keyword in query_lower for keyword in ['progress', 'status', 'completion', 'percent']):
            # Query for project progress
            result = query_project_progress()
            text_result = "Here is the current progress status of all projects:"
            visualization = create_progress_visualization(result)
        elif any(keyword in query_lower for keyword in ['resource', 'allocation', 'utilization']):
            # Query for resource allocation
            result = query_resource_allocation()
            text_result = "Here is the current resource allocation across projects:"
            visualization = create_resource_visualization(result)
        elif any(keyword in query_lower for keyword in ['critical', 'path', 'key activities']):
            # Query for critical path
            result = query_critical_path()
            text_result = "Here are the activities on the critical path:"
            visualization = create_critical_path_visualization(result)
        else:
            # Default response for unknown queries
            return jsonify({
                'status': 'success',
                'result': f"I'm not sure how to answer: '{query}'. Try asking about late activities, project progress, resource allocation, or critical path."
            })
        
        return jsonify({
            'status': 'success',
            'text_result': text_result,
            'result': result,
            'visualization': visualization
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@primavera_api.route('/api/v1/primavera/import', methods=['POST'])
def import_primavera_data():
    """Import data from Primavera P6."""
    try:
        data = request.json
        import_type = data.get('type', 'api')  # 'api', 'database', or 'file'
        source = data.get('source', '')
        
        # Connect to Primavera
        connector.connection_type = import_type
        connection_success = connector.connect()
        
        if not connection_success:
            return jsonify({
                'status': 'error',
                'message': f'Failed to connect to Primavera using {import_type} connection'
            }), 500
        
        # Import projects
        projects = connector.get_projects()
        project_count = database.store_projects(projects)
        
        # Import activities for each project
        activity_count = 0
        for project in projects:
            activities = connector.get_activities(project.get('proj_id'))
            activity_count += database.store_activities(activities)
        
        # Log import
        import_id = database.store_import_log(
            import_type=import_type,
            source=source,
            status='success',
            message=f'Imported {project_count} projects and {activity_count} activities',
            metadata={'project_count': project_count, 'activity_count': activity_count}
        )
        
        return jsonify({
            'status': 'success',
            'import_id': import_id,
            'project_count': project_count,
            'activity_count': activity_count
        })
    except Exception as e:
        # Log import error
        database.store_import_log(
            import_type=request.json.get('type', 'api'),
            source=request.json.get('source', ''),
            status='error',
            message=str(e)
        )
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Helper functions for generating demo data
def generate_demo_projects():
    """Generate demo projects when no real data is available."""
    return [
        {
            'id': 'DEMO-001',
            'name': 'Office Building Construction',
            'start_date': '2025-01-15',
            'end_date': '2025-10-30',
            'progress': 35.8
        },
        {
            'id': 'DEMO-002',
            'name': 'Highway Infrastructure Project',
            'start_date': '2024-11-10',
            'end_date': '2026-05-20',
            'progress': 15.2
        },
        {
            'id': 'DEMO-003',
            'name': 'Solar Farm Installation',
            'start_date': '2025-02-01',
            'end_date': '2025-08-15',
            'progress': 42.5
        }
    ]

def generate_demo_project_details(proj_id):
    """Generate demo project details."""
    # Find project in demo projects
    demo_projects = generate_demo_projects()
    project = next((p for p in demo_projects if p['id'] == proj_id), None)
    
    if not project:
        project = demo_projects[0]
    
    # Generate demo gantt data
    gantt_data = {
        'project_id': project['id'],
        'project_name': project['name'],
        'tasks': [
            {
                'id': f"{project['id']}-T1",
                'name': 'Project Initiation',
                'start': '2025-01-15',
                'end': '2025-02-15',
                'progress': 100,
                'dependencies': []
            },
            {
                'id': f"{project['id']}-T2",
                'name': 'Design Phase',
                'start': '2025-02-16',
                'end': '2025-04-30',
                'progress': 85,
                'dependencies': [f"{project['id']}-T1"]
            },
            {
                'id': f"{project['id']}-T3",
                'name': 'Foundation Work',
                'start': '2025-04-15',
                'end': '2025-06-30',
                'progress': 40,
                'dependencies': [f"{project['id']}-T2"]
            },
            {
                'id': f"{project['id']}-T4",
                'name': 'Construction Phase',
                'start': '2025-06-15',
                'end': '2025-09-30',
                'progress': 0,
                'dependencies': [f"{project['id']}-T3"]
            },
            {
                'id': f"{project['id']}-T5",
                'name': 'Final Inspection',
                'start': '2025-10-01',
                'end': '2025-10-30',
                'progress': 0,
                'dependencies': [f"{project['id']}-T4"]
            }
        ]
    }
    
    # Generate demo resource data
    resource_data = {
        'project_id': project['id'],
        'project_name': project['name'],
        'resources': [
            {
                'id': 'R1',
                'name': 'Engineers',
                'type': 'Labor',
                'planned_units': 450,
                'actual_units': 380
            },
            {
                'id': 'R2',
                'name': 'Construction Workers',
                'type': 'Labor',
                'planned_units': 1200,
                'actual_units': 850
            },
            {
                'id': 'R3',
                'name': 'Heavy Equipment',
                'type': 'Equipment',
                'planned_units': 300,
                'actual_units': 180
            },
            {
                'id': 'R4',
                'name': 'Building Materials',
                'type': 'Material',
                'planned_units': 800,
                'actual_units': 420
            },
            {
                'id': 'R5',
                'name': 'Project Management',
                'type': 'Labor',
                'planned_units': 180,
                'actual_units': 100
            }
        ]
    }
    
    # Generate demo progress data
    progress_data = {
        'project_id': project['id'],
        'project_name': project['name'],
        'progress_curve': [
            {'date': '2025-01-15', 'planned': 0, 'actual': 0, 'is_actual': True},
            {'date': '2025-02-15', 'planned': 10, 'actual': 8, 'is_actual': True},
            {'date': '2025-03-15', 'planned': 25, 'actual': 20, 'is_actual': True},
            {'date': '2025-04-15', 'planned': 40, 'actual': 36, 'is_actual': True},
            {'date': '2025-05-15', 'planned': 55, 'actual': 45, 'is_actual': False},
            {'date': '2025-06-15', 'planned': 70, 'actual': None, 'is_actual': False},
            {'date': '2025-07-15', 'planned': 80, 'actual': None, 'is_actual': False},
            {'date': '2025-08-15', 'planned': 90, 'actual': None, 'is_actual': False},
            {'date': '2025-09-15', 'planned': 95, 'actual': None, 'is_actual': False},
            {'date': '2025-10-30', 'planned': 100, 'actual': None, 'is_actual': False}
        ]
    }
    
    return {
        'status': 'success',
        'project_id': project['id'],
        'gantt_data': gantt_data,
        'resource_data': resource_data,
        'progress_data': progress_data,
        'source': 'demo'
    }

# Helper functions for query handling
def query_late_activities():
    """Query for late activities."""
    # In a real implementation, this would query the database
    # For demo, return synthetic data
    return [
        {
            'task_id': 'DEMO-001-T3',
            'task_name': 'Foundation Work',
            'project': 'Office Building Construction',
            'planned_end': '2025-06-30',
            'forecast_end': '2025-07-15',
            'days_late': 15,
            'impact': 'High'
        },
        {
            'task_id': 'DEMO-002-T2',
            'task_name': 'Environmental Assessment',
            'project': 'Highway Infrastructure Project',
            'planned_end': '2025-01-30',
            'forecast_end': '2025-03-10',
            'days_late': 39,
            'impact': 'Critical'
        },
        {
            'task_id': 'DEMO-003-T1',
            'task_name': 'Site Preparation',
            'project': 'Solar Farm Installation',
            'planned_end': '2025-03-15',
            'forecast_end': '2025-03-22',
            'days_late': 7,
            'impact': 'Medium'
        }
    ]

def query_project_progress():
    """Query for project progress."""
    # In a real implementation, this would query the database
    # For demo, return synthetic data
    return [
        {
            'project_id': 'DEMO-001',
            'project_name': 'Office Building Construction',
            'planned_progress': 45.0,
            'actual_progress': 35.8,
            'variance': -9.2,
            'status': 'Behind Schedule'
        },
        {
            'project_id': 'DEMO-002',
            'project_name': 'Highway Infrastructure Project',
            'planned_progress': 22.5,
            'actual_progress': 15.2,
            'variance': -7.3,
            'status': 'Behind Schedule'
        },
        {
            'project_id': 'DEMO-003',
            'project_name': 'Solar Farm Installation',
            'planned_progress': 40.0,
            'actual_progress': 42.5,
            'variance': 2.5,
            'status': 'On Schedule'
        }
    ]

def query_resource_allocation():
    """Query for resource allocation."""
    # In a real implementation, this would query the database
    # For demo, return synthetic data
    return [
        {
            'resource_name': 'Engineers',
            'resource_type': 'Labor',
            'total_planned': 900,
            'total_allocated': 750,
            'utilization': 83.3
        },
        {
            'resource_name': 'Construction Workers',
            'resource_type': 'Labor',
            'total_planned': 2500,
            'total_allocated': 1800,
            'utilization': 72.0
        },
        {
            'resource_name': 'Heavy Equipment',
            'resource_type': 'Equipment',
            'total_planned': 600,
            'total_allocated': 420,
            'utilization': 70.0
        },
        {
            'resource_name': 'Building Materials',
            'resource_type': 'Material',
            'total_planned': 1500,
            'total_allocated': 900,
            'utilization': 60.0
        },
        {
            'resource_name': 'Project Management',
            'resource_type': 'Labor',
            'total_planned': 450,
            'total_allocated': 380,
            'utilization': 84.4
        }
    ]

def query_critical_path():
    """Query for critical path activities."""
    # In a real implementation, this would query the database
    # For demo, return synthetic data
    return [
        {
            'task_id': 'DEMO-001-T1',
            'task_name': 'Project Initiation',
            'project': 'Office Building Construction',
            'start_date': '2025-01-15',
            'end_date': '2025-02-15',
            'float': 0,
            'complete': True
        },
        {
            'task_id': 'DEMO-001-T2',
            'task_name': 'Design Phase',
            'project': 'Office Building Construction',
            'start_date': '2025-02-16',
            'end_date': '2025-04-30',
            'float': 0,
            'complete': False
        },
        {
            'task_id': 'DEMO-001-T3',
            'task_name': 'Foundation Work',
            'project': 'Office Building Construction',
            'start_date': '2025-04-15',
            'end_date': '2025-06-30',
            'float': 0,
            'complete': False
        },
        {
            'task_id': 'DEMO-001-T4',
            'task_name': 'Construction Phase',
            'project': 'Office Building Construction',
            'start_date': '2025-06-15',
            'end_date': '2025-09-30',
            'float': 0,
            'complete': False
        },
        {
            'task_id': 'DEMO-001-T5',
            'task_name': 'Final Inspection',
            'project': 'Office Building Construction',
            'start_date': '2025-10-01',
            'end_date': '2025-10-30',
            'float': 0,
            'complete': False
        }
    ]

# Helper functions for creating visualizations
def create_late_activities_visualization(data):
    """Create visualization for late activities."""
    return {
        'type': 'bar',
        'data': {
            'labels': [item['task_name'] for item in data],
            'datasets': [{
                'label': 'Days Late',
                'data': [item['days_late'] for item in data],
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(255, 99, 132, 0.7)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                'borderWidth': 1
            }]
        },
        'options': {
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'title': {
                        'display': True,
                        'text': 'Days Behind Schedule'
                    }
                },
                'x': {
                    'title': {
                        'display': True,
                        'text': 'Activities'
                    }
                }
            },
            'plugins': {
                'title': {
                    'display': True,
                    'text': 'Late Activities'
                }
            }
        }
    }

def create_progress_visualization(data):
    """Create visualization for project progress."""
    return {
        'type': 'bar',
        'data': {
            'labels': [item['project_name'] for item in data],
            'datasets': [
                {
                    'label': 'Planned Progress',
                    'data': [item['planned_progress'] for item in data],
                    'backgroundColor': 'rgba(54, 162, 235, 0.7)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Actual Progress',
                    'data': [item['actual_progress'] for item in data],
                    'backgroundColor': 'rgba(75, 192, 192, 0.7)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                }
            ]
        },
        'options': {
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'max': 100,
                    'title': {
                        'display': True,
                        'text': 'Progress (%)'
                    }
                },
                'x': {
                    'title': {
                        'display': True,
                        'text': 'Projects'
                    }
                }
            },
            'plugins': {
                'title': {
                    'display': True,
                    'text': 'Project Progress'
                }
            }
        }
    }

def create_resource_visualization(data):
    """Create visualization for resource allocation."""
    return {
        'type': 'bar',
        'data': {
            'labels': [item['resource_name'] for item in data],
            'datasets': [{
                'label': 'Utilization (%)',
                'data': [item['utilization'] for item in data],
                'backgroundColor': [
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(54, 162, 235, 0.7)'
                ],
                'borderColor': [
                    'rgba(54, 162, 235, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(54, 162, 235, 1)'
                ],
                'borderWidth': 1
            }]
        },
        'options': {
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'max': 100,
                    'title': {
                        'display': True,
                        'text': 'Utilization (%)'
                    }
                },
                'x': {
                    'title': {
                        'display': True,
                        'text': 'Resources'
                    }
                }
            },
            'plugins': {
                'title': {
                    'display': True,
                    'text': 'Resource Utilization'
                }
            }
        }
    }

def create_critical_path_visualization(data):
    """Create visualization for critical path."""
    # For critical path, a timeline visualization would be better
    # But for simplicity, use a bar chart showing duration
    durations = []
    for item in data:
        start_date = datetime.strptime(item['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(item['end_date'], '%Y-%m-%d')
        duration = (end_date - start_date).days
        durations.append(duration)
    
    return {
        'type': 'bar',
        'data': {
            'labels': [item['task_name'] for item in data],
            'datasets': [{
                'label': 'Duration (days)',
                'data': durations,
                'backgroundColor': [
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(255, 159, 64, 0.7)'
                ],
                'borderColor': [
                    'rgba(255, 159, 64, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                'borderWidth': 1
            }]
        },
        'options': {
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'title': {
                        'display': True,
                        'text': 'Duration (days)'
                    }
                },
                'x': {
                    'title': {
                        'display': True,
                        'text': 'Critical Path Activities'
                    }
                }
            },
            'plugins': {
                'title': {
                    'display': True,
                    'text': 'Critical Path Duration'
                }
            }
        }
    }
