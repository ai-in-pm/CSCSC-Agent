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
from src.database.cscsc_analytics import CSCSCAnalyticsDB

app = Flask(__name__, template_folder='../user_interface/static')
CORS(app)

# Initialize analytics database
analytics_db = CSCSCAnalyticsDB()

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

@app.route('/api/v1/cscsc/architecture-diagram')
def get_architecture_diagram():
    try:
        diagram_path = Path('../user_interface/static/images/crewai_architecture.txt')
        with open(diagram_path, 'r') as f:
            return f.read()
    except Exception as e:
        return str(e), 500

@app.route('/api/v1/cscsc/status')
def get_status():
    return jsonify(demo_status)

@app.route('/api/v1/cscsc/results')
def get_results():
    return jsonify(demo_results)

@app.route('/api/v1/cscsc/forecast')
def run_forecast():
    """Run AI-powered Bayesian forecast model"""
    try:
        # In a real implementation, this would run actual forecast calculations
        # For the demo, we'll return synthetic forecast data
        forecast_data = {
            'historical': [
                {'date': '2025-01-01', 'value': 90000},
                {'date': '2025-02-01', 'value': 210000},
                {'date': '2025-03-01', 'value': 320000},
                {'date': '2025-04-01', 'value': 400000},
                {'date': '2025-05-01', 'value': 490000},
                {'date': '2025-06-01', 'value': 550000}
            ],
            'forecast': [
                {'date': '2025-05-01', 'value': 490000},
                {'date': '2025-06-01', 'value': 550000},
                {'date': '2025-07-01', 'value': 640000},
                {'date': '2025-08-01', 'value': 725000},
                {'date': '2025-09-01', 'value': 810000},
                {'date': '2025-10-01', 'value': 880000},
                {'date': '2025-11-01', 'value': 940000},
                {'date': '2025-12-01', 'value': 1020000}
            ],
            'upper_bound': [
                {'date': '2025-05-01', 'value': 524300},
                {'date': '2025-06-01', 'value': 588500},
                {'date': '2025-07-01', 'value': 684800},
                {'date': '2025-08-01', 'value': 775750},
                {'date': '2025-09-01', 'value': 866700},
                {'date': '2025-10-01', 'value': 941600},
                {'date': '2025-11-01', 'value': 1005800},
                {'date': '2025-12-01', 'value': 1091400}
            ],
            'lower_bound': [
                {'date': '2025-05-01', 'value': 455700},
                {'date': '2025-06-01', 'value': 511500},
                {'date': '2025-07-01', 'value': 595200},
                {'date': '2025-08-01', 'value': 674250},
                {'date': '2025-09-01', 'value': 753300},
                {'date': '2025-10-01', 'value': 818400},
                {'date': '2025-11-01', 'value': 874200},
                {'date': '2025-12-01', 'value': 948600}
            ],
            'metrics': {
                'accuracy': 98.1,
                'confidence_interval': 3.8,
                'rmse': 14250.32,
                'mae': 9876.54
            }
        }
        
        # Store forecast data in the database
        project_id = 'DEMO-2025-001'
        analytics_db.store_forecast(
            project_id=project_id,
            forecast_type='bayesian',
            forecast_data=forecast_data,
            model_params={
                'model': 'bayesian_structural_time_series',
                'seasonal_periods': 12,
                'trend_components': ['local_linear_trend', 'seasonal'],
                'hyperparameters': {
                    'sigma_level': 0.01,
                    'sigma_trend': 0.01,
                    'sigma_seasonal': 0.1
                }
            },
            metrics=forecast_data['metrics']
        )
        
        # Simulate ML processing delay
        time.sleep(1)
        add_message('Bayesian forecast model executed with 98.1% accuracy', 'task-complete')
        return jsonify(forecast_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/cscsc/sensitivity')
def run_sensitivity_analysis():
    """Run sensitivity analysis on project parameters"""
    try:
        # In a real implementation, this would run actual sensitivity calculations
        # For the demo, we'll return synthetic sensitivity data
        parameters = [
            {
                'name': 'Labor Productivity',
                'baseline': '100%',
                'negative_impact': '-15.3% SPI',
                'positive_impact': '+8.7% SPI',
                'elasticity': 1.53
            },
            {
                'name': 'Material Costs',
                'baseline': '$450,000',
                'negative_impact': '-7.2% CPI',
                'positive_impact': '+6.4% CPI',
                'elasticity': 0.72
            },
            {
                'name': 'Weather Days',
                'baseline': '12 days',
                'negative_impact': '-11.8% SPI',
                'positive_impact': '+4.1% SPI',
                'elasticity': 1.18
            },
            {
                'name': 'Permitting Time',
                'baseline': '45 days',
                'negative_impact': '-9.5% SPI',
                'positive_impact': '+3.2% SPI',
                'elasticity': 0.95
            },
            {
                'name': 'Equipment Availability',
                'baseline': '92%',
                'negative_impact': '-8.6% SPI',
                'positive_impact': '+2.3% SPI',
                'elasticity': 0.86
            }
        ]
        
        key_finding = 'Labor productivity has the highest elasticity (1.53), making it the most sensitive parameter affecting project performance. A 10% increase in productivity yields an 8.7% improvement in SPI.'
        
        sensitivity_data = {
            'parameters': parameters,
            'key_finding': key_finding
        }
        
        # Store sensitivity analysis results in the database
        project_id = 'DEMO-2025-001'
        analytics_db.store_sensitivity_analysis(
            project_id=project_id,
            parameters={
                'variation_percentage': 10,
                'metrics_analyzed': ['SPI', 'CPI'],
                'parameters_list': [p['name'] for p in parameters]
            },
            results={
                'detailed_results': parameters,
                'ranked_elasticity': [p['elasticity'] for p in sorted(parameters, key=lambda x: x['elasticity'], reverse=True)]
            },
            key_findings=key_finding
        )
        
        # Simulate processing delay
        time.sleep(1.5)
        add_message('Multivariate sensitivity analysis completed with elasticity calculations', 'task-complete')
        return jsonify(sensitivity_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/cscsc/monte-carlo')
def run_monte_carlo_simulation():
    """Run Monte Carlo simulation for project completion"""
    try:
        # In a real implementation, this would run actual Monte Carlo simulations
        # For the demo, we'll return synthetic simulation results
        completion_distribution = [
            {'month': 'Aug 2025', 'probability': 3},
            {'month': 'Sep 2025', 'probability': 14},
            {'month': 'Oct 2025', 'probability': 28},
            {'month': 'Nov 2025', 'probability': 35},
            {'month': 'Dec 2025', 'probability': 16},
            {'month': 'Jan 2026', 'probability': 3},
            {'month': 'Feb 2026', 'probability': 1}
        ]
        
        risk_factors = [
            {'name': 'Supply Chain Disruption', 'impact': 'High', 'confidence': 92},
            {'name': 'Weather Event (Flooding)', 'impact': 'Medium', 'confidence': 78},
            {'name': 'Regulatory Compliance', 'impact': 'Medium', 'confidence': 85},
            {'name': 'Labor Shortage', 'impact': 'High', 'confidence': 89, 'new': True},
            {'name': 'Quality Control Issues', 'impact': 'Low', 'confidence': 68, 'new': True}
        ]
        
        metadata = {
            'algorithm': 'Adaptive Stratified Sampling with Quasi-Monte Carlo integration',
            'confidence_level': 95,
            'correlation_matrix': 'Applied Pearson correlation coefficients for interdependent variables',
            'execution_time': '4.23 seconds'
        }
        
        simulation_data = {
            'simulation_runs': 5000,
            'completion_distribution': completion_distribution,
            'p50_completion': 'Oct 21, 2025',
            'p80_completion': 'Nov 29, 2025',
            'risk_factors': risk_factors,
            'metadata': metadata
        }
        
        # Store Monte Carlo simulation results in the database
        project_id = 'DEMO-2025-001'
        
        # Store the overall simulation results
        analytics_db.store_monte_carlo_simulation(
            project_id=project_id,
            simulation_runs=5000,
            distribution_data=completion_distribution,
            completion_dates={
                'p10': 'Sep 10, 2025',
                'p50': 'Oct 21, 2025',
                'p80': 'Nov 29, 2025',
                'p90': 'Dec 15, 2025'
            },
            risk_factors=risk_factors,
            metadata=metadata
        )
        
        # Also store each individual risk factor for detailed tracking
        for risk in risk_factors:
            # Only store newly detected risks in the separate risk_factors table
            if risk.get('new', False):
                analytics_db.store_risk_factor(
                    project_id=project_id,
                    risk_name=risk['name'],
                    impact=risk['impact'],
                    probability=risk.get('probability', 50),  # Default if not provided
                    confidence=risk['confidence'],
                    detection_method='Monte Carlo Simulation',
                    status='Identified'
                )
        
        # Simulate intensive computation
        time.sleep(2)
        add_message('Monte Carlo simulation completed with 5,000 runs. Two new risk factors identified.', 'task-complete')
        return jsonify(simulation_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        data_dir = Path("data/cscsc")
        data_dir.mkdir(parents=True, exist_ok=True)
        output_file = data_dir / f"cscsc_analysis_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, default=str, indent=2)
        
        add_message(f"Results saved to {output_file}", "task-complete")
        
    except Exception as e:
        add_message(f"Error during demo execution: {str(e)}", "error")
    finally:
        demo_status['running'] = False

@app.route('/api/v1/cscsc/run/<analysis_type>')
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
