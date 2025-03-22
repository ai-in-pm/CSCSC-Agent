"""Primavera P6 Data Processor for CSCSC AI Agent.

This module processes data from Primavera P6 and converts it into
formats suitable for analysis and visualization by the CSCSC AI Agent.
"""

import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from .primavera_connector import PrimaveraConnector

class PrimaveraDataProcessor:
    """Process and transform Primavera P6 data for CSCSC AI Agent analysis."""
    
    def __init__(self, connector=None, p6_installation_path=None):
        """Initialize the data processor.
        
        Args:
            connector: PrimaveraConnector instance or None (will create default)
            p6_installation_path: Path to P6 installation
        """
        self.connector = connector or PrimaveraConnector()
        self.p6_path = p6_installation_path or r"C:\Program Files\Oracle\Primavera P6\P6 Professional\21.12.0"
        self.verify_p6_installation()
        
    def verify_p6_installation(self):
        """Verify P6 installation path and log important files."""
        p6_path = Path(self.p6_path)
        if not p6_path.exists():
            print(f"Warning: P6 installation path does not exist: {self.p6_path}")
            return
            
        print(f"Found P6 installation at: {self.p6_path}")
        
        # Look for key P6 files (SDK, executable, etc.)
        exe_path = p6_path / "PM.exe"
        if exe_path.exists():
            print(f"Found P6 executable: {exe_path}")
    
    def get_project_data(self, project_id=None):
        """Retrieve project data from P6 and process it for analysis.
        
        Args:
            project_id: Specific project ID or None for all projects
            
        Returns:
            Dictionary containing processed project data
        """
        # Get raw project data
        projects = self.connector.get_projects()
        
        if not projects:
            print("No projects found")
            return {}
            
        # Filter by project_id if specified
        if project_id:
            projects = [p for p in projects if p.get('proj_id') == project_id]
            
            if not projects:
                print(f"Project not found: {project_id}")
                return {}
        
        # Get activities for each project
        project_data = []
        for project in projects:
            activities = self.connector.get_activities(project['proj_id'])
            
            # Calculate project metrics
            metrics = self._calculate_project_metrics(project, activities)
            
            project_data.append({
                'project': project,
                'activities': activities,
                'metrics': metrics
            })
        
        return project_data
    
    def _calculate_project_metrics(self, project, activities):
        """Calculate important project metrics from raw P6 data."""
        metrics = {
            'activity_count': len(activities),
            'start_date': project.get('act_start_date') or project.get('target_start_date'),
            'end_date': project.get('act_end_date') or project.get('target_end_date'),
        }
        
        # Calculate progress if activities exist
        if activities:
            completed_activities = [a for a in activities if a.get('act_end_date')]
            metrics['progress'] = len(completed_activities) / len(activities) * 100
            
            # Calculate critical path activities (simplified)
            # In real implementation, would use Total Float = 0
            metrics['critical_path_count'] = int(len(activities) * 0.25)  # Estimate 25% activities on critical path
        
        return metrics
    
    def prepare_for_visualization(self, project_data):
        """Transform project data into format for CSCSC visualizations.
        
        Args:
            project_data: Project data from get_project_data
            
        Returns:
            Dictionary with visualization-ready data structures
        """
        if not project_data:
            return {}
            
        visualization_data = {
            'projects': [],
            'activities': [],
            'gantt_data': [],
            'resource_data': [],
            'progress_data': [],
        }
        
        for project in project_data:
            # Basic project info
            visualization_data['projects'].append({
                'id': project['project']['proj_id'],
                'name': project['project']['proj_name'],
                'start_date': project['metrics']['start_date'],
                'end_date': project['metrics']['end_date'],
                'progress': project['metrics'].get('progress', 0)
            })
            
            # Activity data
            for activity in project['activities']:
                visualization_data['activities'].append({
                    'id': activity['task_id'],
                    'project_id': project['project']['proj_id'],
                    'name': activity['task_name'],
                    'start_date': activity.get('act_start_date') or activity.get('target_start_date'),
                    'end_date': activity.get('act_end_date') or activity.get('target_end_date'),
                    'duration': activity.get('target_duration'),
                    'remaining_duration': activity.get('remain_duration'),
                    'completed': bool(activity.get('act_end_date'))
                })
            
            # Create Gantt data
            gantt_data = self._create_gantt_data(project)
            visualization_data['gantt_data'].append(gantt_data)
            
            # Create resource data (would require additional connector functions)
            # For now, create synthetic resource data
            resource_data = self._create_synthetic_resource_data(project)
            visualization_data['resource_data'].append(resource_data)
            
            # Create progress data over time
            progress_data = self._create_progress_data(project)
            visualization_data['progress_data'].append(progress_data)
        
        return visualization_data
    
    def _create_gantt_data(self, project):
        """Create Gantt chart data from project activities."""
        activities = project['activities']
        
        gantt_data = {
            'project_id': project['project']['proj_id'],
            'project_name': project['project']['proj_name'],
            'tasks': []
        }
        
        for activity in activities:
            # Parse dates - assuming ISO format strings
            start_date = activity.get('act_start_date') or activity.get('target_start_date')
            end_date = activity.get('act_end_date') or activity.get('target_end_date')
            
            # Skip activities without dates
            if not start_date or not end_date:
                continue
                
            # Convert string dates to datetime if needed
            if isinstance(start_date, str):
                try:
                    # Attempt to parse date string - format may vary
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                except ValueError:
                    # Fallback parsing
                    try:
                        start_date = datetime.strptime(start_date, '%Y-%m-%d')
                    except ValueError:
                        continue
                        
            if isinstance(end_date, str):
                try:
                    end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        end_date = datetime.strptime(end_date, '%Y-%m-%d')
                    except ValueError:
                        continue
            
            # Create task for Gantt
            task = {
                'id': activity['task_id'],
                'name': activity['task_name'],
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'progress': 100 if activity.get('act_end_date') else 0,  # Simplified
                'dependencies': []  # Would require relationship data from P6
            }
            
            gantt_data['tasks'].append(task)
        
        return gantt_data
    
    def _create_synthetic_resource_data(self, project):
        """Create synthetic resource data for visualization (placeholder)."""
        # In a real implementation, this would query P6 for actual resource assignments
        resource_types = ['Labor', 'Equipment', 'Material', 'Expenses']
        resource_data = {
            'project_id': project['project']['proj_id'],
            'project_name': project['project']['proj_name'],
            'resources': []
        }
        
        # Generate some synthetic resources
        for i in range(5):  # Create 5 synthetic resources
            resource_type = resource_types[i % len(resource_types)]
            resource_data['resources'].append({
                'id': f"R-{i+1}",
                'name': f"{resource_type} {i+1}",
                'type': resource_type,
                'planned_units': 100 + i * 20,
                'actual_units': (80 + i * 15) * (project['metrics'].get('progress', 50) / 100)
            })
        
        return resource_data
    
    def _create_progress_data(self, project):
        """Create progress data over time for S-curves."""
        # In a real implementation, this would use actual progress data points
        
        # Estimate project duration in days
        start_date_str = project['metrics']['start_date']
        end_date_str = project['metrics']['end_date']
        
        if not start_date_str or not end_date_str:
            # Create synthetic timeline if dates missing
            start_date = datetime.now() - timedelta(days=90)  # 3 months ago
            end_date = datetime.now() + timedelta(days=90)    # 3 months from now
        else:
            # Parse dates from strings
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                except (ValueError, AttributeError):
                    start_date = datetime.now() - timedelta(days=90)
                    
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                except (ValueError, AttributeError):
                    end_date = datetime.now() + timedelta(days=90)
        
        # Create date range with monthly intervals
        duration_days = (end_date - start_date).days
        num_points = max(6, duration_days // 30)  # At least 6 points, or one per month
        
        date_points = [start_date + timedelta(days=duration_days * i / (num_points-1)) for i in range(num_points)]
        
        # Create synthetic progress curve (S-curve shape)
        progress_curve = []
        for i, date in enumerate(date_points):
            # Create S-curve using sine function transformed to 0-100 range
            x = i / (num_points - 1)  # Normalize to 0-1
            # S-curve approximation
            if x < 0.5:
                progress = 100 * (x * x) * 2
            else:
                progress = 100 * (1 - (1-x) * (1-x) * 2)
                
            # Add some variance
            progress = min(100, max(0, progress + np.random.normal(0, 5)))
            
            # For dates in the past, use "actual" progress
            if date <= datetime.now():
                progress_curve.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'planned': progress,
                    'actual': min(100, max(0, progress + np.random.normal(0, 10))),
                    'is_actual': True
                })
            else:
                # For future dates, only include planned
                progress_curve.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'planned': progress,
                    'is_actual': False
                })
        
        progress_data = {
            'project_id': project['project']['proj_id'],
            'project_name': project['project']['proj_name'],
            'progress_curve': progress_curve
        }
        
        return progress_data
    
    def export_to_json(self, data, output_path):
        """Export data to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data exported to {output_path}")
        
    def export_to_csv(self, data, output_dir):
        """Export data to CSV files in the specified directory."""
        output_dir = Path(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        # Export projects
        if 'projects' in data and data['projects']:
            df_projects = pd.DataFrame(data['projects'])
            df_projects.to_csv(output_dir / 'projects.csv', index=False)
            
        # Export activities
        if 'activities' in data and data['activities']:
            df_activities = pd.DataFrame(data['activities'])
            df_activities.to_csv(output_dir / 'activities.csv', index=False)
        
        print(f"Data exported to CSV files in {output_dir}")
