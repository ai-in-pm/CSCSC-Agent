from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional

from src.models.schemas import UserQuery, AgentResponse, Task, ProjectData, EVMMetrics, Forecast
from src.config.settings import settings
from src.user_interface.nlp_processor import NLPProcessor
from src.evm_engine.calculator import EVMCalculator
from src.ai_ml_analysis.analyzer import EVMAnalyzer
from src.nlg_engine.generator import NLGGenerator

# Create API router
router = APIRouter(prefix=settings.API_PREFIX)

# Initialize components
nlp_processor = NLPProcessor()
evm_calculator = EVMCalculator()
evm_analyzer = EVMAnalyzer(evm_calculator)
nlg_generator = NLGGenerator()


@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(query: UserQuery):
    """Chat with the EVM AI agent using natural language."""
    # Process the user query
    intent, entities = nlp_processor.process_query(query.query)
    
    # Prepare the response based on intent
    if intent == "status_request":
        # Get project status data (in a real implementation this would query a database)
        project_id = entities.get("project_id")
        if not project_id:
            return AgentResponse(
                response="Please specify which project you'd like information about.",
                confidence=0.8
            )
            
        # This is simplified - would actually query for real data
        metrics = _get_mock_metrics(project_id)
        
        # Generate natural language status update
        status_text = nlg_generator.generate_status_update(metrics)
        
        return AgentResponse(
            response=status_text,
            data={"metrics": metrics.dict()},
            confidence=0.9
        )
        
    elif intent == "forecast_request":
        project_id = entities.get("project_id")
        if not project_id:
            return AgentResponse(
                response="Please specify which project you'd like a forecast for.",
                confidence=0.8
            )
            
        # Get mock forecast data
        forecast = _get_mock_forecast(project_id)
        
        # Generate forecast commentary
        from datetime import datetime, timedelta
        commentary = nlg_generator.generate_forecast_commentary(
            forecast,
            datetime.now() + timedelta(days=90),  # Mock baseline finish
            100000.0  # Mock BAC
        )
        
        return AgentResponse(
            response=commentary,
            data={"forecast": forecast.dict()},
            confidence=0.85
        )
        
    elif intent == "variance_explanation":
        task_id = entities.get("task_id")
        variance_type = entities.get("variance_type", "cost")
        
        if not task_id:
            return AgentResponse(
                response="Please specify which task you'd like me to explain the variance for.",
                confidence=0.8
            )
            
        # Get mock variance explanation
        metrics = _get_mock_metrics(task_id)
        explanation = evm_analyzer.analyze_variance(metrics)
        
        explanation_text = nlg_generator.generate_variance_explanation(explanation)
        
        return AgentResponse(
            response=explanation_text,
            data={"explanation": explanation.dict()},
            confidence=0.9
        )
        
    elif intent == "recommendation_request":
        project_id = entities.get("project_id")
        
        if not project_id:
            return AgentResponse(
                response="Please specify which project you'd like recommendations for.",
                confidence=0.8
            )
            
        # Get mock data
        metrics = _get_mock_metrics(project_id)
        explanation = evm_analyzer.analyze_variance(metrics)
        
        recommendations = nlg_generator.generate_recommendations(metrics, explanation)
        
        return AgentResponse(
            response=recommendations,
            data={"metrics": metrics.dict()},
            confidence=0.85
        )
        
    else:
        # Generic response for unrecognized intents
        return AgentResponse(
            response="I'm not sure I understand. You can ask me about project status, forecasts, variance explanations, or recommendations.",
            confidence=0.6
        )


@router.get("/projects", response_model=List[ProjectData])
async def get_projects():
    """Get a list of all projects."""
    # In a real implementation, this would query the database
    return [_get_mock_project()]


@router.get("/projects/{project_id}", response_model=ProjectData)
async def get_project(project_id: str):
    """Get details for a specific project."""
    # In a real implementation, this would query the database
    return _get_mock_project(project_id)


@router.get("/projects/{project_id}/metrics", response_model=Dict[str, EVMMetrics])
async def get_project_metrics(project_id: str):
    """Get EVM metrics for a specific project."""
    # In a real implementation, this would query metrics from a database
    return {"project": _get_mock_metrics(project_id)}


@router.get("/projects/{project_id}/forecast", response_model=Forecast)
async def get_project_forecast(project_id: str):
    """Get forecast for a specific project."""
    # In a real implementation, this would query the forecast from a database or calculate it
    return _get_mock_forecast(project_id)


@router.get("/tasks/{task_id}/metrics", response_model=EVMMetrics)
async def get_task_metrics(task_id: str):
    """Get EVM metrics for a specific task."""
    # In a real implementation, this would query metrics from a database
    return _get_mock_metrics(task_id)


# Helper functions for mock data (in a real implementation, these would be database queries)
def _get_mock_project(project_id: str = "P001") -> ProjectData:
    """Generate mock project data for demonstration purposes."""
    from datetime import datetime, timedelta
    
    return ProjectData(
        id=project_id,
        name="Sample Construction Project",
        description="A demonstration project for the EVM AI Agent",
        start_date=datetime.now() - timedelta(days=30),
        planned_finish_date=datetime.now() + timedelta(days=90),
        budget_at_completion=100000.0,
        tasks=[
            Task(
                id="T001",
                name="Foundation Work",
                wbs_element="1.1",
                control_account="CA001",
                responsible_person="John Engineer",
                planned_start_date=datetime.now() - timedelta(days=30),
                planned_finish_date=datetime.now() - timedelta(days=10),
                actual_start_date=datetime.now() - timedelta(days=32),
                actual_finish_date=datetime.now() - timedelta(days=8),
                budget_at_completion=20000.0,
                status="completed",
                percent_complete=1.0
            ),
            Task(
                id="T002",
                name="Framing",
                wbs_element="1.2",
                control_account="CA001",
                responsible_person="Sarah Builder",
                planned_start_date=datetime.now() - timedelta(days=15),
                planned_finish_date=datetime.now() + timedelta(days=15),
                actual_start_date=datetime.now() - timedelta(days=12),
                budget_at_completion=30000.0,
                status="in_progress",
                percent_complete=0.4
            ),
            Task(
                id="T003",
                name="Electrical Work",
                wbs_element="1.3",
                control_account="CA002",
                responsible_person="Mike Electrician",
                planned_start_date=datetime.now() + timedelta(days=10),
                planned_finish_date=datetime.now() + timedelta(days=30),
                budget_at_completion=25000.0,
                status="not_started",
                percent_complete=0.0
            ),
            Task(
                id="T004",
                name="Plumbing",
                wbs_element="1.4",
                control_account="CA002",
                responsible_person="Lisa Plumber",
                planned_start_date=datetime.now() + timedelta(days=10),
                planned_finish_date=datetime.now() + timedelta(days=25),
                budget_at_completion=15000.0,
                status="not_started",
                percent_complete=0.0
            ),
            Task(
                id="T005",
                name="Finishing Work",
                wbs_element="1.5",
                control_account="CA003",
                responsible_person="David Finisher",
                planned_start_date=datetime.now() + timedelta(days=30),
                planned_finish_date=datetime.now() + timedelta(days=60),
                budget_at_completion=10000.0,
                status="not_started",
                percent_complete=0.0
            )
        ]
    )


def _get_mock_metrics(entity_id: str) -> EVMMetrics:
    """Generate mock EVM metrics for demonstration purposes."""
    from datetime import datetime
    
    # Simulate slightly different metrics based on the ID
    id_num = int(entity_id[-3:]) % 3
    
    if id_num == 0:  # On track
        return EVMMetrics(
            task_id=entity_id,
            date=datetime.now(),
            bcws=50000.0,
            bcwp=51000.0,
            acwp=49500.0,
            bac=100000.0,
            eac=97000.0,
            etc=47500.0,
            cv=1500.0,
            sv=1000.0,
            cpi=1.03,
            spi=1.02,
            tcpi=0.97,
            vac=3000.0
        )
    elif id_num == 1:  # Cost issues
        return EVMMetrics(
            task_id=entity_id,
            date=datetime.now(),
            bcws=50000.0,
            bcwp=51000.0,
            acwp=60000.0,
            bac=100000.0,
            eac=118000.0,
            etc=58000.0,
            cv=-9000.0,
            sv=1000.0,
            cpi=0.85,
            spi=1.02,
            tcpi=1.23,
            vac=-18000.0
        )
    else:  # Schedule issues
        return EVMMetrics(
            task_id=entity_id,
            date=datetime.now(),
            bcws=50000.0,
            bcwp=40000.0,
            acwp=39000.0,
            bac=100000.0,
            eac=97500.0,
            etc=58500.0,
            cv=1000.0,
            sv=-10000.0,
            cpi=1.025,
            spi=0.8,
            tcpi=0.97,
            vac=2500.0
        )


def _get_mock_forecast(project_id: str) -> Forecast:
    """Generate mock forecast data for demonstration purposes."""
    from datetime import datetime, timedelta
    
    # Simulate different forecasts based on the ID
    id_num = int(project_id[-3:]) % 3
    
    if id_num == 0:  # On track
        return Forecast(
            project_id=project_id,
            date=datetime.now(),
            eac=98000.0,
            etc=48000.0,
            estimated_finish_date=datetime.now() + timedelta(days=88),  # Slightly early
            probability=0.8,
            methodology="CPI-based",
            key_factors=["Good cost performance", "Consistent schedule performance"]
        )
    elif id_num == 1:  # Cost overrun
        return Forecast(
            project_id=project_id,
            date=datetime.now(),
            eac=118000.0,
            etc=58000.0,
            estimated_finish_date=datetime.now() + timedelta(days=92),  # Slightly late
            probability=0.7,
            methodology="CPI*SPI",
            key_factors=["Material cost increases", "Labor productivity lower than expected"]
        )
    else:  # Schedule delay
        return Forecast(
            project_id=project_id,
            date=datetime.now(),
            eac=97000.0,
            etc=57000.0,
            estimated_finish_date=datetime.now() + timedelta(days=110),  # Significantly late
            probability=0.65,
            methodology="earned-schedule",
            key_factors=["Resource availability issues", "Delayed approvals"]
        )
