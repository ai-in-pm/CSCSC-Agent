from typing import Dict, List, Any, Optional
import os
import json
from datetime import datetime, timedelta
import logging

# Note: In a production application, these would be replaced with actual plotting libraries
# like matplotlib, plotly, or bokeh. For this prototype, we'll create JSON structures
# that could be consumed by a frontend visualization library.

logger = logging.getLogger(__name__)

class EVMVisualizer:
    """Class to generate visualization data for EVM metrics and physical project aspects."""
    
    def __init__(self):
        """Initialize the EVM Visualizer."""
        logger.info("Initializing EVM Visualizer")
    
    def generate_physical_progress_chart(self, project_id: str, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate data for a chart comparing physical vs. reported progress over time.
        
        Args:
            project_id: ID of the project
            metrics: List of physical progress metrics data points
            
        Returns:
            Dict containing chart data
        """
        logger.info(f"Generating physical progress chart for project {project_id}")
        
        # Sort metrics by date
        sorted_metrics = sorted(metrics, key=lambda x: x.get('date', datetime.min))
        
        # Extract data points
        dates = [m.get('date').strftime('%Y-%m-%d') for m in sorted_metrics if 'date' in m]
        physical_progress = [m.get('physical_percent_complete', 0.0) * 100 for m in sorted_metrics]
        reported_progress = [m.get('reported_percent_complete', 0.0) * 100 for m in sorted_metrics]
        variance = [m.get('variance_percentage', 0.0) for m in sorted_metrics]
        
        chart_data = {
            "project_id": project_id,
            "chart_type": "line",
            "title": "Physical vs. Reported Progress",
            "x_axis": {
                "title": "Date",
                "values": dates
            },
            "y_axis": {
                "title": "Percent Complete",
                "format": "{value}%"
            },
            "series": [
                {
                    "name": "Physical Progress",
                    "data": physical_progress,
                    "color": "#4285F4"
                },
                {
                    "name": "Reported Progress",
                    "data": reported_progress,
                    "color": "#EA4335"
                }
            ],
            "annotations": []
        }
        
        # Add annotations for significant variances
        for i, var in enumerate(variance):
            if abs(var) > 10:  # Only annotate significant variances
                chart_data["annotations"].append({
                    "x": dates[i],
                    "y": max(physical_progress[i], reported_progress[i]),
                    "text": f"{var:.1f}% variance",
                    "color": "#FF5722" if var < 0 else "#4CAF50"
                })
        
        return chart_data
    
    def generate_environmental_impact_heatmap(self, project_id: str, impact_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate data for a heatmap showing environmental impacts on project WBS elements.
        
        Args:
            project_id: ID of the project
            impact_data: List of environmental impact data points
            
        Returns:
            Dict containing heatmap data
        """
        logger.info(f"Generating environmental impact heatmap for project {project_id}")
        
        # Collect all unique WBS elements and environmental factors
        wbs_elements = set()
        factors = set()
        
        for impact in impact_data:
            factor_type = impact.get("factor_type", "unknown")
            factors.add(factor_type)
            
            affected_wbs = impact.get("affected_wbs_elements", [])
            for wbs in affected_wbs:
                wbs_elements.add(wbs)
        
        # Create a grid of impact values
        wbs_list = sorted(list(wbs_elements))
        factor_list = sorted(list(factors))
        
        # Initialize grid with zeros
        impact_grid = []
        for wbs in wbs_list:
            row = []
            for factor in factor_list:
                # Find the maximum impact value for this WBS and factor
                max_impact = 0
                for impact in impact_data:
                    if (impact.get("factor_type") == factor and 
                        wbs in impact.get("affected_wbs_elements", [])):
                        # Calculate impact value based on severity and duration
                        severity_value = {
                            "low": 1,
                            "medium": 2,
                            "high": 3,
                            "critical": 4
                        }.get(impact.get("severity", "low"), 1)
                        
                        duration = impact.get("duration_days", 1)
                        impact_value = severity_value * min(duration / 5, 2)
                        max_impact = max(max_impact, impact_value)
                
                row.append(max_impact)
            impact_grid.append(row)
        
        heatmap_data = {
            "project_id": project_id,
            "chart_type": "heatmap",
            "title": "Environmental Impact by WBS Element",
            "x_axis": {
                "title": "Environmental Factor",
                "categories": factor_list
            },
            "y_axis": {
                "title": "WBS Element",
                "categories": wbs_list
            },
            "color_scale": [
                [0, "#FFFFFF"],  # No impact
                [0.25, "#FFEB3B"],  # Low impact
                [0.5, "#FF9800"],  # Medium impact
                [0.75, "#F44336"],  # High impact
                [1, "#9C27B0"]  # Critical impact
            ],
            "data": []
        }
        
        # Format data for heatmap
        for i, wbs in enumerate(wbs_list):
            for j, factor in enumerate(factor_list):
                heatmap_data["data"].append({
                    "x": j,
                    "y": i,
                    "value": impact_grid[i][j],
                    "wbs": wbs,
                    "factor": factor
                })
        
        return heatmap_data
    
    def generate_risk_matrix(self, project_id: str, risk_elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate data for a risk matrix visualization.
        
        Args:
            project_id: ID of the project
            risk_elements: List of risk assessment data
            
        Returns:
            Dict containing risk matrix data
        """
        logger.info(f"Generating risk matrix for project {project_id}")
        
        matrix_data = {
            "project_id": project_id,
            "chart_type": "scatter",
            "title": "Project Risk Matrix",
            "x_axis": {
                "title": "Likelihood",
                "min": 0,
                "max": 1,
                "tickPositions": [0, 0.25, 0.5, 0.75, 1],
                "labels": ["Very Low", "Low", "Medium", "High", "Very High"]
            },
            "y_axis": {
                "title": "Impact",
                "min": 0,
                "max": 1,
                "tickPositions": [0, 0.25, 0.5, 0.75, 1],
                "labels": ["Minimal", "Minor", "Moderate", "Major", "Severe"]
            },
            "zones": [
                {"value": 0.25, "color": "#4CAF50"},  # Low risk zone
                {"value": 0.5, "color": "#FFEB3B"},   # Medium risk zone
                {"value": 0.75, "color": "#FF9800"},  # High risk zone
                {"value": 1, "color": "#F44336"}     # Critical risk zone
            ],
            "data": []
        }
        
        # Add risk elements to the matrix
        for risk in risk_elements:
            likelihood = risk.get("likelihood", 0.5)
            impact = risk.get("impact", 0.5)
            risk_factor = risk.get("risk_factor", "other")
            wbs = risk.get("wbs_element", "")
            description = risk.get("description", "")
            
            # Calculate point size based on risk score
            risk_score = likelihood * impact
            point_size = 5 + (risk_score * 15)  # Size between 5 and 20
            
            matrix_data["data"].append({
                "x": likelihood,
                "y": impact,
                "name": f"WBS {wbs}",
                "description": description,
                "risk_factor": risk_factor,
                "risk_score": risk_score,
                "marker": {
                    "radius": point_size,
                    "symbol": "circle"
                }
            })
        
        return matrix_data
    
    def generate_resource_productivity_chart(self, project_id: str, productivity_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate data for a resource productivity chart.
        
        Args:
            project_id: ID of the project
            productivity_data: List of resource productivity data points
            
        Returns:
            Dict containing chart data
        """
        logger.info(f"Generating resource productivity chart for project {project_id}")
        
        # Group resources by type
        resource_types = {}
        for resource in productivity_data:
            resource_type = resource.get("resource_type", "other")
            if resource_type not in resource_types:
                resource_types[resource_type] = []
            resource_types[resource_type].append(resource)
        
        chart_data = {
            "project_id": project_id,
            "chart_type": "column",
            "title": "Resource Productivity Index",
            "subtitle": "Actual vs. Planned Productivity",
            "x_axis": {
                "title": "Resource",
                "categories": []
            },
            "y_axis": {
                "title": "Productivity Index",
                "min": 0,
                "plotLines": [{"value": 1, "color": "#000000", "width": 2, "dashStyle": "dash"}]
            },
            "series": [],
            "resource_types": list(resource_types.keys())
        }
        
        # Process all resources
        all_resources = []
        for resource_type, resources in resource_types.items():
            # Sort by productivity index
            sorted_resources = sorted(resources, key=lambda x: x.get("productivity_index", 0))
            all_resources.extend(sorted_resources)
        
        # Build chart data
        chart_data["x_axis"]["categories"] = [r.get("resource_name", "") for r in all_resources]
        
        # Create series for productivity index
        productivity_data = []
        colors = []
        
        for resource in all_resources:
            index = resource.get("productivity_index", 1.0)
            productivity_data.append(index)
            
            # Color coding based on productivity index
            if index < 0.8:
                colors.append("#F44336")  # Significantly under-performing
            elif index < 0.95:
                colors.append("#FF9800")  # Slightly under-performing
            elif index <= 1.05:
                colors.append("#4CAF50")  # On target
            elif index <= 1.2:
                colors.append("#2196F3")  # Slightly over-performing
            else:
                colors.append("#673AB7")  # Significantly over-performing
        
        chart_data["series"].append({
            "name": "Productivity Index",
            "data": productivity_data,
            "colors": colors
        })
        
        # Add target line
        chart_data["target_line"] = 1.0
        
        return chart_data
    
    def generate_site_conditions_dashboard(self, project_id: str, site_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for a site conditions dashboard.
        
        Args:
            project_id: ID of the project
            site_conditions: Site conditions data
            
        Returns:
            Dict containing dashboard data
        """
        logger.info(f"Generating site conditions dashboard for project {project_id}")
        
        # Extract weather information
        weather = site_conditions.get("weather", {})
        current = weather.get("current", {})
        forecast = weather.get("forecast", [])
        alerts = weather.get("weather_alerts", [])
        
        # Extract site access information
        site_access = site_conditions.get("site_access", {})
        
        # Extract IoT sensor data
        iot_sensors = site_conditions.get("iot_sensors", {})
        
        dashboard_data = {
            "project_id": project_id,
            "dashboard_type": "site_conditions",
            "title": "Site Conditions Dashboard",
            "scan_date": site_conditions.get("scan_date", datetime.now()).strftime("%Y-%m-%d %H:%M"),
            "panels": [
                {
                    "title": "Current Weather",
                    "type": "weather",
                    "data": {
                        "temperature": current.get("temperature", 0),
                        "conditions": current.get("conditions", "Unknown"),
                        "precipitation": current.get("precipitation", 0),
                        "wind_speed": current.get("wind_speed", 0),
                        "humidity": current.get("humidity", 0),
                        "icon": self._get_weather_icon(current.get("conditions", "Unknown"))
                    }
                },
                {
                    "title": "Weather Forecast",
                    "type": "forecast",
                    "data": [{
                        "date": f.get("date").strftime("%Y-%m-%d") if isinstance(f.get("date"), datetime) else f.get("date"),
                        "conditions": f.get("conditions", "Unknown"),
                        "high_temp": f.get("high_temp", 0),
                        "low_temp": f.get("low_temp", 0),
                        "precipitation_chance": f.get("precipitation_chance", 0),
                        "work_impact": f.get("work_impact", "low"),
                        "icon": self._get_weather_icon(f.get("conditions", "Unknown"))
                    } for f in forecast]
                },
                {
                    "title": "Weather Alerts",
                    "type": "alerts",
                    "data": alerts
                },
                {
                    "title": "Site Access",
                    "type": "site_access",
                    "data": {
                        "status": site_access.get("status", "unknown"),
                        "restrictions": site_access.get("restrictions", []),
                        "delivery_access": site_access.get("delivery_access", "unknown")
                    }
                }
            ]
        }
        
        # Add IoT sensor panels
        for sensor_type, sensors in iot_sensors.items():
            dashboard_data["panels"].append({
                "title": f"{sensor_type.replace('_', ' ').title()}",
                "type": "sensors",
                "sensor_type": sensor_type,
                "data": sensors
            })
        
        return dashboard_data
    
    def _get_weather_icon(self, conditions: str) -> str:
        """Get a weather icon name based on conditions.
        
        Args:
            conditions: Weather conditions description
            
        Returns:
            str: Icon name
        """
        conditions_lower = conditions.lower()
        
        if "rain" in conditions_lower:
            return "rain"
        elif "snow" in conditions_lower or "flurries" in conditions_lower:
            return "snow"
        elif "cloud" in conditions_lower:
            if "partly" in conditions_lower:
                return "partly_cloudy"
            else:
                return "cloudy"
        elif "sun" in conditions_lower or "clear" in conditions_lower:
            return "sunny"
        elif "storm" in conditions_lower or "thunder" in conditions_lower:
            return "storm"
        elif "fog" in conditions_lower or "hazy" in conditions_lower:
            return "fog"
        elif "wind" in conditions_lower:
            return "windy"
        else:
            return "unknown"
