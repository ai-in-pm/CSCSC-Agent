import os
import sys
import json
import time
import threading
import argparse
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS

from src.crewai_integration.cscsc_crew import CSCSCAgentCrew
from src.utils.helpers import generate_sample_physical_data
from src.utils.json_helpers import serialize_with_dates

app = Flask(__name__, template_folder='../user_interface/static')
CORS(app)

# Global variables to track demo progress
demo_results = {}
demo_status = {
    'running': False,
    'analysis_type': None,
    'progress': 0,
    'messages': [],
    'agent_statuses': {
        'Environmental Impact Analyst': 'Idle',
        'Supply Chain Manager': 'Idle',
        'Site Progress Verifier': 'Idle',
        'Risk Assessment Specialist': 'Idle',
        'EVM Integration Specialist': 'Idle'
    },
    'task_count': 0,
    'completed_tasks': 0
}

@app.route('/')
def index():
    return render_template('cscsc_agent_demo.html')

@app.route('/api/v1/crewai/architecture-diagram')
def get_architecture_diagram():
    try:
        diagram_path = Path('../user_interface/static/images/crewai_architecture.txt')
        with open(diagram_path, 'r') as f:
            return f.read()
    except Exception as e:
        return str(e), 500

@app.route('/api/v1/crewai/status')
def get_status():
    return jsonify(demo_status)

@app.route('/api/v1/crewai/results')
def get_results():
    return jsonify(demo_results)

def add_message(message, log_type='info'):
    timestamp = datetime.now().strftime('%H:%M:%S')
    demo_status['messages'].append({
        'timestamp': timestamp,
        'message': message,
        'type': log_type
    })
    print(f"[{timestamp}] [{log_type}] {message}")

def update_agent_status(agent, status):
    demo_status['agent_statuses'][agent] = status
    add_message(f"{agent} status: {status}")

def update_progress(progress, analysis_type=None):
    demo_status['progress'] = progress
    if analysis_type:
        demo_status['analysis_type'] = analysis_type

def run_demo_thread(api_key, analysis_type):
    """Run the CSCSC Agent Crew demo in a separate thread."""
    try:
        # Reset status
        global demo_status, demo_results
        demo_status['running'] = True
        demo_status['progress'] = 0
        demo_status['messages'] = []
        demo_status['completed_tasks'] = 0
        demo_status['analysis_type'] = analysis_type
        for agent in demo_status['agent_statuses']:
            demo_status['agent_statuses'][agent] = 'Idle'
        
        # Initialize crew
        add_message(f"Initializing CSCSC Agent Crew for {analysis_type} analysis")
        crew = CSCSCAgentCrew(openai_api_key=api_key)
        
        # Generate sample data
        add_message("Generating sample project data")
        update_progress(10)
        project_data = generate_sample_physical_data()
        
        # Run the analysis
        if analysis_type == 'environmental':
            update_agent_status('Environmental Impact Analyst', 'Working')
            demo_status['task_count'] = 3  # Analyze, Mitigate, Integrate
            
            add_message("Analyzing environmental factors", "thinking")
            update_progress(20)
            time.sleep(2)  # Simulate processing time
            
            add_message("Developing mitigation strategies", "thinking")
            update_progress(40)
            time.sleep(2)  # Simulate processing time
            
            update_agent_status('Environmental Impact Analyst', 'Completed')
            demo_status['completed_tasks'] = 2
            update_agent_status('EVM Integration Specialist', 'Working')
            
            add_message("Integrating with EVM metrics", "thinking")
            update_progress(60)
            time.sleep(2)  # Simulate processing time
            
            add_message("Running environmental impact analysis", "agent-interaction")
            update_progress(80)
            results = crew.analyze_environmental_impact(project_data)
            
            update_agent_status('EVM Integration Specialist', 'Completed')
            demo_status['completed_tasks'] = 3
            
        elif analysis_type == 'supply_chain':
            update_agent_status('Supply Chain Manager', 'Working')
            demo_status['task_count'] = 3  # Analyze, Mitigate, Integrate
            
            add_message("Analyzing supply chain delays", "thinking")
            update_progress(20)
            time.sleep(2)  # Simulate processing time
            
            add_message("Developing procurement strategies", "thinking")
            update_progress(40)
            time.sleep(2)  # Simulate processing time
            
            update_agent_status('Supply Chain Manager', 'Completed')
            demo_status['completed_tasks'] = 2
            update_agent_status('EVM Integration Specialist', 'Working')
            
            add_message("Integrating with EVM metrics", "thinking")
            update_progress(60)
            time.sleep(2)  # Simulate processing time
            
            add_message("Running supply chain impact analysis", "agent-interaction")
            update_progress(80)
            results = crew.analyze_supply_chain_impact(project_data)
            
            update_agent_status('EVM Integration Specialist', 'Completed')
            demo_status['completed_tasks'] = 3
            
        elif analysis_type == 'site_progress':
            update_agent_status('Site Progress Verifier', 'Working')
            demo_status['task_count'] = 2  # Verify, Integrate
            
            add_message("Verifying site progress", "thinking")
            update_progress(30)
            time.sleep(2)  # Simulate processing time
            
            update_agent_status('Site Progress Verifier', 'Completed')
            demo_status['completed_tasks'] = 1
            update_agent_status('EVM Integration Specialist', 'Working')
            
            add_message("Integrating with EVM metrics", "thinking")
            update_progress(60)
            time.sleep(2)  # Simulate processing time
            
            add_message("Running site progress verification", "agent-interaction")
            update_progress(80)
            results = crew.verify_site_progress(project_data)
            
            update_agent_status('EVM Integration Specialist', 'Completed')
            demo_status['completed_tasks'] = 2
            
        elif analysis_type == 'risk':
            update_agent_status('Risk Assessment Specialist', 'Working')
            demo_status['task_count'] = 3  # Identify, Evaluate, Integrate
            
            add_message("Identifying project risks", "thinking")
            update_progress(20)
            time.sleep(2)  # Simulate processing time
            
            add_message("Evaluating risk impacts", "thinking")
            update_progress(40)
            time.sleep(2)  # Simulate processing time
            
            update_agent_status('Risk Assessment Specialist', 'Completed')
            demo_status['completed_tasks'] = 2
            update_agent_status('EVM Integration Specialist', 'Working')
            
            add_message("Integrating with EVM metrics", "thinking")
            update_progress(60)
            time.sleep(2)  # Simulate processing time
            
            add_message("Running risk assessment analysis", "agent-interaction")
            update_progress(80)
            results = crew.assess_project_risks(project_data)
            
            update_agent_status('EVM Integration Specialist', 'Completed')
            demo_status['completed_tasks'] = 3
            
        else:  # all
            # Run all analyses sequentially
            add_message("Running all analyses sequentially", "info")
            update_progress(10)
            
            # Environmental analysis
            update_agent_status('Environmental Impact Analyst', 'Working')
            add_message("Running environmental impact analysis", "agent-interaction")
            results = {}
            results['environmental'] = crew.analyze_environmental_impact(project_data)
            update_agent_status('Environmental Impact Analyst', 'Completed')
            update_progress(25)
            
            # Supply chain analysis
            update_agent_status('Supply Chain Manager', 'Working')
            add_message("Running supply chain impact analysis", "agent-interaction")
            results['supply_chain'] = crew.analyze_supply_chain_impact(project_data)
            update_agent_status('Supply Chain Manager', 'Completed')
            update_progress(50)
            
            # Site progress verification
            update_agent_status('Site Progress Verifier', 'Working')
            add_message("Running site progress verification", "agent-interaction")
            results['site_progress'] = crew.verify_site_progress(project_data)
            update_agent_status('Site Progress Verifier', 'Completed')
            update_progress(75)
            
            # Risk assessment
            update_agent_status('Risk Assessment Specialist', 'Working')
            add_message("Running risk assessment", "agent-interaction")
            results['risk'] = crew.assess_project_risks(project_data)
            update_agent_status('Risk Assessment Specialist', 'Completed')
            update_progress(100)
        
        # Save results
        demo_results = results
        add_message("Analysis complete!", "task-complete")
        update_progress(100)
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_dir = Path("data/crewai")
        data_dir.mkdir(parents=True, exist_ok=True)
        output_file = data_dir / f"crewai_analysis_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, default=str, indent=2)
        
        add_message(f"Results saved to {output_file}", "task-complete")
        
    except Exception as e:
        add_message(f"Error during demo execution: {str(e)}", "error")
    finally:
        demo_status['running'] = False

@app.route('/api/v1/crewai/run/<analysis_type>')
def run_demo(analysis_type):
    if demo_status['running']:
        return jsonify({'error': 'Demo already running'}), 400
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return jsonify({'error': 'OPENAI_API_KEY environment variable not set'}), 400
    
    valid_types = ['environmental', 'supply_chain', 'site_progress', 'risk', 'all']
    if analysis_type not in valid_types:
        return jsonify({'error': f'Invalid analysis type. Must be one of: {valid_types}'}), 400
    
    # Start the demo in a new thread
    threading.Thread(target=run_demo_thread, args=(api_key, analysis_type)).start()
    
    return jsonify({'message': f'Started {analysis_type} analysis demo'}), 200

def main():
    """Run the web demo."""
    parser = argparse.ArgumentParser(description="CSCSC AI Agent Web Demo")
    parser.add_argument(
        "--api-key", 
        type=str,
        help="OpenAI API key (optional, can use OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--port", 
        type=int,
        default=8000,
        help="Port to run the server on"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Run in debug mode"
    )
    
    args = parser.parse_args()
    
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
    
    # Check if API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("\nWarning: OPENAI_API_KEY environment variable not set.")
        print("Set it by running: set OPENAI_API_KEY=your-api-key-here")
    
    print(f"\n===== Starting CSCSC AI Agent Web Demo =====\n")
    print(f"Server will be available at: http://localhost:{args.port}/")
    print(f"Press Ctrl+C to stop the server\n")
    
    # Ensure the diagram file exists
    diagram_path = Path(__file__).parent.parent / 'user_interface/static/images/crewai_architecture.txt'
    if not diagram_path.exists():
        print(f"Warning: Architecture diagram not found at {diagram_path}")
    
    app.run(host='0.0.0.0', port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()
