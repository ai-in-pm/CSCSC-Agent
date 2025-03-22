from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel

from src.models.physical_schemas import (
    EnvironmentalFactor,
    SiteObservation,
    SupplyChainIssue,
    ResourceAllocation,
    SiteCondition,
    RiskAssessment,
    PhysicalProgressMetrics
)
from src.evm_engine.physical_ai_assistant import PhysicalEVMAssistant
from src.evm_engine.calculator import EVMCalculator
from src.nlg_engine.generator import NLGGenerator
from src.data_ingestion.database import Database

router = APIRouter(prefix="/api/v1/physical", tags=["Physical EVM"])

# Dependencies
def get_physical_ai_assistant():
    """Dependency to get the Physical EVM Assistant instance."""
    evm_calculator = EVMCalculator()
    return PhysicalEVMAssistant(evm_calculator)


def get_nlg_generator():
    """Dependency to get the NLG Generator instance."""
    return NLGGenerator()


def get_db():
    """Dependency to get the database connection."""
    return Database()


# Request/Response Models
class EnvironmentalAnalysisRequest(BaseModel):
    project_id: str
    environmental_factors: List[EnvironmentalFactor]


class SupplyChainAnalysisRequest(BaseModel):
    project_id: str
    delayed_materials: List[Dict[str, Any]]


class SiteProgressAdjustmentRequest(BaseModel):
    task_id: str
    site_observations: List[Dict[str, Any]]


class SiteConditionRequest(BaseModel):
    project_id: str
    site_conditions: Dict[str, Any]


# API Endpoints
@router.post("/environmental-impact", summary="Analyze environmental impact on project performance")
async def analyze_environmental_impact(
    request: EnvironmentalAnalysisRequest,
    physical_ai: PhysicalEVMAssistant = Depends(get_physical_ai_assistant),
    nlg: NLGGenerator = Depends(get_nlg_generator)
):
    """Analyze the impact of environmental factors on project performance.
    
    This endpoint takes a list of environmental factors (weather, site conditions, etc.)
    and analyzes their impact on project schedule, cost, and affected work elements.
    It provides both quantitative analysis and natural language explanation.
    """
    # Perform technical analysis
    impact_analysis = physical_ai.analyze_environmental_impact(
        request.project_id,
        request.environmental_factors
    )
    
    # Generate natural language explanation
    explanation = nlg.generate_environmental_impact_explanation(
        request.project_id,
        impact_analysis
    )
    
    # Return combined results
    return {
        "analysis": impact_analysis,
        "explanation": explanation
    }


@router.post("/supply-chain-impact", summary="Analyze supply chain impact on project")
async def analyze_supply_chain_impact(
    request: SupplyChainAnalysisRequest,
    physical_ai: PhysicalEVMAssistant = Depends(get_physical_ai_assistant),
    nlg: NLGGenerator = Depends(get_nlg_generator)
):
    """Analyze the impact of supply chain delays on project performance.
    
    This endpoint evaluates material delays and their impact on project schedule,
    critical path, and affected tasks. It provides mitigation strategies and natural
    language explanation.
    """
    # Perform technical analysis
    impact_analysis = physical_ai.analyze_supply_chain_impact(
        request.project_id,
        request.delayed_materials
    )
    
    # Generate natural language explanation
    explanation = nlg.generate_supply_chain_impact_explanation(
        request.project_id,
        impact_analysis
    )
    
    # Return combined results
    return {
        "analysis": impact_analysis,
        "explanation": explanation
    }


@router.post("/site-progress-adjustment", summary="Generate site progress adjustment based on observations")
async def generate_site_progress_adjustment(
    request: SiteProgressAdjustmentRequest,
    physical_ai: PhysicalEVMAssistant = Depends(get_physical_ai_assistant),
    nlg: NLGGenerator = Depends(get_nlg_generator)
):
    """Generate EVM metric adjustments based on on-site observations.
    
    This endpoint takes a list of on-site observations and generates suggested
    adjustments to percent complete and actual costs, with justification.
    """
    # Generate adjustment recommendations
    adjustment = physical_ai.generate_site_progress_adjustment(
        request.task_id,
        request.site_observations
    )
    
    # Generate natural language explanation
    explanation = nlg.generate_site_adjustment_explanation(
        request.task_id,
        adjustment
    )
    
    # Return combined results
    return {
        "adjustment": adjustment,
        "explanation": explanation
    }


@router.post("/at-risk-wbs-elements", summary="Identify WBS elements at risk based on site conditions")
async def identify_at_risk_wbs_elements(
    request: SiteConditionRequest,
    physical_ai: PhysicalEVMAssistant = Depends(get_physical_ai_assistant),
    nlg: NLGGenerator = Depends(get_nlg_generator)
):
    """Identify WBS elements at risk based on current site conditions.
    
    This endpoint analyzes current site conditions (weather, labor, equipment, materials)
    and identifies which WBS elements are at risk, along with risk levels and reasons.
    """
    # Identify at-risk elements
    at_risk_elements = physical_ai.identify_at_risk_wbs_elements(
        request.project_id,
        request.site_conditions
    )
    
    # Generate natural language explanation
    explanation = nlg.generate_risk_assessment_explanation(
        request.project_id,
        at_risk_elements
    )
    
    # Return combined results
    return {
        "at_risk_elements": at_risk_elements,
        "explanation": explanation
    }


@router.post("/site-observations", summary="Record site observations and their EVM implications")
async def record_site_observation(
    observation: SiteObservation,
    db: Database = Depends(get_db)
):
    """Record a site observation and its implications for EVM metrics.
    
    This endpoint stores site observations from field personnel, including progress assessments,
    quality observations, and potential cost/schedule implications.
    """
    # In a real implementation, this would store the observation in the database
    # For now, we'll just return a simulated response
    return {
        "status": "success",
        "message": "Observation recorded successfully",
        "observation_id": observation.id
    }


@router.get("/resource-productivity/{project_id}", summary="Get resource productivity analysis")
async def get_resource_productivity(
    project_id: str,
    date_from: Optional[datetime] = Query(None, description="Start date for analysis"),
    date_to: Optional[datetime] = Query(None, description="End date for analysis")
):
    """Get productivity analysis for resources on a physical project.
    
    This endpoint analyzes resource productivity over time, comparing planned vs.
    actual utilization and identifying productivity trends and issues.
    """
    # In a real implementation, this would query the database and perform productivity analysis
    # For now, we'll return a simulated response
    return {
        "project_id": project_id,
        "analysis_period": {
            "from": date_from or datetime.now(),
            "to": date_to or datetime.now()
        },
        "resources": [
            {
                "resource_type": "labor",
                "resource_name": "Concrete crew",
                "planned_productivity": 15.0,  # units per day
                "actual_productivity": 13.2,   # units per day
                "productivity_index": 0.88,    # actual / planned
                "trend": "declining",
                "contributing_factors": ["Weather delays", "Material quality issues"]
            },
            {
                "resource_type": "equipment",
                "resource_name": "Excavator",
                "planned_productivity": 45.0,  # cubic yards per day
                "actual_productivity": 42.3,   # cubic yards per day
                "productivity_index": 0.94,    # actual / planned
                "trend": "stable",
                "contributing_factors": ["Operator experience"]
            }
        ],
        "summary": "Overall resource productivity is 6% below plan, primarily due to weather impacts on concrete work."
    }


@router.get("/physical-vs-reported/{project_id}", summary="Compare physical vs. reported progress")
async def compare_physical_vs_reported(
    project_id: str,
    wbs_element: Optional[str] = Query(None, description="Specific WBS element to analyze")
):
    """Compare physically observed progress versus reported progress.
    
    This endpoint provides analysis of the gap between physical observations
    and reported progress, helping to identify potential reporting issues.
    """
    # In a real implementation, this would query the database and perform analysis
    # For now, we'll return a simulated response
    return {
        "project_id": project_id,
        "wbs_element": wbs_element or "All",
        "analysis_date": datetime.now(),
        "overall_physical_progress": 0.42,  # 42% complete
        "overall_reported_progress": 0.45,  # 45% complete
        "variance": -0.03,  # physical - reported
        "variance_percentage": -6.67,  # (physical - reported) / reported * 100
        "variance_classification": "minor overreporting",
        "elements_with_significant_variance": [
            {
                "wbs_element": "1.3.2",
                "element_name": "Structural Steel",
                "physical_progress": 0.35,
                "reported_progress": 0.45,
                "variance": -0.10,
                "explanation": "Delays in steel delivery not reflected in reports"
            },
            {
                "wbs_element": "1.4.1",
                "element_name": "Electrical Rough-In",
                "physical_progress": 0.20,
                "reported_progress": 0.30,
                "variance": -0.10,
                "explanation": "Quality issues requiring rework not captured in reports"
            }
        ],
        "recommendation": "Review progress reporting procedures for Structural Steel and Electrical work. Consider site verification of progress reports for these elements."
    }


@router.get("/environmental-scan/{project_id}", summary="Get environmental scan of project site")
async def get_environmental_scan(
    project_id: str
):
    """Get current environmental scan of the project site.
    
    This endpoint provides an overview of current environmental conditions
    affecting the project site, including weather forecasts, site access issues,
    and other physical factors that may impact project performance.
    """
    # In a real implementation, this would query external APIs and IoT sensors
    # For now, we'll return a simulated response
    return {
        "project_id": project_id,
        "scan_date": datetime.now(),
        "weather": {
            "current": {
                "temperature": 72.5,  # °F
                "conditions": "Partly cloudy",
                "precipitation": 0.0,  # inches
                "wind_speed": 8.5,  # mph
                "humidity": 65  # %
            },
            "forecast": [
                {
                    "date": datetime.now(),
                    "conditions": "Partly cloudy",
                    "high_temp": 75.0,
                    "low_temp": 62.0,
                    "precipitation_chance": 20,
                    "work_impact": "low"
                },
                {
                    "date": datetime.now(),
                    "conditions": "Rain",
                    "high_temp": 68.0,
                    "low_temp": 59.0,
                    "precipitation_chance": 80,
                    "precipitation_amount": 0.5,
                    "work_impact": "high"
                }
            ],
            "weather_alerts": ["Rain expected tomorrow, may impact exterior work"]
        },
        "site_access": {
            "status": "normal",
            "restrictions": [],
            "delivery_access": "clear"
        },
        "site_conditions": {
            "ground_conditions": "dry",
            "hazards": [],
            "safety_concerns": []
        },
        "iot_sensors": {
            "moisture_sensors": [
                {"location": "North foundation", "reading": 15, "unit": "%", "status": "normal"},
                {"location": "South foundation", "reading": 22, "unit": "%", "status": "warning"}
            ],
            "temperature_sensors": [
                {"location": "Concrete curing area", "reading": 68.5, "unit": "°F", "status": "normal"}
            ]
        },
        "recommendations": [
            "Schedule indoor work for tomorrow due to expected rain",
            "Investigate elevated moisture readings in South foundation"
        ]
    }
