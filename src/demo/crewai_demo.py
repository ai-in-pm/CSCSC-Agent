import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
import logging

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.crewai_integration.cscsc_crew import CSCSCAgentCrew
from src.utils.helpers import generate_sample_physical_data, _convert_dates_to_iso

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CrewAIDemo:
    """Demonstration of the CrewAI integration for Physical EVM analysis."""
    
    def __init__(self, api_key: str = None):
        """Initialize the CrewAI demo.
        
        Args:
            api_key: OpenAI API key (optional, can use environment variable)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No OpenAI API key provided. Please set OPENAI_API_KEY environment variable.")
            
        # Create the CSCSC Agent Crew
        self.crew = CSCSCAgentCrew(openai_api_key=self.api_key)
        
        # Initialize data directory
        self.data_dir = Path("data/crewai")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def run_demo(self, analysis_type: str = "all", save_results: bool = True):
        """Run the CrewAI demo for the specified analysis type.
        
        Args:
            analysis_type: Type of analysis to run (environmental, supply_chain, site_progress, risk, all)
            save_results: Whether to save results to files
        """
        print(f"\n===== AI EVM Agent: CrewAI Integration Demo =====\n")
        
        if not self.api_key:
            print("\nError: OpenAI API key is required for this demo.")
            print("Please set the OPENAI_API_KEY environment variable or provide it as an argument.")
            return
        
        # Generate sample physical data
        print("\nGenerating sample project data for CrewAI analysis...")
        project_data = generate_sample_physical_data()
        
        # Track results
        results = {}
        
        # Run the selected analyses
        if analysis_type in ["environmental", "all"]:
            print("\n----- Environmental Impact Analysis with CrewAI -----")
            results["environmental"] = self.crew.analyze_environmental_impact(project_data)
            self._display_result(results["environmental"])
            
        if analysis_type in ["supply_chain", "all"]:
            print("\n----- Supply Chain Impact Analysis with CrewAI -----")
            results["supply_chain"] = self.crew.analyze_supply_chain_impact(project_data)
            self._display_result(results["supply_chain"])
            
        if analysis_type in ["site_progress", "all"]:
            print("\n----- Site Progress Verification with CrewAI -----")
            results["site_progress"] = self.crew.verify_site_progress(project_data)
            self._display_result(results["site_progress"])
            
        if analysis_type in ["risk", "all"]:
            print("\n----- Risk Assessment with CrewAI -----")
            results["risk"] = self.crew.assess_project_risks(project_data)
            self._display_result(results["risk"])
        
        # Save results if requested
        if save_results and results:
            self._save_results(results)
            
        print("\n===== Demo Complete =====\n")
    
    def _display_result(self, result: dict):
        """Display CrewAI analysis results.
        
        Args:
            result: Analysis result from CrewAI
        """
        print(f"\nAnalysis Type: {result['analysis_type']}")
        print(f"Timestamp: {result['timestamp']}")
        print("\nCrewAI Output:")
        print("-" * 80)
        print(result['crew_output'])
        print("-" * 80)
    
    def _save_results(self, results: dict):
        """Save analysis results to files.
        
        Args:
            results: Dict of analysis results
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.data_dir / f"crewai_analysis_{timestamp}.json"
        
        # Convert to serializable format
        serializable_results = {k: v.copy() for k, v in results.items()}
        for result in serializable_results.values():
            _convert_dates_to_iso(result)
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"\nResults saved to {output_file}")


def main():
    """Run the CrewAI demo."""
    parser = argparse.ArgumentParser(description="EVM CrewAI Demo")
    parser.add_argument(
        "--api-key", 
        type=str,
        help="OpenAI API key (optional, can use OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--type", 
        choices=["environmental", "supply_chain", "site_progress", "risk", "all"], 
        default="all",
        help="Type of analysis to run"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save results to files"
    )
    
    args = parser.parse_args()
    
    demo = CrewAIDemo(api_key=args.api_key)
    demo.run_demo(args.type, save_results=not args.no_save)


if __name__ == "__main__":
    main()
