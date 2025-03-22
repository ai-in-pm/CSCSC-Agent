from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body
from typing import Dict, List, Any, Optional
import os
import json
from datetime import datetime
import logging

from src.crewai_integration.cscsc_crew import CSCSCAgentCrew
from src.utils.helpers import _convert_dates_to_iso
from src.config.settings import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/crewai",
    tags=["crewai"],
    responses={404: {"description": "Not found"}},
)

# Initialize CrewAI agents
_crew_instance = None

def get_crew_instance():
    """Get or create a CrewAI instance."""
    global _crew_instance
    if _crew_instance is None:
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            logger.warning("No OpenAI API key found in environment variables")
        _crew_instance = CSCSCAgentCrew(openai_api_key=openai_api_key)
    return _crew_instance


@router.post("/environmental-impact", response_model=Dict[str, Any])
async def analyze_environmental_impact(
    project_data: Dict[str, Any] = Body(...),
    background_tasks: BackgroundTasks = None,
    crew: CSCSCAgentCrew = Depends(get_crew_instance),
):
    """Analyze environmental impacts using CrewAI agents."""
    try:
        # For synchronous execution
        if background_tasks is None:
            result = crew.analyze_environmental_impact(project_data)
            return {"status": "success", "result": result}
        
        # For asynchronous execution (not implemented yet)
        # Would use background_tasks.add_task(crew.analyze_environmental_impact, project_data)
        # and return a job ID for status polling
        raise HTTPException(status_code=501, detail="Asynchronous execution not implemented yet")
    
    except Exception as e:
        logger.error(f"Error in environmental impact analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/supply-chain-impact", response_model=Dict[str, Any])
async def analyze_supply_chain_impact(
    project_data: Dict[str, Any] = Body(...),
    background_tasks: BackgroundTasks = None,
    crew: CSCSCAgentCrew = Depends(get_crew_instance),
):
    """Analyze supply chain impacts using CrewAI agents."""
    try:
        # For synchronous execution
        if background_tasks is None:
            result = crew.analyze_supply_chain_impact(project_data)
            return {"status": "success", "result": result}
        
        # For asynchronous execution (not implemented yet)
        raise HTTPException(status_code=501, detail="Asynchronous execution not implemented yet")
    
    except Exception as e:
        logger.error(f"Error in supply chain impact analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/site-progress-verification", response_model=Dict[str, Any])
async def verify_site_progress(
    project_data: Dict[str, Any] = Body(...),
    background_tasks: BackgroundTasks = None,
    crew: CSCSCAgentCrew = Depends(get_crew_instance),
):
    """Verify site progress using CrewAI agents."""
    try:
        # For synchronous execution
        if background_tasks is None:
            result = crew.verify_site_progress(project_data)
            return {"status": "success", "result": result}
        
        # For asynchronous execution (not implemented yet)
        raise HTTPException(status_code=501, detail="Asynchronous execution not implemented yet")
    
    except Exception as e:
        logger.error(f"Error in site progress verification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.post("/risk-assessment", response_model=Dict[str, Any])
async def assess_project_risks(
    project_data: Dict[str, Any] = Body(...),
    background_tasks: BackgroundTasks = None,
    crew: CSCSCAgentCrew = Depends(get_crew_instance),
):
    """Assess project risks using CrewAI agents."""
    try:
        # For synchronous execution
        if background_tasks is None:
            result = crew.assess_project_risks(project_data)
            return {"status": "success", "result": result}
        
        # For asynchronous execution (not implemented yet)
        raise HTTPException(status_code=501, detail="Asynchronous execution not implemented yet")
    
    except Exception as e:
        logger.error(f"Error in risk assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")
