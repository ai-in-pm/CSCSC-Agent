"""Route handlers for the CSCSC AI Agent user interface."""

from flask import Blueprint, render_template, jsonify, request
import os

# Create blueprint for UI routes
ui_routes = Blueprint('ui_routes', __name__)

@ui_routes.route('/')
def index():
    """Render the main page of the CSCSC AI Agent."""
    return render_template('index.html')

@ui_routes.route('/demo')
def demo():
    """Render the demo page of the CSCSC AI Agent."""
    return render_template('demo.html')

@ui_routes.route('/demo/cscsc-agent')
def cscsc_agent_demo():
    """Render the CSCSC Agent Demo page."""
    return render_template('cscsc_agent_demo.html')

@ui_routes.route('/primavera')
def primavera_integration():
    """Render the Primavera P6 integration page."""
    return render_template('primavera_integration.html')

@ui_routes.route('/mpxj')
def mpxj_conversion():
    """Render the MPXJ project file conversion page."""
    return render_template('mpxj_conversion.html')

@ui_routes.route('/api/system-info')
def system_info():
    """Return system information."""
    return jsonify({
        'version': '0.9.5',
        'name': 'CSCSC AI Agent',
        'environment': os.environ.get('FLASK_ENV', 'production')
    })
