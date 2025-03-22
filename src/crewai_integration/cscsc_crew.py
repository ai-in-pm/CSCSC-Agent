from typing import Dict, List, Any
import os
import json
from datetime import datetime
import logging

# Import CrewAI components
from crewai import Agent, Task, Crew, Process
from crewai.tasks.task_output import TaskOutput

# Import custom utilities
from src.utils.json_helpers import serialize_with_dates

logger = logging.getLogger(__name__)

class CSCSCAgentCrew:
    """A CrewAI implementation for Physical EVM management.
    
    This crew consists of specialized agents that collaborate to analyze physical
    project data, provide insights, and recommend actions for effective EVM.
    """
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the CSCSC Agent Crew.
        
        Args:
            openai_api_key: OpenAI API key for LLM access. If not provided, will use the
                          OPENAI_API_KEY environment variable.
        """
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        self.agents = self._create_agents()
        logger.info("CSCSC Agent Crew initialized with specialized agents")
    
    def _create_agents(self) -> Dict[str, Agent]:
        """Create the specialized agents for the crew.
        
        Returns:
            Dict of agents by role
        """
        # Environmental Analysis Agent
        environmental_agent = Agent(
            role="Environmental Impact Analyst",
            goal="Analyze environmental factors affecting project performance",
            backstory="""You are an expert in environmental science and construction 
            management with decades of experience assessing how weather, site conditions, 
            and natural factors impact construction projects. You understand the complex 
            interplay between environmental variables and project performance metrics.""",
            verbose=True,
            allow_delegation=True
        )
        
        # Supply Chain Agent
        supply_chain_agent = Agent(
            role="Supply Chain Manager",
            goal="Optimize material procurement and assess supply chain impacts",
            backstory="""You have extensive experience in construction procurement and 
            supply chain management. You excel at identifying potential material delays, 
            assessing their impacts on project timelines, and developing mitigation 
            strategies to keep projects on track despite supply challenges.""",
            verbose=True,
            allow_delegation=True
        )
        
        # Site Progress Verification Agent
        site_verification_agent = Agent(
            role="Site Progress Verifier",
            goal="Compare reported progress with physical observations to ensure accuracy",
            backstory="""You are a veteran construction inspector with a keen eye for 
            detail and precise measurement skills. You've spent years reconciling what's 
            in project reports with actual site conditions, ensuring that earned value 
            calculations reflect real-world progress.""",
            verbose=True,
            allow_delegation=True
        )
        
        # Risk Assessment Agent
        risk_agent = Agent(
            role="Risk Assessment Specialist",
            goal="Identify and quantify physical risks to project execution",
            backstory="""You are an expert in construction risk management with a 
            background in both engineering and probability analysis. You excel at 
            identifying potential failure points, quantifying their likelihood and impact, 
            and developing practical mitigation plans.""",
            verbose=True,
            allow_delegation=True
        )
        
        # EVM Integration Agent
        evm_agent = Agent(
            role="EVM Integration Specialist",
            goal="Synthesize physical insights into EVM metrics and recommendations",
            backstory="""You are a seasoned project controls expert with deep knowledge 
            of earned value management principles. You excel at translating physical 
            project realities into EVM metrics and actionable recommendations that 
            project managers can use to make informed decisions.""",
            verbose=True,
            allow_delegation=True
        )
        
        return {
            "environmental": environmental_agent,
            "supply_chain": supply_chain_agent,
            "site_verification": site_verification_agent,
            "risk": risk_agent,
            "evm": evm_agent
        }
    
    def analyze_environmental_impact(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use the crew to analyze environmental impacts on the project.
        
        Args:
            project_data: Dict containing project information and environmental factors
            
        Returns:
            Dict containing analysis and recommendations
        """
        logger.info(f"Starting environmental impact analysis for project {project_data.get('project_id')}")
        
        # Create tasks for environmental analysis
        analyze_factors_task = Task(
            description=f"""Analyze the following environmental factors affecting project {project_data.get('project_id')}:
            {serialize_with_dates(project_data.get('environmental_factors', []))}
            
            Determine how these factors impact the project schedule, cost, and quality. 
            Categorize each factor by severity and provide quantitative impact estimates.""",
            agent=self.agents["environmental"],
            expected_output="A comprehensive analysis of environmental impacts with quantified effects"
        )
        
        generate_mitigation_task = Task(
            description="""Based on the environmental impact analysis, develop specific 
            mitigation strategies for each significant factor. Include timeline adjustments, 
            resource allocation recommendations, and alternative approaches.""",
            agent=self.agents["environmental"],
            expected_output="Detailed mitigation strategies for each environmental factor",
            context=[analyze_factors_task]
        )
        
        integrate_with_evm_task = Task(
            description="""Incorporate the environmental impact analysis and mitigation strategies 
            into adjusted EVM metrics. Calculate the expected changes to schedule variance (SV), 
            cost variance (CV), SPI, and CPI based on these environmental factors.""",
            agent=self.agents["evm"],
            expected_output="Updated EVM metrics accounting for environmental factors",
            context=[analyze_factors_task, generate_mitigation_task]
        )
        
        # Create and run the crew
        environmental_crew = Crew(
            agents=[self.agents["environmental"], self.agents["evm"]],
            tasks=[analyze_factors_task, generate_mitigation_task, integrate_with_evm_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Execute the crew's work
        result = environmental_crew.kickoff()
        
        return self._parse_crew_result(result, "environmental_impact")
    
    def analyze_supply_chain_impact(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use the crew to analyze supply chain impacts on the project.
        
        Args:
            project_data: Dict containing project information and material delays
            
        Returns:
            Dict containing analysis and recommendations
        """
        logger.info(f"Starting supply chain impact analysis for project {project_data.get('project_id')}")
        
        # Create tasks for supply chain analysis
        analyze_delays_task = Task(
            description=f"""Analyze the following material delays affecting project {project_data.get('project_id')}:
            {serialize_with_dates(project_data.get('delayed_materials', []))}
            
            Determine how these delays impact the project schedule, critical path, and dependent activities. 
            Quantify the impact in terms of days delayed and cost implications.""",
            agent=self.agents["supply_chain"],
            expected_output="A detailed analysis of supply chain delays with quantified impacts"
        )
        
        generate_mitigation_task = Task(
            description="""Based on the supply chain impact analysis, develop specific 
            procurement and scheduling strategies to mitigate these delays. Include 
            alternative suppliers, material substitutions, and schedule resequencing options.""",
            agent=self.agents["supply_chain"],
            expected_output="Detailed mitigation strategies for each material delay",
            context=[analyze_delays_task]
        )
        
        assess_risk_task = Task(
            description="""Evaluate the risks associated with the identified supply chain 
            disruptions and the proposed mitigation strategies. Identify any secondary risks 
            that might emerge from the mitigation actions.""",
            agent=self.agents["risk"],
            expected_output="Risk assessment of supply chain disruptions and mitigations",
            context=[analyze_delays_task, generate_mitigation_task]
        )
        
        integrate_with_evm_task = Task(
            description="""Incorporate the supply chain impact analysis, mitigation strategies, 
            and risk assessment into adjusted EVM metrics. Calculate the expected changes to 
            schedule variance (SV), cost variance (CV), SPI, and CPI.""",
            agent=self.agents["evm"],
            expected_output="Updated EVM metrics accounting for supply chain factors",
            context=[analyze_delays_task, generate_mitigation_task, assess_risk_task]
        )
        
        # Create and run the crew
        supply_chain_crew = Crew(
            agents=[self.agents["supply_chain"], self.agents["risk"], self.agents["evm"]],
            tasks=[analyze_delays_task, generate_mitigation_task, assess_risk_task, integrate_with_evm_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Execute the crew's work
        result = supply_chain_crew.kickoff()
        
        return self._parse_crew_result(result, "supply_chain_impact")
    
    def verify_site_progress(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use the crew to verify site progress and reconcile with reported values.
        
        Args:
            project_data: Dict containing project information and site observations
            
        Returns:
            Dict containing verification results and adjustments
        """
        logger.info(f"Starting site progress verification for project {project_data.get('project_id')}")
        
        # Create tasks for site verification
        analyze_observations_task = Task(
            description=f"""Analyze the following site observations for project {project_data.get('project_id')}:
            {json.dumps(project_data.get('site_observations', []), indent=2)}
            
            Compare the observed progress with reported progress. Identify discrepancies 
            and assess their impact on earned value calculations.""",
            agent=self.agents["site_verification"],
            expected_output="Analysis of discrepancies between observed and reported progress"
        )
        
        recommend_adjustments_task = Task(
            description="""Based on the site observation analysis, recommend specific 
            adjustments to percent complete values and actual costs. Provide justification 
            for each adjustment and assign a confidence level.""",
            agent=self.agents["site_verification"],
            expected_output="Recommended adjustments to EVM inputs with justifications",
            context=[analyze_observations_task]
        )
        
        integrate_with_evm_task = Task(
            description="""Incorporate the site verification results and recommended adjustments 
            into revised EVM metrics. Calculate the adjusted BCWP, ACWP, CV, CPI, and EAC values 
            based on the verified physical progress.""",
            agent=self.agents["evm"],
            expected_output="Recalculated EVM metrics based on verified progress",
            context=[analyze_observations_task, recommend_adjustments_task]
        )
        
        # Create and run the crew
        verification_crew = Crew(
            agents=[self.agents["site_verification"], self.agents["evm"]],
            tasks=[analyze_observations_task, recommend_adjustments_task, integrate_with_evm_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Execute the crew's work
        result = verification_crew.kickoff()
        
        return self._parse_crew_result(result, "site_progress_verification")
    
    def assess_project_risks(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use the crew to perform a comprehensive risk assessment.
        
        Args:
            project_data: Dict containing project information and current conditions
            
        Returns:
            Dict containing risk assessment and mitigation strategies
        """
        logger.info(f"Starting risk assessment for project {project_data.get('project_id')}")
        
        # Create tasks for risk assessment
        analyze_conditions_task = Task(
            description=f"""Analyze the current site conditions for project {project_data.get('project_id')}:
            {json.dumps(project_data.get('site_conditions', {}), indent=2)}
            
            Identify all risk factors including weather, labor, equipment, and materials.
            Categorize each risk by likelihood and potential impact.""",
            agent=self.agents["risk"],
            expected_output="Comprehensive risk factor identification and categorization"
        )
        
        identify_at_risk_elements_task = Task(
            description="""Based on the identified risk factors, determine which WBS elements 
            are most at risk. Provide a risk score for each affected element and explain 
            the specific threats to successful completion.""",
            agent=self.agents["risk"],
            expected_output="List of at-risk WBS elements with risk scores and explanations",
            context=[analyze_conditions_task]
        )
        
        develop_mitigation_task = Task(
            description="""Develop specific risk mitigation strategies for each at-risk WBS element. 
            Include preventive actions, contingency plans, and recommended timeline adjustments.""",
            agent=self.agents["risk"],
            expected_output="Detailed risk mitigation strategies for each at-risk element",
            context=[analyze_conditions_task, identify_at_risk_elements_task]
        )
        
        integrate_with_evm_task = Task(
            description="""Incorporate the risk assessment and mitigation strategies into EVM 
            forecasting. Calculate risk-adjusted estimates for EAC and ETC, and provide 
            confidence intervals for key metrics.""",
            agent=self.agents["evm"],
            expected_output="Risk-adjusted EVM forecasts with confidence intervals",
            context=[analyze_conditions_task, identify_at_risk_elements_task, develop_mitigation_task]
        )
        
        # Create and run the crew
        risk_crew = Crew(
            agents=[self.agents["risk"], self.agents["evm"]],
            tasks=[analyze_conditions_task, identify_at_risk_elements_task, develop_mitigation_task, integrate_with_evm_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Execute the crew's work
        result = risk_crew.kickoff()
        
        return self._parse_crew_result(result, "risk_assessment")
    
    def _parse_crew_result(self, result: TaskOutput, analysis_type: str) -> Dict[str, Any]:
        """Parse CrewAI results into a structured format.
        
        Args:
            result: TaskOutput from the crew execution
            analysis_type: Type of analysis performed
            
        Returns:
            Dict containing structured results
        """
        # In a production system, we would parse the LLM output into a structured format
        # For now, we'll return a basic structure with the raw output
        
        parsed_result = {
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat(),
            "crew_output": str(result),
            "success": True
        }
        
        return parsed_result
