import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from crewai import Agent, Task, Crew, Process
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_test(api_key=None):
    """Run a simple CrewAI test."""
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    print("\n===== Testing CrewAI Integration =====\n")
    
    # Check if API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")
        print("You can set it by running: set OPENAI_API_KEY=your-api-key-here")
        return False
    
    try:
        # Create a simple agent
        test_agent = Agent(
            role="Test Agent",
            goal="Verify that CrewAI is working properly",
            backstory="You are a test agent created to verify the CrewAI installation.",
            verbose=True
        )
        
        # Create a simple task
        test_task = Task(
            description="Generate a simple greeting message to verify that CrewAI is working properly.",
            agent=test_agent,
            expected_output="A greeting message"
        )
        
        # Create a crew with just one agent and one task
        test_crew = Crew(
            agents=[test_agent],
            tasks=[test_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Run the crew
        print("\nExecuting CrewAI test...\n")
        result = test_crew.kickoff()
        
        print("\n===== Test Result =====\n")
        print(result)
        print("\n===== CrewAI is working! =====\n")
        
        return True
    
    except Exception as e:
        print(f"\nError during CrewAI test: {str(e)}")
        return False

def main():
    """Main function to run the test."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test CrewAI Installation")
    parser.add_argument(
        "--api-key", 
        type=str,
        help="OpenAI API key (optional, can use OPENAI_API_KEY env var)"
    )
    
    args = parser.parse_args()
    run_test(api_key=args.api_key)

if __name__ == "__main__":
    main()
