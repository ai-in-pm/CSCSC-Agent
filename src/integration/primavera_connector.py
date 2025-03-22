"""Primavera P6 Connector Module for CSCSC AI Agent.

This module provides functionality to connect to Primavera P6,
extract data, and query project information.
"""

import os
import json
import pandas as pd
import pyodbc
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

class PrimaveraConnector:
    """Connector class for Primavera P6 integration with CSCSC AI Agent."""
    
    def __init__(self, connection_type='api', config_path=None):
        """Initialize the Primavera connector.
        
        Args:
            connection_type (str): Type of connection - 'api', 'database', or 'file'
            config_path (str): Path to configuration file
        """
        self.connection_type = connection_type
        self.connection = None
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path):
        """Load configuration from file."""
        if not config_path:
            # Default to config in same directory
            config_path = Path(__file__).parent / 'primavera_config.json'
            
        if not config_path.exists():
            # Create default config if not exists
            default_config = {
                'api': {
                    'base_url': 'http://localhost:8203/p6api',
                    'username': '',
                    'password': '',
                    'auth_type': 'basic'
                },
                'database': {
                    'driver': '{Oracle in OraClient12Home1}',
                    'server': 'localhost',
                    'database': 'pmdb',
                    'username': '',
                    'password': '',
                    'port': 1521
                },
                'file': {
                    'import_dir': './imports',
                    'export_dir': './exports'
                }
            }
            
            os.makedirs(config_path.parent, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
                
            return default_config
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def connect(self):
        """Establish connection to Primavera P6 based on connection type."""
        if self.connection_type == 'api':
            return self._connect_api()
        elif self.connection_type == 'database':
            return self._connect_database()
        elif self.connection_type == 'file':
            # File-based doesn't need persistent connection
            return True
        else:
            raise ValueError(f"Unsupported connection type: {self.connection_type}")
    
    def _connect_api(self):
        """Connect to Primavera P6 via REST API."""
        api_config = self.config['api']
        base_url = api_config['base_url']
        
        # Test connection with authentication
        try:
            response = requests.get(
                f"{base_url}/session",
                auth=(api_config['username'], api_config['password'])
            )
            
            if response.status_code == 200:
                self.connection = {'session': response.cookies, 'base_url': base_url}
                return True
            else:
                print(f"API connection failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"API connection error: {str(e)}")
            return False
    
    def _connect_database(self):
        """Connect to Primavera P6 database directly."""
        db_config = self.config['database']
        
        connection_string = (
            f"DRIVER={db_config['driver']};"
            f"SERVER={db_config['server']};"
            f"DATABASE={db_config['database']};"
            f"UID={db_config['username']};"
            f"PWD={db_config['password']};"
            f"PORT={db_config['port']}"
        )
        
        try:
            self.connection = pyodbc.connect(connection_string)
            return True
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            return False
    
    def disconnect(self):
        """Close the connection to Primavera P6."""
        if self.connection_type == 'database' and self.connection:
            self.connection.close()
        self.connection = None
    
    def get_projects(self):
        """Retrieve list of projects from Primavera P6."""
        if self.connection_type == 'api':
            return self._get_projects_api()
        elif self.connection_type == 'database':
            return self._get_projects_database()
        elif self.connection_type == 'file':
            return self._get_projects_file()
    
    def _get_projects_api(self):
        """Get projects using REST API."""
        if not self.connection:
            if not self.connect():
                return []
        
        base_url = self.connection['base_url']
        try:
            response = requests.get(
                f"{base_url}/projects",
                cookies=self.connection['session']
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error retrieving projects: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"API request error: {str(e)}")
            return []
    
    def _get_projects_database(self):
        """Get projects from direct database connection."""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """SELECT proj_id, proj_name, proj_short_name, last_update_date, 
                         target_start_date, target_end_date, act_start_date, act_end_date
                  FROM projwbs 
                  WHERE parent_wbs_id IS NULL"""
            )
            
            columns = [column[0] for column in cursor.description]
            projects = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return projects
        except Exception as e:
            print(f"Database query error: {str(e)}")
            return []
    
    def _get_projects_file(self):
        """Get projects from XER/XML file."""
        # This would parse the most recent XER or XML file in the import directory
        import_dir = Path(self.config['file']['import_dir'])
        if not import_dir.exists():
            print(f"Import directory does not exist: {import_dir}")
            return []
        
        # Find most recent XER or XML file
        files = list(import_dir.glob("*.xer")) + list(import_dir.glob("*.xml"))
        if not files:
            print("No XER or XML files found in import directory")
            return []
        
        latest_file = max(files, key=lambda p: p.stat().st_mtime)
        
        if latest_file.suffix.lower() == '.xer':
            return self._parse_xer_file(latest_file)
        else:  # .xml
            return self._parse_xml_file(latest_file)
    
    def _parse_xer_file(self, file_path):
        """Parse projects from XER file."""
        projects = []
        
        try:
            with open(file_path, 'r') as f:
                current_table = None
                headers = []
                
                for line in f:
                    line = line.strip()
                    if line.startswith('%T'):
                        current_table = line[3:]
                        headers = []
                    elif line.startswith('%F') and current_table:
                        headers = line[3:].split('\t')
                    elif current_table == 'PROJECT' and headers and not line.startswith('%'):
                        values = line.split('\t')
                        project_data = dict(zip(headers, values))
                        projects.append({
                            'proj_id': project_data.get('proj_id', ''),
                            'proj_name': project_data.get('proj_name', ''),
                            'proj_short_name': project_data.get('proj_short_name', ''),
                            'target_start_date': project_data.get('target_start_date', ''),
                            'target_end_date': project_data.get('target_end_date', ''),
                            'act_start_date': project_data.get('act_start_date', ''),
                            'act_end_date': project_data.get('act_end_date', '')
                        })
            
            return projects
        except Exception as e:
            print(f"Error parsing XER file: {str(e)}")
            return []
    
    def _parse_xml_file(self, file_path):
        """Parse projects from XML file."""
        projects = []
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for project in root.findall('.//Project'):
                projects.append({
                    'proj_id': project.get('ID', ''),
                    'proj_name': project.get('Name', ''),
                    'proj_short_name': project.get('ShortName', ''),
                    'target_start_date': project.get('PlannedStartDate', ''),
                    'target_end_date': project.get('PlannedFinishDate', ''),
                    'act_start_date': project.get('ActualStartDate', ''),
                    'act_end_date': project.get('ActualFinishDate', '')
                })
            
            return projects
        except Exception as e:
            print(f"Error parsing XML file: {str(e)}")
            return []
    
    def get_activities(self, project_id):
        """Retrieve activities for a specific project."""
        if self.connection_type == 'api':
            return self._get_activities_api(project_id)
        elif self.connection_type == 'database':
            return self._get_activities_database(project_id)
        elif self.connection_type == 'file':
            return self._get_activities_file(project_id)
    
    def _get_activities_api(self, project_id):
        """Get activities using REST API."""
        if not self.connection:
            if not self.connect():
                return []
        
        base_url = self.connection['base_url']
        try:
            response = requests.get(
                f"{base_url}/projects/{project_id}/activities",
                cookies=self.connection['session']
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error retrieving activities: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"API request error: {str(e)}")
            return []
    
    def _get_activities_database(self, project_id):
        """Get activities from direct database connection."""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """SELECT task_id, task_code, task_name, target_start_date, target_end_date, 
                         act_start_date, act_end_date, target_drtn_hr_cnt, remain_drtn_hr_cnt
                  FROM task
                  WHERE proj_id = ?""",
                (project_id,)
            )
            
            columns = [column[0] for column in cursor.description]
            activities = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return activities
        except Exception as e:
            print(f"Database query error: {str(e)}")
            return []
    
    def _get_activities_file(self, project_id):
        """Get activities from XER/XML file for a specific project."""
        import_dir = Path(self.config['file']['import_dir'])
        if not import_dir.exists():
            print(f"Import directory does not exist: {import_dir}")
            return []
        
        # Find most recent XER or XML file
        files = list(import_dir.glob("*.xer")) + list(import_dir.glob("*.xml"))
        if not files:
            print("No XER or XML files found in import directory")
            return []
        
        latest_file = max(files, key=lambda p: p.stat().st_mtime)
        
        if latest_file.suffix.lower() == '.xer':
            return self._parse_xer_activities(latest_file, project_id)
        else:  # .xml
            return self._parse_xml_activities(latest_file, project_id)
    
    def _parse_xer_activities(self, file_path, project_id):
        """Parse activities from XER file for a specific project."""
        activities = []
        
        try:
            with open(file_path, 'r') as f:
                current_table = None
                headers = []
                
                for line in f:
                    line = line.strip()
                    if line.startswith('%T'):
                        current_table = line[3:]
                        headers = []
                    elif line.startswith('%F') and current_table:
                        headers = line[3:].split('\t')
                    elif current_table == 'TASK' and headers and not line.startswith('%'):
                        values = line.split('\t')
                        activity_data = dict(zip(headers, values))
                        
                        # Check if activity belongs to the specified project
                        if activity_data.get('proj_id') == project_id:
                            activities.append({
                                'task_id': activity_data.get('task_id', ''),
                                'task_code': activity_data.get('task_code', ''),
                                'task_name': activity_data.get('task_name', ''),
                                'target_start_date': activity_data.get('target_start_date', ''),
                                'target_end_date': activity_data.get('target_end_date', ''),
                                'act_start_date': activity_data.get('act_start_date', ''),
                                'act_end_date': activity_data.get('act_end_date', ''),
                                'target_duration': activity_data.get('target_drtn_hr_cnt', ''),
                                'remain_duration': activity_data.get('remain_drtn_hr_cnt', '')
                            })
            
            return activities
        except Exception as e:
            print(f"Error parsing XER activities: {str(e)}")
            return []
    
    def _parse_xml_activities(self, file_path, project_id):
        """Parse activities from XML file for a specific project."""
        activities = []
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Find the specified project
            project = root.find(f".//Project[@ID='{project_id}']")
            if project is None:
                return []
            
            # Get activities for the project
            for activity in project.findall('./Activity'):
                activities.append({
                    'task_id': activity.get('ID', ''),
                    'task_code': activity.get('Code', ''),
                    'task_name': activity.get('Name', ''),
                    'target_start_date': activity.get('PlannedStartDate', ''),
                    'target_end_date': activity.get('PlannedFinishDate', ''),
                    'act_start_date': activity.get('ActualStartDate', ''),
                    'act_end_date': activity.get('ActualFinishDate', ''),
                    'target_duration': activity.get('PlannedDuration', ''),
                    'remain_duration': activity.get('RemainingDuration', '')
                })
            
            return activities
        except Exception as e:
            print(f"Error parsing XML activities: {str(e)}")
            return []
    
    def export_to_dataframe(self, data):
        """Convert data to pandas DataFrame for analysis."""
        return pd.DataFrame(data)
    
    def run_query(self, query, params=None):
        """Run a custom query against the Primavera database.
        
        Only works with 'database' connection type.
        """
        if self.connection_type != 'database':
            raise ValueError("Custom queries only supported with database connection type")
        
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return results
        except Exception as e:
            print(f"Query execution error: {str(e)}")
            return []
