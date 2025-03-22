import os
import json
import argparse
import sys
import requests
from datetime import datetime, timedelta
import random
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.physical_schemas import EnvironmentalFactor, SiteObservation
from src.evm_engine.physical_ai_assistant import PhysicalEVMAssistant
from src.evm_engine.calculator import EVMCalculator
from src.nlg_engine.generator import NLGGenerator
from src.config.settings import settings

class PhysicalAIDemo:
    """Demonstration of the Physical AI capabilities for EVM."""
    
    def __init__(self):
        """Initialize the demo with required components."""
        self.evm_calculator = EVMCalculator()
        self.physical_ai = PhysicalEVMAssistant(self.evm_calculator)
        self.nlg_generator = NLGGenerator()
        self.api_base_url = f"http://{settings.HOST}:{settings.PORT}"
        
    def run_demo(self, demo_type: str = "all"):
        """Run selected demonstration.
        
        Args:
            demo_type: Type of demo to run (environmental, supply_chain, site_progress, risk, all)
        """
        print(f"\n===== AI EVM Agent: Physical AI Capabilities Demo =====\n")
        
        if demo_type in ["environmental", "all"]:
            self.run_environmental_impact_demo()
            
        if demo_type in ["supply_chain", "all"]:
            self.run_supply_chain_impact_demo()
            
        if demo_type in ["site_progress", "all"]:
            self.run_site_progress_adjustment_demo()
            
        if demo_type in ["risk", "all"]:
            self.run_risk_assessment_demo()
            
        print("\n===== Demo Complete =====\n")
        print("To explore more capabilities, run the API server with 'python -m src.main'")
        print(f"and access the API documentation at http://{settings.HOST}:{settings.PORT}/docs")
            
    def run_environmental_impact_demo(self):
        """Demonstrate environmental impact analysis."""
        print("\n----- Environmental Impact Analysis Demo -----\n")
        
        # Create sample environmental factors
        factors = [
            EnvironmentalFactor(
                id="E001",
                project_id="P001",
                factor_type="weather",
                description="Heavy rainfall causing flooding in excavation areas",
                severity="high",
                start_date=datetime.now() - timedelta(days=2),
                end_date=datetime.now() + timedelta(days=1),
                duration_days=3,
                affected_wbs_elements=["1.3.1", "1.3.2"],
                affected_tasks=["T003", "T004"],
                status="active"
            ),
            EnvironmentalFactor(
                id="E002",
                project_id="P001",
                factor_type="site_condition",
                description="Unexpected rock formation requiring additional excavation equipment",
                severity="medium",
                start_date=datetime.now() - timedelta(days=1),
                duration_days=4,
                affected_wbs_elements=["1.3.1"],
                affected_tasks=["T003"],
                status="active"
            )
        ]
        
        # Perform analysis using the Physical AI Assistant
        impact_analysis = self.physical_ai.analyze_environmental_impact("P001", factors)
        
        # Generate explanation using the NLG Generator
        explanation = self.nlg_generator.generate_environmental_impact_explanation("P001", impact_analysis)
        
        # Display results
        print("Environmental Factors:")
        for factor in factors:
            print(f"  - {factor.factor_type.title()}: {factor.description} (Severity: {factor.severity})")
            
        print("\nImpact Analysis:")
        print(f"  Schedule Impact: {impact_analysis['schedule_impact']['total_days']} days")
        print(f"  Cost Impact: ${impact_analysis['cost_impact']['total_amount']:,.2f}")
        print(f"  Affected WBS Elements: {', '.join(impact_analysis['affected_wbs_elements'])}")
        
        print("\nAI-Generated Explanation:")
        print(f"  {explanation}")
        
        print("\nTo access this functionality via API:")
        print(f"  POST {self.api_base_url}/api/v1/physical/environmental-impact")
            
    def run_supply_chain_impact_demo(self):
        """Demonstrate supply chain impact analysis."""
        print("\n----- Supply Chain Impact Analysis Demo -----\n")
        
        # Create sample delayed materials
        delayed_materials = [
            {
                "material_name": "Structural Steel",
                "supplier_name": "Steel Supply Co.",
                "delay_days": 5,
                "dependent_tasks": ["T003", "T004"],
                "on_critical_path": True,
                "alternatives_available": False,
                "description": "20-ton shipment of structural steel beams delayed due to transportation issues"
            },
            {
                "material_name": "Electrical Components",
                "supplier_name": "Electro Systems Inc.",
                "delay_days": 3,
                "dependent_tasks": ["T005"],
                "on_critical_path": False,
                "alternatives_available": True,
                "description": "Control panel components delayed due to manufacturing backlog"
            }
        ]
        
        # Perform analysis using the Physical AI Assistant
        impact_analysis = self.physical_ai.analyze_supply_chain_impact("P001", delayed_materials)
        
        # Generate explanation using the NLG Generator
        explanation = self.nlg_generator.generate_supply_chain_impact_explanation("P001", impact_analysis)
        
        # Display results
        print("Delayed Materials:")
        for material in delayed_materials:
            print(f"  - {material['material_name']}: {material['description']}")
            print(f"    Delay: {material['delay_days']} days, Critical Path: {'Yes' if material['on_critical_path'] else 'No'}")
            
        print("\nImpact Analysis:")
        print(f"  Critical Path Impact: {'Yes' if impact_analysis['critical_path_impact'] else 'No'}")
        print(f"  Schedule Delay: {impact_analysis['schedule_delay_days']} days")
        print(f"  Affected Tasks: {', '.join(impact_analysis['affected_tasks'])}")
        print("\n  Mitigation Strategies:")
        for strategy in impact_analysis['mitigation_strategies']:
            print(f"    - {strategy}")
        
        print("\nAI-Generated Explanation:")
        print(f"  {explanation}")
        
        print("\nTo access this functionality via API:")
        print(f"  POST {self.api_base_url}/api/v1/physical/supply-chain-impact")
            
    def run_site_progress_adjustment_demo(self):
        """Demonstrate site progress adjustment."""
        print("\n----- Site Progress Adjustment Demo -----\n")
        
        # Create sample site observations
        site_observations = [
            {
                "observed_progress": 0.65,  # 65% complete observed on site
                "reported_progress": 0.75,  # 75% complete in system reports
                "cost_implication": 2500.0,  # $2,500 additional cost identified
                "notes": "Site inspection revealed that only 65% of concrete work is complete, contrary to 75% reported. Additional rebar needed."
            },
            {
                "observed_progress": 0.60,  # 60% complete observed on site
                "reported_progress": 0.75,  # 75% complete in system reports
                "notes": "Second inspector confirmed progress discrepancy in concrete work."
            }
        ]
        
        # Perform analysis using the Physical AI Assistant
        adjustment = self.physical_ai.generate_site_progress_adjustment("T002", site_observations)
        
        # Generate explanation using the NLG Generator
        explanation = self.nlg_generator.generate_site_adjustment_explanation("T002", adjustment)
        
        # Display results
        print("Site Observations:")
        for i, observation in enumerate(site_observations, 1):
            print(f"  Observation #{i}:")
            print(f"    - Observed Progress: {observation['observed_progress']*100:.1f}%")
            print(f"    - Reported Progress: {observation['reported_progress']*100:.1f}%")
            if 'cost_implication' in observation and observation['cost_implication'] > 0:
                print(f"    - Cost Implication: ${observation['cost_implication']:,.2f}")
            print(f"    - Notes: {observation['notes']}")
            
        print("\nRecommended Adjustments:")
        percent_adj = adjustment['percent_complete_adjustment']
        cost_adj = adjustment['actual_cost_adjustment']
        
        print(f"  - Percent Complete: {'-' if percent_adj < 0 else '+'}{abs(percent_adj)*100:.1f}%")
        print(f"  - Actual Cost: {'-' if cost_adj < 0 else '+'}{abs(cost_adj):,.2f}")
        print(f"  - Confidence Level: {adjustment['confidence_level'].title()}")
        print(f"  - Justification: {adjustment['justification']}")
        
        print("\nAI-Generated Explanation:")
        print(f"  {explanation}")
        
        print("\nTo access this functionality via API:")
        print(f"  POST {self.api_base_url}/api/v1/physical/site-progress-adjustment")
            
    def run_risk_assessment_demo(self):
        """Demonstrate risk assessment based on site conditions."""
        print("\n----- Risk Assessment Demo -----\n")
        
        # Create sample site conditions
        site_conditions = {
            "weather": {
                "severe_weather_warning": True,
                "warning_details": "Heavy thunderstorms expected in the next 48 hours"
            },
            "labor": {
                "shortage": True,
                "affected_trades": [
                    {"trade_name": "Electricians", "wbs_element": "1.4.1", "impact_description": "electrical rough-in work"}
                ]
            },
            "equipment": {
                "issues": [
                    {
                        "critical": True,
                        "no_alternative": True,
                        "wbs_element": "1.3.2",
                        "description": "Crane malfunction",
                        "recommended_action": "Schedule emergency repair or rent replacement"
                    }
                ]
            },
            "materials": {
                "delayed": [
                    {
                        "wbs_element": "1.5",
                        "criticality": "medium",
                        "description": "HVAC equipment delayed by 1 week",
                        "delay_days": 7,
                        "mitigation_strategy": "Resequence installation tasks to minimize impact"
                    }
                ]
            }
        }
        
        # Perform analysis using the Physical AI Assistant
        at_risk_elements = self.physical_ai.identify_at_risk_wbs_elements("P001", site_conditions)
        
        # Generate explanation using the NLG Generator
        explanation = self.nlg_generator.generate_risk_assessment_explanation("P001", at_risk_elements)
        
        # Display results
        print("Current Site Conditions:")
        print("  - Weather: Severe weather warning for thunderstorms")
        print("  - Labor: Shortage of electricians")
        print("  - Equipment: Critical crane malfunction")
        print("  - Materials: HVAC equipment delayed by 1 week")
            
        print("\nAt-Risk WBS Elements:")
        for element in at_risk_elements:
            print(f"  - WBS {element['wbs_element']} - {element['risk_level'].upper()} RISK:")
            print(f"    Factor: {element['risk_factor']}")
            print(f"    Description: {element['description']}")
            print(f"    Action: {element['recommended_action']}")
        
        print("\nAI-Generated Explanation:")
        print(f"  {explanation}")
        
        print("\nTo access this functionality via API:")
        print(f"  POST {self.api_base_url}/api/v1/physical/at-risk-wbs-elements")


def main():
    """Run the Physical AI Demo."""
    parser = argparse.ArgumentParser(description="EVM Physical AI Capabilities Demo")
    parser.add_argument(
        "--type", 
        choices=["environmental", "supply_chain", "site_progress", "risk", "all"], 
        default="all",
        help="Type of demo to run"
    )
    
    args = parser.parse_args()
    
    demo = PhysicalAIDemo()
    demo.run_demo(args.type)


if __name__ == "__main__":
    main()
