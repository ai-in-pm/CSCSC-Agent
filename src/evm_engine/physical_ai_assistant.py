from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import os
import json
from pathlib import Path
import logging

from src.models.schemas import Task, ProjectData, EVMMetrics, Forecast, EnvironmentalFactor
from src.config.settings import settings
from src.evm_engine.calculator import EVMCalculator

logger = logging.getLogger(__name__)

class PhysicalEVMAssistant:
    """Physical AI Assistant for real-world EVM project applications.
    
    This class provides functionality to integrate physical project data with EVM analysis,
    incorporating real-world factors like environmental conditions, supply chain status,
    and on-site observations into the earned value management process.
    """
    
    def __init__(self, evm_calculator: EVMCalculator):
        """Initialize the Physical EVM Assistant.
        
        Args:
            evm_calculator: Instance of the EVMCalculator for performing EVM calculations
        """
        self.evm_calculator = evm_calculator
        
    def analyze_environmental_impact(self, project_id: str, environmental_factors: List[EnvironmentalFactor]) -> Dict[str, Any]:
        """Analyze the impact of environmental factors on project performance.
        
        Args:
            project_id: ID of the project to analyze
            environmental_factors: List of environmental factors (weather, site conditions, etc.)
            
        Returns:
            Dict containing impact analysis on schedule, cost, and recommendations
        """
        logger.info(f"Analyzing environmental impact for project {project_id} with {len(environmental_factors)} factors")
        
        # This would be a more complex model in production
        impact_analysis = {
            "project_id": project_id,
            "analysis_date": datetime.now(),
            "schedule_impact": {},
            "cost_impact": {},
            "affected_wbs_elements": [],
            "recommendations": []
        }
        
        total_schedule_impact_days = 0
        total_cost_impact = 0.0
        affected_wbs = set()
        
        for factor in environmental_factors:
            # Calculate schedule impact based on factor type and severity
            schedule_days = self._calculate_schedule_impact(factor)
            total_schedule_impact_days += schedule_days
            
            # Calculate cost impact
            cost_impact = self._calculate_cost_impact(factor)
            total_cost_impact += cost_impact
            
            # Identify affected WBS elements
            if factor.affected_wbs_elements:
                for wbs in factor.affected_wbs_elements:
                    affected_wbs.add(wbs)
            
            # Generate specific recommendation for this factor
            recommendation = self._generate_recommendation(factor)
            if recommendation:
                impact_analysis["recommendations"].append(recommendation)
        
        # Update the impact analysis results
        impact_analysis["schedule_impact"] = {
            "total_days": total_schedule_impact_days,
            "impact_level": self._get_impact_level(total_schedule_impact_days),
            "description": self._generate_schedule_impact_description(total_schedule_impact_days)
        }
        
        impact_analysis["cost_impact"] = {
            "total_amount": total_cost_impact,
            "impact_level": self._get_impact_level(total_cost_impact / 10000), # Normalize by project size
            "description": self._generate_cost_impact_description(total_cost_impact)
        }
        
        impact_analysis["affected_wbs_elements"] = list(affected_wbs)
        
        return impact_analysis
    
    def analyze_supply_chain_impact(self, project_id: str, delayed_materials: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the impact of supply chain delays on project performance.
        
        Args:
            project_id: ID of the project to analyze
            delayed_materials: List of delayed materials with their details
            
        Returns:
            Dict containing impact analysis on schedule, cost, and critical path
        """
        logger.info(f"Analyzing supply chain impact for project {project_id} with {len(delayed_materials)} delayed materials")
        
        impact_analysis = {
            "project_id": project_id,
            "analysis_date": datetime.now(),
            "critical_path_impact": False,
            "schedule_delay_days": 0,
            "affected_tasks": [],
            "mitigation_strategies": [],
        }
        
        max_delay_days = 0
        critical_path_affected = False
        affected_tasks = set()
        
        for material in delayed_materials:
            delay_days = material.get("delay_days", 0)
            critical = material.get("on_critical_path", False)
            dependent_tasks = material.get("dependent_tasks", [])
            
            # Track maximum delay for critical path items
            if critical and delay_days > max_delay_days:
                max_delay_days = delay_days
                critical_path_affected = True
            
            # Add all dependent tasks to our affected list
            for task_id in dependent_tasks:
                affected_tasks.add(task_id)
            
            # Generate mitigation strategy
            strategy = self._generate_supply_chain_mitigation(material)
            if strategy:
                impact_analysis["mitigation_strategies"].append(strategy)
        
        # Update the impact analysis results
        impact_analysis["critical_path_impact"] = critical_path_affected
        impact_analysis["schedule_delay_days"] = max_delay_days
        impact_analysis["affected_tasks"] = list(affected_tasks)
        
        return impact_analysis
    
    def generate_site_progress_adjustment(self, task_id: str, site_observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate EVM metric adjustments based on on-site observations.
        
        Args:
            task_id: ID of the task to adjust
            site_observations: List of on-site observations with their details
            
        Returns:
            Dict containing suggested adjustments to percent complete and actual costs
        """
        logger.info(f"Generating site progress adjustment for task {task_id} with {len(site_observations)} observations")
        
        adjustment = {
            "task_id": task_id,
            "analysis_date": datetime.now(),
            "percent_complete_adjustment": 0.0,
            "actual_cost_adjustment": 0.0,
            "confidence_level": "medium",
            "justification": ""
        }
        
        # Analyze site observations to determine adjustments
        percent_adjustments = []
        cost_adjustments = []
        justifications = []
        
        for observation in site_observations:
            # Extract data from the observation
            observed_progress = observation.get("observed_progress", 0.0)
            reported_progress = observation.get("reported_progress", 0.0)
            cost_implication = observation.get("cost_implication", 0.0)
            observation_note = observation.get("notes", "")
            
            # Calculate adjustments
            if observed_progress != reported_progress:
                progress_diff = observed_progress - reported_progress
                percent_adjustments.append(progress_diff)
                justifications.append(f"Observed progress ({observed_progress:.1%}) differs from reported ({reported_progress:.1%})")
            
            if cost_implication != 0:
                cost_adjustments.append(cost_implication)
                justifications.append(f"Additional cost of ${cost_implication:.2f} identified: {observation_note}")
        
        # Calculate the final adjustments (average of all observations)
        if percent_adjustments:
            adjustment["percent_complete_adjustment"] = sum(percent_adjustments) / len(percent_adjustments)
        
        if cost_adjustments:
            adjustment["actual_cost_adjustment"] = sum(cost_adjustments)
        
        # Determine confidence level based on number and consistency of observations
        if len(site_observations) > 5:
            adjustment["confidence_level"] = "high"
        elif len(site_observations) < 2:
            adjustment["confidence_level"] = "low"
            
        # Compile justification text
        if justifications:
            adjustment["justification"] = ". ".join(justifications)
            
        return adjustment
    
    def identify_at_risk_wbs_elements(self, project_id: str, site_conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify WBS elements at risk based on current site conditions.
        
        Args:
            project_id: ID of the project to analyze
            site_conditions: Dict containing information about current site conditions
            
        Returns:
            List of at-risk WBS elements with risk levels and reasons
        """
        logger.info(f"Identifying at-risk WBS elements for project {project_id} based on site conditions")
        
        # This would integrate with a more robust risk assessment model in production
        at_risk_elements = []
        
        # Example site conditions that could be analyzed:
        # - Weather forecasts
        # - Labor availability
        # - Equipment status
        # - Material deliveries
        # - Regulatory inspections
        
        weather_conditions = site_conditions.get("weather", {})
        labor_status = site_conditions.get("labor", {})
        equipment_status = site_conditions.get("equipment", {})
        material_status = site_conditions.get("materials", {})
        
        # Check weather-related risks
        if weather_conditions.get("severe_weather_warning", False):
            # Identify outdoor activities that would be affected
            at_risk_elements.append({
                "wbs_element": "1.3.2",  # Example WBS for exterior work
                "risk_level": "high",
                "risk_factor": "weather",
                "description": f"Severe weather warning: {weather_conditions.get('warning_details', '')}",
                "recommended_action": "Consider rescheduling exterior work and securing the site"
            })
        
        # Check labor-related risks
        if labor_status.get("shortage", False):
            affected_trades = labor_status.get("affected_trades", [])
            for trade in affected_trades:
                at_risk_elements.append({
                    "wbs_element": trade.get("wbs_element", ""),
                    "risk_level": "medium",
                    "risk_factor": "labor",
                    "description": f"Labor shortage in {trade.get('trade_name', '')} affecting {trade.get('impact_description', '')}",
                    "recommended_action": "Consider resource reallocation or schedule adjustment"
                })
        
        # Check equipment-related risks
        for equipment in equipment_status.get("issues", []):
            if equipment.get("critical", False):
                at_risk_elements.append({
                    "wbs_element": equipment.get("wbs_element", ""),
                    "risk_level": "high" if equipment.get("no_alternative", False) else "medium",
                    "risk_factor": "equipment",
                    "description": f"Critical equipment issue: {equipment.get('description', '')}",
                    "recommended_action": equipment.get("recommended_action", "Arrange for immediate repair or replacement")
                })
        
        # Check material-related risks
        for material in material_status.get("delayed", []):
            criticality = material.get("criticality", "low")
            if criticality in ("medium", "high"):
                at_risk_elements.append({
                    "wbs_element": material.get("wbs_element", ""),
                    "risk_level": criticality,
                    "risk_factor": "material",
                    "description": f"Material delay: {material.get('description', '')}, expected delay: {material.get('delay_days', 0)} days",
                    "recommended_action": material.get("mitigation_strategy", "Evaluate alternative suppliers or materials")
                })
        
        return at_risk_elements
    
    def _calculate_schedule_impact(self, factor: EnvironmentalFactor) -> int:
        """Calculate the schedule impact in days based on an environmental factor.
        
        Args:
            factor: The environmental factor to evaluate
            
        Returns:
            int: Estimated impact in days
        """
        # This would be a more sophisticated model in production
        base_impact = {
            "weather": 2,
            "site_condition": 3,
            "regulatory": 5,
            "other": 1
        }.get(factor.factor_type, 1)
        
        # Adjust based on severity
        severity_multiplier = {
            "low": 0.5,
            "medium": 1.0,
            "high": 2.0,
            "critical": 3.0
        }.get(factor.severity, 1.0)
        
        return int(base_impact * severity_multiplier)
    
    def _calculate_cost_impact(self, factor: EnvironmentalFactor) -> float:
        """Calculate the cost impact based on an environmental factor.
        
        Args:
            factor: The environmental factor to evaluate
            
        Returns:
            float: Estimated cost impact
        """
        # Base cost impacts by factor type (this would be more sophisticated in production)
        base_impact = {
            "weather": 5000.0,
            "site_condition": 7500.0,
            "regulatory": 10000.0,
            "other": 2500.0
        }.get(factor.factor_type, 2500.0)
        
        # Adjust based on severity
        severity_multiplier = {
            "low": 0.5,
            "medium": 1.0,
            "high": 2.0,
            "critical": 3.0
        }.get(factor.severity, 1.0)
        
        # Factor in duration
        duration_factor = min(factor.duration_days / 5.0, 3.0) if factor.duration_days else 1.0
        
        return base_impact * severity_multiplier * duration_factor
    
    def _get_impact_level(self, value: float) -> str:
        """Convert a numeric impact value to a qualitative impact level.
        
        Args:
            value: Numeric impact value
            
        Returns:
            str: Impact level (low, medium, high, critical)
        """
        if value <= 1.0:
            return "low"
        elif value <= 3.0:
            return "medium"
        elif value <= 5.0:
            return "high"
        else:
            return "critical"
    
    def _generate_schedule_impact_description(self, days: int) -> str:
        """Generate a description of schedule impact based on days affected.
        
        Args:
            days: Number of days impacted
            
        Returns:
            str: Human-readable description of schedule impact
        """
        if days <= 0:
            return "No significant schedule impact expected."
        elif days <= 3:
            return f"Minor schedule impact of {days} days, likely absorbable within existing float."
        elif days <= 7:
            return f"Moderate schedule impact of {days} days, may require adjustment to near-term milestones."
        elif days <= 14:
            return f"Significant schedule impact of {days} days, likely to affect critical path activities."
        else:
            return f"Severe schedule impact of {days} days, will require major project replanning."
    
    def _generate_cost_impact_description(self, amount: float) -> str:
        """Generate a description of cost impact based on amount affected.
        
        Args:
            amount: Cost impact amount
            
        Returns:
            str: Human-readable description of cost impact
        """
        if amount <= 0:
            return "No significant cost impact expected."
        elif amount <= 5000:
            return f"Minor cost impact of ${amount:.2f}, within typical contingency reserves."
        elif amount <= 15000:
            return f"Moderate cost impact of ${amount:.2f}, may require reallocation of budget."
        elif amount <= 50000:
            return f"Significant cost impact of ${amount:.2f}, will affect overall project budget performance."
        else:
            return f"Severe cost impact of ${amount:.2f}, requires immediate financial review and replanning."
    
    def _generate_recommendation(self, factor: EnvironmentalFactor) -> Optional[str]:
        """Generate a recommendation based on an environmental factor.
        
        Args:
            factor: The environmental factor to evaluate
            
        Returns:
            str or None: Recommended action
        """
        if factor.factor_type == "weather":
            if factor.severity in ("high", "critical"):
                return f"Immediately secure the site against {factor.description}. Consider temporary work stoppage for affected activities."
            else:
                return f"Monitor {factor.description} conditions and prepare contingency plans for outdoor activities."
        
        elif factor.factor_type == "site_condition":
            if factor.severity in ("high", "critical"):
                return f"Conduct emergency assessment of {factor.description}. Allocate resources to resolve the condition before proceeding with affected work."
            else:
                return f"Address {factor.description} through standard site management procedures. Document all related costs separately."
        
        elif factor.factor_type == "regulatory":
            return f"Engage project compliance officer to address {factor.description}. Prepare documentation to demonstrate regulatory adherence."
        
        else:
            return None
    
    def _generate_supply_chain_mitigation(self, material: Dict[str, Any]) -> Optional[str]:
        """Generate a mitigation strategy for a delayed material.
        
        Args:
            material: Information about the delayed material
            
        Returns:
            str or None: Recommended mitigation strategy
        """
        material_name = material.get("material_name", "Unknown material")
        delay_days = material.get("delay_days", 0)
        critical = material.get("on_critical_path", False)
        alternatives = material.get("alternatives_available", False)
        
        if critical:
            if alternatives:
                return f"Immediately procure alternative for {material_name} from secondary suppliers, even at premium pricing, to avoid critical path delay."
            elif delay_days <= 7:
                return f"Consider fast-tracking subsequent activities to recover {delay_days} day delay in {material_name} delivery."
            else:
                return f"Initiate partial project replanning to accommodate {delay_days} day delay in critical {material_name} delivery."
        else:
            if alternatives:
                return f"Evaluate cost-benefit of alternative {material_name} sources versus accepting the {delay_days} day delay."
            else:
                return f"Resequence non-critical activities to minimize impact of {delay_days} day delay in {material_name} delivery."
