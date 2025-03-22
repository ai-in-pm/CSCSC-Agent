import os
import sys
import json
import time
import threading
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import math
import random

# Add the project root to the Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS

# Import the analytics database module
from src.database.cscsc_analytics import CSCSCAnalyticsDB

app = Flask(__name__, template_folder='../user_interface/static')
CORS(app)

# Initialize analytics database
analytics_db = CSCSCAnalyticsDB()

# Global variables to track demo progress
demo_results = {}
demo_status = {
    'status': 'idle',  # idle, running, complete, error
    'messages': []
}

# Ensure demo status directory exists
data_dir = root_dir / 'data'
data_dir.mkdir(exist_ok=True)

# Route to serve the demo page
@app.route('/')
def index():
    """Serve the main demo page"""
    return render_template('cscsc_agent_demo.html')

@app.route('/api/v1/cscsc/status')
def get_status():
    return jsonify(demo_status)

@app.route('/api/v1/cscsc/results')
def get_results():
    return jsonify(demo_results)

@app.route('/api/v1/cscsc/forecast')
def run_forecast():
    """Generate a synthetic forecast with multiple scenarios and anomalies."""
    # Generate a date range for historical data (past 24 months)
    start_date = datetime.now() - timedelta(days=24*30)  # 24 months ago
    dates = [(start_date + timedelta(days=30*i)).strftime("%Y-%m-%d") for i in range(25)]  # 24 months + current
    
    # Generate synthetic historical values (with some realistic variability)
    hist_values = []
    base_value = 150000
    for i in range(len(dates)):
        # Add some seasonality and trend
        seasonal = 20000 * math.sin(i/4)
        trend = 10000 * i
        noise = random.randint(-15000, 15000)
        value = max(0, base_value + seasonal + trend + noise)
        hist_values.append(int(value))
    
    # Create historical data
    historical = [{'date': dates[i], 'value': hist_values[i]} for i in range(len(dates))]
    
    # Generate future dates (next 12 months)
    future_start = datetime.now() + timedelta(days=30)
    future_dates = [(future_start + timedelta(days=30*i)).strftime("%Y-%m-%d") for i in range(12)]
    
    # Create baseline forecast with different growth models
    last_value = hist_values[-1]
    forecast_values = []
    for i in range(len(future_dates)):
        # Baseline forecast - moderate growth with some seasonality
        seasonal = 25000 * math.sin((i+len(dates))/4)
        trend = 15000 * i
        value = last_value + trend + seasonal + random.randint(-10000, 10000)
        forecast_values.append(int(value))
    
    forecast = [{'date': future_dates[i], 'value': forecast_values[i]} for i in range(len(future_dates))]
    
    # Create upper bound (97.5% CI)
    upper_ci = 0.12  # 12% confidence interval
    upper_bound = [{'date': forecast[i]['date'], 'value': int(forecast[i]['value'] * (1 + upper_ci))} for i in range(len(forecast))]
    
    # Create lower bound (2.5% CI)
    lower_ci = 0.12
    lower_bound = [{'date': forecast[i]['date'], 'value': int(forecast[i]['value'] * (1 - lower_ci))} for i in range(len(forecast))]
    
    # Create optimistic scenario
    optimistic_factor = 1.15
    optimistic_scenario = {
        'name': 'Optimistic',
        'forecast': [{'date': forecast[i]['date'], 'value': int(forecast[i]['value'] * optimistic_factor)} for i in range(len(forecast))]
    }
    
    # Create pessimistic scenario
    pessimistic_factor = 0.85
    pessimistic_scenario = {
        'name': 'Pessimistic',
        'forecast': [{'date': forecast[i]['date'], 'value': int(forecast[i]['value'] * pessimistic_factor)} for i in range(len(forecast))]
    }
    
    # Identify anomalies in historical data
    anomalies = []
    # Add some synthetic anomalies
    anomalies.append({
        'date': dates[5],
        'value': hist_values[5],
        'type': 'negative',
        'description': 'Unexpected resource shortage'
    })
    anomalies.append({
        'date': dates[12],
        'value': hist_values[12],
        'type': 'positive',
        'description': 'Accelerated milestone completion'
    })
    anomalies.append({
        'date': dates[18],
        'value': hist_values[18],
        'type': 'negative',
        'description': 'Regulatory compliance delay'
    })
    
    # Add forecast metrics
    metrics = {
        'accuracy': 94.2,
        'confidence_interval': 12.0,
        'mape': 5.8,
        'mae': 32400
    }
    
    # Return the forecast data
    return jsonify({
        'historical': historical,
        'forecast': forecast,
        'upper_bound': upper_bound,
        'lower_bound': lower_bound,
        'scenarios': [optimistic_scenario, pessimistic_scenario],
        'anomaly_detection': {
            'anomalies': anomalies,
            'method': 'Seasonal Decomposition (STL)'
        },
        'model': {
            'type': 'Bayesian-ARIMA Hybrid',
            'parameters': {
                'p': 2,
                'd': 1,
                'q': 2,
                'bayes_inference': 'MCMC',
                'prior': 'Gaussian'
            }
        },
        'metrics': metrics
    })

@app.route('/api/v1/cscsc/sensitivity')
def run_sensitivity_analysis():
    """Generate synthetic sensitivity analysis with interdependency modeling."""
    
    # Create synthetic parameter data with elasticity values
    parameters = [
        {
            'name': 'Labor Productivity',
            'elasticity': 1.53,
            'baseline': '100%',
            'negative_impact': '-15.3% SPI',
            'positive_impact': '+8.7% SPI',
            'threshold': 'High',
            'interdependencies': ['Weather Days', 'Equipment Availability']
        },
        {
            'name': 'Material Costs',
            'elasticity': 0.72,
            'baseline': '$450,000',
            'negative_impact': '-7.2% CPI',
            'positive_impact': '+6.4% CPI',
            'threshold': 'Medium',
            'interdependencies': ['Permitting Time']
        },
        {
            'name': 'Weather Days',
            'elasticity': 1.18,
            'baseline': '12 days',
            'negative_impact': '-11.8% SPI',
            'positive_impact': '+4.1% SPI',
            'threshold': 'High',
            'interdependencies': ['Labor Productivity', 'Equipment Availability']
        },
        {
            'name': 'Permitting Time',
            'elasticity': 0.95,
            'baseline': '45 days',
            'negative_impact': '-9.5% SPI',
            'positive_impact': '+3.2% SPI',
            'threshold': 'Medium',
            'interdependencies': ['Material Costs']
        },
        {
            'name': 'Equipment Availability',
            'elasticity': 0.86,
            'baseline': '92%',
            'negative_impact': '-8.6% SPI',
            'positive_impact': '+2.3% SPI',
            'threshold': 'Medium',
            'interdependencies': ['Labor Productivity', 'Weather Days']
        }
    ]
    
    # Generate correlation matrix for the parameters
    param_names = [p['name'] for p in parameters]
    correlation_matrix = [
        [1.00, 0.12, 0.65, 0.08, 0.45],  # Labor Productivity
        [0.12, 1.00, 0.09, 0.58, 0.14],  # Material Costs
        [0.65, 0.09, 1.00, 0.22, 0.61],  # Weather Days
        [0.08, 0.58, 0.22, 1.00, 0.18],  # Permitting Time
        [0.45, 0.14, 0.61, 0.18, 1.00]   # Equipment Availability
    ]
    
    return jsonify({
        'parameters': parameters,
        'correlation_matrix': correlation_matrix,
        'key_finding': 'Labor productivity has the highest elasticity (1.53), making it the most sensitive parameter affecting project performance. A 10% increase in productivity yields an 8.7% improvement in SPI.'
    })

@app.route('/api/v1/cscsc/monte-carlo')
def run_monte_carlo_simulation():
    """Generate synthetic Monte Carlo simulation results with critical path analysis."""
    
    # Generate synthetic distribution data for completion dates
    base_date = datetime(2025, 8, 15)
    completion_distribution = []
    
    # Create a somewhat normal distribution with dates
    dates = [(base_date + timedelta(days=15*i - 60)).strftime("%b %d, %Y") for i in range(9)]
    frequencies = [3, 8, 14, 24, 31, 22, 12, 7, 2]
    
    for i in range(len(dates)):
        completion_distribution.append({
            'completion_date': dates[i],
            'frequency': frequencies[i],
            'cumulative_probability': sum(frequencies[:i+1]) / sum(frequencies) * 100
        })
    
    # Define key percentiles
    percentiles = {
        'p10': dates[1],  # 10th percentile
        'p50': dates[4],  # 50th percentile (median)
        'p90': dates[7]   # 90th percentile
    }
    
    # Generate S-curve data for progress over time
    start_date = datetime(2023, 6, 1)
    s_curve_dates = [(start_date + timedelta(days=30*i)).strftime("%Y-%m-%d") for i in range(24)]
    
    s_curve = []
    for i, date in enumerate(s_curve_dates):
        progress = min(100, (i / 23) * 100)
        
        # Add variability between percentiles
        p10 = min(100, progress * 1.15) if i > 0 else 0  # Optimistic
        p50 = progress                                   # Most likely
        p90 = max(0, progress * 0.85) if progress > 0 else 0  # Conservative
        
        s_curve.append({
            'date': date,
            'p10': round(p10, 1),
            'p50': round(p50, 1),
            'p90': round(p90, 1)
        })
    
    # Critical path activities
    critical_path = {
        'duration': 430,  # days
        'activities': [
            {
                'name': 'Site Preparation',
                'start_date': '2023-06-15',
                'end_date': '2023-08-30',
                'duration': 45,
                'risk_level': 'Low'
            },
            {
                'name': 'Foundation Work',
                'start_date': '2023-09-01',
                'end_date': '2023-10-31',
                'duration': 60,
                'risk_level': 'Medium'
            },
            {
                'name': 'Structural Framework',
                'start_date': '2023-11-01',
                'end_date': '2024-02-28',
                'duration': 90,
                'risk_level': 'High'
            },
            {
                'name': 'Enclosure & Roofing',
                'start_date': '2024-03-01',
                'end_date': '2024-05-31',
                'duration': 75,
                'risk_level': 'Medium'
            },
            {
                'name': 'Systems Integration',
                'start_date': '2024-06-01',
                'end_date': '2024-10-15',
                'duration': 105,
                'risk_level': 'High'
            },
            {
                'name': 'Interior Finishing',
                'start_date': '2024-10-16',
                'end_date': '2025-01-31',
                'duration': 80,
                'risk_level': 'Low'
            },
            {
                'name': 'Testing & Commissioning',
                'start_date': '2025-02-01',
                'end_date': '2025-04-15',
                'duration': 75,
                'risk_level': 'Medium'
            }
        ]
    }
    
    # Risk factors from regression tree analysis
    risk_factors = [
        {
            'factor': 'Supply Chain Disruption',
            'impact_score': 0.82,
            'probability': 0.68,
            'detection_difficulty': 'Medium'
        },
        {
            'factor': 'Labor Shortage',
            'impact_score': 0.78,
            'probability': 0.72,
            'detection_difficulty': 'High'
        },
        {
            'factor': 'Weather Events',
            'impact_score': 0.71,
            'probability': 0.55,
            'detection_difficulty': 'Low'
        },
        {
            'factor': 'Regulatory Compliance',
            'impact_score': 0.65,
            'probability': 0.60,
            'detection_difficulty': 'High'
        },
        {
            'factor': 'Quality Control Issues',
            'impact_score': 0.58,
            'probability': 0.45,
            'detection_difficulty': 'Medium'
        },
        {
            'factor': 'Design Changes',
            'impact_score': 0.52,
            'probability': 0.38,
            'detection_difficulty': 'Medium'
        },
        {
            'factor': 'Subcontractor Performance',
            'impact_score': 0.48,
            'probability': 0.50,
            'detection_difficulty': 'High'
        },
        {
            'factor': 'Budget Overruns',
            'impact_score': 0.45,
            'probability': 0.62,
            'detection_difficulty': 'Low'
        }
    ]
    
    return jsonify({
        'simulation_runs': 10000,
        'completion_distribution': completion_distribution,
        'percentiles': percentiles,
        's_curve': s_curve,
        'critical_path': critical_path,
        'risk_factors': risk_factors,
        'analysis_method': 'Multivariate Regression Tree',
        'confidence_level': 95
    })

def add_message(message, log_type='info'):
    """Add a message to the demo status"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    demo_status['messages'].append({
        'timestamp': timestamp,
        'message': message,
        'type': log_type
    })

def reset_demo():
    """Reset the demo state"""
    global demo_results, demo_status
    demo_results = {}
    demo_status = {
        'status': 'idle',
        'messages': []
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CSCSC Agent Advanced Features Demo')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()
    
    print(f"\n================================================================")
    print(f"CSCSC AI Agent Advanced Features Demo")
    print(f"Running at http://localhost:{args.port}")
    print(f"================================================================\n")
    
    app.run(debug=True, port=args.port)
