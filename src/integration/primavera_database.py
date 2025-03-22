"""Primavera P6 Database Module for CSCSC AI Agent.

This module provides functionality to store Primavera P6 data in a local SQLite database,
facilitating efficient querying, analysis, and reporting on project data.
"""

import os
import json
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

class PrimaveraDatabase:
    """Database manager for Primavera P6 data integration with CSCSC AI Agent."""
    
    def __init__(self, db_path=None):
        """Initialize the Primavera database.
        
        Args:
            db_path (str): Path to database file
        """
        if db_path is None:
            # Use a default path in the integration directory
            self.db_path = Path(__file__).parent / 'primavera_integration.db'
        else:
            self.db_path = Path(db_path)
            
        # Ensure parent directory exists
        os.makedirs(self.db_path.parent, exist_ok=True)
        
        self.connection = None
        self.initialize_database()
    
    def initialize_database(self):
        """Create database tables if they don't exist."""
        self.connect()
        
        cursor = self.connection.cursor()
        
        # Create projects table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            proj_id TEXT PRIMARY KEY,
            proj_name TEXT,
            proj_short_name TEXT,
            target_start_date TEXT,
            target_end_date TEXT,
            act_start_date TEXT,
            act_end_date TEXT,
            progress REAL,
            last_updated TEXT,
            metadata TEXT
        )
        """)
        
        # Create activities table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            task_id TEXT PRIMARY KEY,
            proj_id TEXT,
            task_code TEXT,
            task_name TEXT,
            target_start_date TEXT,
            target_end_date TEXT,
            act_start_date TEXT,
            act_end_date TEXT,
            target_duration REAL,
            remain_duration REAL,
            progress REAL,
            metadata TEXT,
            FOREIGN KEY (proj_id) REFERENCES projects (proj_id)
        )
        """)
        
        # Create resources table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            resource_id TEXT PRIMARY KEY,
            resource_name TEXT,
            resource_type TEXT,
            metadata TEXT
        )
        """)
        
        # Create resource assignments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resource_assignments (
            assignment_id TEXT PRIMARY KEY,
            task_id TEXT,
            resource_id TEXT,
            planned_units REAL,
            actual_units REAL,
            remain_units REAL,
            metadata TEXT,
            FOREIGN KEY (task_id) REFERENCES activities (task_id),
            FOREIGN KEY (resource_id) REFERENCES resources (resource_id)
        )
        """)
        
        # Create relationships table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS relationships (
            rel_id TEXT PRIMARY KEY,
            pred_task_id TEXT,
            succ_task_id TEXT, 
            rel_type TEXT,
            lag REAL,
            metadata TEXT,
            FOREIGN KEY (pred_task_id) REFERENCES activities (task_id),
            FOREIGN KEY (succ_task_id) REFERENCES activities (task_id)
        )
        """)
        
        # Create import_log table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS import_log (
            import_id INTEGER PRIMARY KEY AUTOINCREMENT,
            import_date TEXT,
            import_type TEXT,
            source TEXT,
            status TEXT,
            message TEXT,
            metadata TEXT
        )
        """)
        
        # Create ai_analysis table to store AI analysis results
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_analysis (
            analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            proj_id TEXT,
            analysis_date TEXT,
            analysis_type TEXT,
            results TEXT,
            visualization_data TEXT,
            FOREIGN KEY (proj_id) REFERENCES projects (proj_id)
        )
        """)
        
        self.connection.commit()
        self.disconnect()
    
    def connect(self):
        """Establish database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            # Enable foreign key support
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Return dictionary-like rows
            self.connection.row_factory = sqlite3.Row
            
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def store_projects(self, projects):
        """Store project data in the database.
        
        Args:
            projects (list): List of project dictionaries
        
        Returns:
            int: Number of projects stored
        """
        if not projects:
            return 0
            
        self.connect()
        cursor = self.connection.cursor()
        
        count = 0
        for project in projects:
            # Extract core fields
            proj_id = project.get('proj_id')
            if not proj_id:
                continue  # Skip projects without ID
                
            # Check if project exists
            cursor.execute("SELECT 1 FROM projects WHERE proj_id = ?", (proj_id,))
            exists = cursor.fetchone() is not None
            
            # Prepare data
            project_data = {
                'proj_id': proj_id,
                'proj_name': project.get('proj_name', ''),
                'proj_short_name': project.get('proj_short_name', ''),
                'target_start_date': project.get('target_start_date', ''),
                'target_end_date': project.get('target_end_date', ''),
                'act_start_date': project.get('act_start_date', ''),
                'act_end_date': project.get('act_end_date', ''),
                'progress': project.get('progress', 0),
                'last_updated': datetime.now().isoformat()
            }
            
            # Store additional fields as JSON in metadata
            metadata = {k: v for k, v in project.items() if k not in project_data}
            project_data['metadata'] = json.dumps(metadata) if metadata else None
            
            if exists:
                # Update existing project
                placeholders = ', '.join([f"{k} = ?" for k in project_data.keys()])
                values = list(project_data.values())
                cursor.execute(
                    f"UPDATE projects SET {placeholders} WHERE proj_id = ?",
                    values + [proj_id]
                )
            else:
                # Insert new project
                placeholders = ', '.join(['?'] * len(project_data))
                columns = ', '.join(project_data.keys())
                cursor.execute(
                    f"INSERT INTO projects ({columns}) VALUES ({placeholders})",
                    list(project_data.values())
                )
            
            count += 1
        
        self.connection.commit()
        self.disconnect()
        return count
    
    def store_activities(self, activities):
        """Store activity data in the database.
        
        Args:
            activities (list): List of activity dictionaries
        
        Returns:
            int: Number of activities stored
        """
        if not activities:
            return 0
            
        self.connect()
        cursor = self.connection.cursor()
        
        count = 0
        for activity in activities:
            # Extract core fields
            task_id = activity.get('task_id')
            if not task_id:
                continue  # Skip activities without ID
                
            # Check if activity exists
            cursor.execute("SELECT 1 FROM activities WHERE task_id = ?", (task_id,))
            exists = cursor.fetchone() is not None
            
            # Prepare data
            activity_data = {
                'task_id': task_id,
                'proj_id': activity.get('proj_id', ''),
                'task_code': activity.get('task_code', ''),
                'task_name': activity.get('task_name', ''),
                'target_start_date': activity.get('target_start_date', ''),
                'target_end_date': activity.get('target_end_date', ''),
                'act_start_date': activity.get('act_start_date', ''),
                'act_end_date': activity.get('act_end_date', ''),
                'target_duration': activity.get('target_duration', 0),
                'remain_duration': activity.get('remain_duration', 0),
                'progress': activity.get('progress', 0)
            }
            
            # Store additional fields as JSON in metadata
            metadata = {k: v for k, v in activity.items() if k not in activity_data}
            activity_data['metadata'] = json.dumps(metadata) if metadata else None
            
            if exists:
                # Update existing activity
                placeholders = ', '.join([f"{k} = ?" for k in activity_data.keys()])
                values = list(activity_data.values())
                cursor.execute(
                    f"UPDATE activities SET {placeholders} WHERE task_id = ?",
                    values + [task_id]
                )
            else:
                # Insert new activity
                placeholders = ', '.join(['?'] * len(activity_data))
                columns = ', '.join(activity_data.keys())
                cursor.execute(
                    f"INSERT INTO activities ({columns}) VALUES ({placeholders})",
                    list(activity_data.values())
                )
            
            count += 1
        
        self.connection.commit()
        self.disconnect()
        return count
        
    def store_import_log(self, import_type, source, status, message=None, metadata=None):
        """Log an import operation.
        
        Args:
            import_type (str): Type of import (API, database, file)
            source (str): Source of the data
            status (str): Status of the import (success, error)
            message (str): Additional message
            metadata (dict): Additional metadata
        
        Returns:
            int: Import log ID
        """
        self.connect()
        cursor = self.connection.cursor()
        
        log_data = {
            'import_date': datetime.now().isoformat(),
            'import_type': import_type,
            'source': source,
            'status': status,
            'message': message,
            'metadata': json.dumps(metadata) if metadata else None
        }
        
        placeholders = ', '.join(['?'] * len(log_data))
        columns = ', '.join(log_data.keys())
        
        cursor.execute(
            f"INSERT INTO import_log ({columns}) VALUES ({placeholders})",
            list(log_data.values())
        )
        
        import_id = cursor.lastrowid
        self.connection.commit()
        self.disconnect()
        
        return import_id
    
    def store_ai_analysis(self, proj_id, analysis_type, results, visualization_data=None):
        """Store AI analysis results in the database.
        
        Args:
            proj_id (str): Project ID
            analysis_type (str): Type of analysis
            results (dict): Analysis results
            visualization_data (dict): Data for visualizations
        
        Returns:
            int: Analysis ID
        """
        self.connect()
        cursor = self.connection.cursor()
        
        analysis_data = {
            'proj_id': proj_id,
            'analysis_date': datetime.now().isoformat(),
            'analysis_type': analysis_type,
            'results': json.dumps(results),
            'visualization_data': json.dumps(visualization_data) if visualization_data else None
        }
        
        placeholders = ', '.join(['?'] * len(analysis_data))
        columns = ', '.join(analysis_data.keys())
        
        cursor.execute(
            f"INSERT INTO ai_analysis ({columns}) VALUES ({placeholders})",
            list(analysis_data.values())
        )
        
        analysis_id = cursor.lastrowid
        self.connection.commit()
        self.disconnect()
        
        return analysis_id
    
    def get_projects(self, proj_id=None):
        """Retrieve projects from the database.
        
        Args:
            proj_id (str): Specific project ID or None for all projects
        
        Returns:
            list: List of project dictionaries
        """
        self.connect()
        cursor = self.connection.cursor()
        
        if proj_id:
            cursor.execute("SELECT * FROM projects WHERE proj_id = ?", (proj_id,))
        else:
            cursor.execute("SELECT * FROM projects")
            
        projects = []
        for row in cursor.fetchall():
            project = dict(row)
            
            # Parse metadata JSON if present
            if project.get('metadata'):
                try:
                    metadata = json.loads(project['metadata'])
                    # Remove metadata field and merge with project
                    del project['metadata']
                    project.update(metadata)
                except json.JSONDecodeError:
                    pass
                    
            projects.append(project)
            
        self.disconnect()
        return projects
    
    def get_activities(self, proj_id=None, task_id=None):
        """Retrieve activities from the database.
        
        Args:
            proj_id (str): Specific project ID or None for all projects
            task_id (str): Specific task ID or None for all tasks
        
        Returns:
            list: List of activity dictionaries
        """
        self.connect()
        cursor = self.connection.cursor()
        
        if task_id:
            cursor.execute("SELECT * FROM activities WHERE task_id = ?", (task_id,))
        elif proj_id:
            cursor.execute("SELECT * FROM activities WHERE proj_id = ?", (proj_id,))
        else:
            cursor.execute("SELECT * FROM activities")
            
        activities = []
        for row in cursor.fetchall():
            activity = dict(row)
            
            # Parse metadata JSON if present
            if activity.get('metadata'):
                try:
                    metadata = json.loads(activity['metadata'])
                    # Remove metadata field and merge with activity
                    del activity['metadata']
                    activity.update(metadata)
                except json.JSONDecodeError:
                    pass
                    
            activities.append(activity)
            
        self.disconnect()
        return activities
    
    def get_ai_analysis(self, analysis_id=None, proj_id=None, analysis_type=None):
        """Retrieve AI analysis results from the database.
        
        Args:
            analysis_id (int): Specific analysis ID or None
            proj_id (str): Specific project ID or None
            analysis_type (str): Specific analysis type or None
        
        Returns:
            list: List of analysis dictionaries
        """
        self.connect()
        cursor = self.connection.cursor()
        
        query = "SELECT * FROM ai_analysis"
        params = []
        conditions = []
        
        if analysis_id:
            conditions.append("analysis_id = ?")
            params.append(analysis_id)
            
        if proj_id:
            conditions.append("proj_id = ?")
            params.append(proj_id)
            
        if analysis_type:
            conditions.append("analysis_type = ?")
            params.append(analysis_type)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        cursor.execute(query, params)
            
        analysis_results = []
        for row in cursor.fetchall():
            analysis = dict(row)
            
            # Parse JSON fields
            for field in ['results', 'visualization_data']:
                if analysis.get(field):
                    try:
                        analysis[field] = json.loads(analysis[field])
                    except json.JSONDecodeError:
                        pass
                    
            analysis_results.append(analysis)
            
        self.disconnect()
        return analysis_results
    
    def run_query(self, query, params=None):
        """Run a custom query against the database.
        
        Args:
            query (str): SQL query
            params (tuple): Query parameters
        
        Returns:
            list: Query results
        """
        self.connect()
        cursor = self.connection.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            # Check if query is a SELECT
            if query.strip().upper().startswith('SELECT'):
                results = [dict(row) for row in cursor.fetchall()]
            else:
                self.connection.commit()
                results = {'rowcount': cursor.rowcount}
                
            self.disconnect()
            return results
        except Exception as e:
            self.connection.rollback()
            self.disconnect()
            raise e
    
    def export_to_dataframe(self, table_name, conditions=None):
        """Export a table to pandas DataFrame.
        
        Args:
            table_name (str): Name of the table
            conditions (dict): Query conditions
        
        Returns:
            DataFrame: Pandas DataFrame
        """
        self.connect()
        
        query = f"SELECT * FROM {table_name}"
        params = []
        
        if conditions:
            query_conditions = []
            for key, value in conditions.items():
                query_conditions.append(f"{key} = ?")
                params.append(value)
                
            if query_conditions:
                query += " WHERE " + " AND ".join(query_conditions)
                
        df = pd.read_sql_query(query, self.connection, params=params)
        self.disconnect()
        
        return df
