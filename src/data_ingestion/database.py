import sqlite3
import os
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path

from src.models.schemas import Task, ProjectData, EVMMetrics, Forecast, VarianceExplanation
from src.config.settings import settings


class Database:
    """Database handler for the EVM AI Agent using embedded SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the database connection.
        
        Args:
            db_path: Optional path to the database file. If not provided, uses default path.
        """
        # Use provided path or default from settings
        if db_path is None:
            # Make sure the directory exists
            db_dir = Path(settings.DATABASE_DIR)
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / settings.DATABASE_FILENAME)
            
        self.db_path = db_path
        self.conn = None
        
        # Initialize database
        self._initialize_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a connection to the database, creating a new one if needed.
        
        Returns:
            sqlite3.Connection: Database connection
        """
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            
            # Enable foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON")
            
        return self.conn

    def _initialize_database(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create projects table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            start_date TEXT NOT NULL,
            planned_finish_date TEXT NOT NULL,
            budget_at_completion REAL NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
        
        # Create tasks table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            name TEXT NOT NULL,
            wbs_element TEXT,
            control_account TEXT,
            responsible_person TEXT,
            planned_start_date TEXT,
            planned_finish_date TEXT,
            actual_start_date TEXT,
            actual_finish_date TEXT,
            budget_at_completion REAL NOT NULL,
            status TEXT NOT NULL,
            percent_complete REAL NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
        """)
        
        # Create EVM metrics table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS evm_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            date TEXT NOT NULL,
            bcws REAL NOT NULL,
            bcwp REAL NOT NULL,
            acwp REAL NOT NULL,
            bac REAL NOT NULL,
            eac REAL NOT NULL,
            etc REAL NOT NULL,
            cv REAL NOT NULL,
            sv REAL NOT NULL,
            cpi REAL NOT NULL,
            spi REAL NOT NULL,
            tcpi REAL NOT NULL,
            vac REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        )
        """)
        
        # Create forecasts table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            date TEXT NOT NULL,
            eac REAL NOT NULL,
            etc REAL NOT NULL,
            estimated_finish_date TEXT NOT NULL,
            probability REAL NOT NULL,
            methodology TEXT NOT NULL,
            key_factors TEXT,  -- JSON array
            created_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
        """)
        
        # Create variance explanations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS variance_explanations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            date TEXT NOT NULL,
            variance_type TEXT NOT NULL,
            explanation TEXT NOT NULL,
            factors TEXT,  -- JSON array
            impact TEXT NOT NULL,
            recommendations TEXT,  -- JSON array
            confidence REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        )
        """)
        
        # Create user_queries table for logging interactions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            intent TEXT,
            entities TEXT,  -- JSON object
            response TEXT,
            created_at TEXT NOT NULL
        )
        """)
        
        conn.commit()

    def close(self):
        """Close the database connection."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def insert_project(self, project: ProjectData) -> bool:
        """Insert a new project into the database.
        
        Args:
            project: ProjectData object to insert
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # Insert project record
            cursor.execute("""
            INSERT INTO projects 
            (id, name, description, start_date, planned_finish_date, budget_at_completion, 
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project.id,
                project.name,
                project.description,
                project.start_date.isoformat(),
                project.planned_finish_date.isoformat(),
                project.budget_at_completion,
                now,
                now
            ))
            
            # Insert associated tasks if any
            if project.tasks:
                for task in project.tasks:
                    self.insert_task(task, project.id)
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error inserting project: {e}")
            conn.rollback()
            return False

    def insert_task(self, task: Task, project_id: str) -> bool:
        """Insert a new task into the database.
        
        Args:
            task: Task object to insert
            project_id: ID of the project this task belongs to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # Convert dates to ISO format, handling None values
            planned_start = task.planned_start_date.isoformat() if task.planned_start_date else None
            planned_finish = task.planned_finish_date.isoformat() if task.planned_finish_date else None
            actual_start = task.actual_start_date.isoformat() if task.actual_start_date else None
            actual_finish = task.actual_finish_date.isoformat() if task.actual_finish_date else None
            
            cursor.execute("""
            INSERT INTO tasks
            (id, project_id, name, wbs_element, control_account, responsible_person,
             planned_start_date, planned_finish_date, actual_start_date, actual_finish_date,
             budget_at_completion, status, percent_complete, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id,
                project_id,
                task.name,
                task.wbs_element,
                task.control_account,
                task.responsible_person,
                planned_start,
                planned_finish,
                actual_start,
                actual_finish,
                task.budget_at_completion,
                task.status,
                task.percent_complete,
                now,
                now
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error inserting task: {e}")
            conn.rollback()
            return False

    def insert_evm_metrics(self, metrics: EVMMetrics) -> bool:
        """Insert new EVM metrics into the database.
        
        Args:
            metrics: EVMMetrics object to insert
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
            INSERT INTO evm_metrics
            (task_id, date, bcws, bcwp, acwp, bac, eac, etc, cv, sv, cpi, spi, tcpi, vac, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.task_id,
                metrics.date.isoformat(),
                metrics.bcws,
                metrics.bcwp,
                metrics.acwp,
                metrics.bac,
                metrics.eac,
                metrics.etc,
                metrics.cv,
                metrics.sv,
                metrics.cpi,
                metrics.spi,
                metrics.tcpi,
                metrics.vac,
                now
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error inserting EVM metrics: {e}")
            conn.rollback()
            return False

    def insert_forecast(self, forecast: Forecast) -> bool:
        """Insert a new forecast into the database.
        
        Args:
            forecast: Forecast object to insert
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # Convert key factors to JSON if present
            key_factors_json = json.dumps(forecast.key_factors) if forecast.key_factors else None
            
            cursor.execute("""
            INSERT INTO forecasts
            (project_id, date, eac, etc, estimated_finish_date, probability, methodology, 
             key_factors, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                forecast.project_id,
                forecast.date.isoformat(),
                forecast.eac,
                forecast.etc,
                forecast.estimated_finish_date.isoformat(),
                forecast.probability,
                forecast.methodology,
                key_factors_json,
                now
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error inserting forecast: {e}")
            conn.rollback()
            return False

    def insert_variance_explanation(self, explanation: VarianceExplanation) -> bool:
        """Insert a new variance explanation into the database.
        
        Args:
            explanation: VarianceExplanation object to insert
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # Convert lists to JSON if present
            factors_json = json.dumps(explanation.factors) if explanation.factors else None
            recommendations_json = json.dumps(explanation.recommendations) if explanation.recommendations else None
            
            cursor.execute("""
            INSERT INTO variance_explanations
            (task_id, date, variance_type, explanation, factors, impact, 
             recommendations, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                explanation.task_id,
                explanation.date.isoformat(),
                explanation.variance_type,
                explanation.explanation,
                factors_json,
                explanation.impact,
                recommendations_json,
                explanation.confidence,
                now
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error inserting variance explanation: {e}")
            conn.rollback()
            return False

    def log_user_query(self, query: str, intent: Optional[str] = None, 
                      entities: Optional[Dict[str, Any]] = None, 
                      response: Optional[str] = None) -> bool:
        """Log a user query and the system's response for future analysis.
        
        Args:
            query: The user's original query text
            intent: The detected intent, if any
            entities: The extracted entities, if any
            response: The system's response to the query
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # Convert entities to JSON if present
            entities_json = json.dumps(entities) if entities else None
            
            cursor.execute("""
            INSERT INTO user_queries
            (query, intent, entities, response, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (
                query,
                intent,
                entities_json,
                response,
                now
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error logging user query: {e}")
            conn.rollback()
            return False

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a project by ID.
        
        Args:
            project_id: The ID of the project to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Project data as a dictionary, or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM projects WHERE id = ?
            """, (project_id,))
            
            result = cursor.fetchone()
            if result is None:
                return None
                
            # Convert to dictionary
            project = dict(result)
            
            # Parse dates
            for date_field in ['start_date', 'planned_finish_date', 'created_at', 'updated_at']:
                if project[date_field]:
                    project[date_field] = datetime.fromisoformat(project[date_field])
            
            # Get tasks for this project
            project['tasks'] = self.get_tasks_for_project(project_id)
            
            return project
            
        except Exception as e:
            print(f"Error getting project: {e}")
            return None

    def get_tasks_for_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a specific project.
        
        Args:
            project_id: The ID of the project to get tasks for
            
        Returns:
            List[Dict[str, Any]]: List of tasks as dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM tasks WHERE project_id = ?
            """, (project_id,))
            
            tasks = []
            for row in cursor.fetchall():
                task = dict(row)
                
                # Parse dates
                for date_field in ['planned_start_date', 'planned_finish_date', 'actual_start_date', 
                                'actual_finish_date', 'created_at', 'updated_at']:
                    if task[date_field]:
                        task[date_field] = datetime.fromisoformat(task[date_field])
                
                tasks.append(task)
                
            return tasks
            
        except Exception as e:
            print(f"Error getting tasks for project: {e}")
            return []

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID.
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Task data as a dictionary, or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM tasks WHERE id = ?
            """, (task_id,))
            
            result = cursor.fetchone()
            if result is None:
                return None
                
            # Convert to dictionary
            task = dict(result)
            
            # Parse dates
            for date_field in ['planned_start_date', 'planned_finish_date', 'actual_start_date', 
                            'actual_finish_date', 'created_at', 'updated_at']:
                if task[date_field]:
                    task[date_field] = datetime.fromisoformat(task[date_field])
            
            return task
            
        except Exception as e:
            print(f"Error getting task: {e}")
            return None

    def get_latest_evm_metrics(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest EVM metrics for a task.
        
        Args:
            task_id: The ID of the task to get metrics for
            
        Returns:
            Optional[Dict[str, Any]]: Latest EVM metrics as a dictionary, or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM evm_metrics 
            WHERE task_id = ? 
            ORDER BY date DESC, created_at DESC 
            LIMIT 1
            """, (task_id,))
            
            result = cursor.fetchone()
            if result is None:
                return None
                
            # Convert to dictionary
            metrics = dict(result)
            
            # Parse date
            if metrics['date']:
                metrics['date'] = datetime.fromisoformat(metrics['date'])
            
            if metrics['created_at']:
                metrics['created_at'] = datetime.fromisoformat(metrics['created_at'])
            
            return metrics
            
        except Exception as e:
            print(f"Error getting latest EVM metrics: {e}")
            return None

    def get_latest_forecast(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest forecast for a project.
        
        Args:
            project_id: The ID of the project to get the forecast for
            
        Returns:
            Optional[Dict[str, Any]]: Latest forecast as a dictionary, or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM forecasts 
            WHERE project_id = ? 
            ORDER BY date DESC, created_at DESC 
            LIMIT 1
            """, (project_id,))
            
            result = cursor.fetchone()
            if result is None:
                return None
                
            # Convert to dictionary
            forecast = dict(result)
            
            # Parse dates
            for date_field in ['date', 'estimated_finish_date', 'created_at']:
                if forecast[date_field]:
                    forecast[date_field] = datetime.fromisoformat(forecast[date_field])
            
            # Parse JSON fields
            if forecast['key_factors']:
                forecast['key_factors'] = json.loads(forecast['key_factors'])
            
            return forecast
            
        except Exception as e:
            print(f"Error getting latest forecast: {e}")
            return None

    def get_latest_variance_explanation(self, task_id: str, variance_type: str) -> Optional[Dict[str, Any]]:
        """Get the latest variance explanation for a task and variance type.
        
        Args:
            task_id: The ID of the task to get the explanation for
            variance_type: The type of variance (cost, schedule, etc.)
            
        Returns:
            Optional[Dict[str, Any]]: Latest variance explanation as a dictionary, or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM variance_explanations 
            WHERE task_id = ? AND variance_type = ? 
            ORDER BY date DESC, created_at DESC 
            LIMIT 1
            """, (task_id, variance_type))
            
            result = cursor.fetchone()
            if result is None:
                return None
                
            # Convert to dictionary
            explanation = dict(result)
            
            # Parse date
            if explanation['date']:
                explanation['date'] = datetime.fromisoformat(explanation['date'])
            
            if explanation['created_at']:
                explanation['created_at'] = datetime.fromisoformat(explanation['created_at'])
            
            # Parse JSON fields
            if explanation['factors']:
                explanation['factors'] = json.loads(explanation['factors'])
                
            if explanation['recommendations']:
                explanation['recommendations'] = json.loads(explanation['recommendations'])
            
            return explanation
            
        except Exception as e:
            print(f"Error getting latest variance explanation: {e}")
            return None

    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects in the database.
        
        Returns:
            List[Dict[str, Any]]: List of all projects as dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM projects")
            
            projects = []
            for row in cursor.fetchall():
                project = dict(row)
                
                # Parse dates
                for date_field in ['start_date', 'planned_finish_date', 'created_at', 'updated_at']:
                    if project[date_field]:
                        project[date_field] = datetime.fromisoformat(project[date_field])
                
                # Get tasks for this project
                project['tasks'] = self.get_tasks_for_project(project['id'])
                
                projects.append(project)
                
            return projects
            
        except Exception as e:
            print(f"Error getting all projects: {e}")
            return []

    def get_evm_metrics_history(self, task_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get historical EVM metrics for a task.
        
        Args:
            task_id: The ID of the task to get metrics history for
            limit: Maximum number of records to return
            
        Returns:
            List[Dict[str, Any]]: List of historical EVM metrics as dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM evm_metrics 
            WHERE task_id = ? 
            ORDER BY date DESC, created_at DESC 
            LIMIT ?
            """, (task_id, limit))
            
            metrics_history = []
            for row in cursor.fetchall():
                metrics = dict(row)
                
                # Parse dates
                if metrics['date']:
                    metrics['date'] = datetime.fromisoformat(metrics['date'])
                
                if metrics['created_at']:
                    metrics['created_at'] = datetime.fromisoformat(metrics['created_at'])
                
                metrics_history.append(metrics)
                
            return metrics_history
            
        except Exception as e:
            print(f"Error getting EVM metrics history: {e}")
            return []

    def search_projects(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for projects by name or description.
        
        Args:
            search_term: The term to search for
            
        Returns:
            List[Dict[str, Any]]: List of matching projects as dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Use LIKE for simple text search
            search_pattern = f"%{search_term}%"
            
            cursor.execute("""
            SELECT * FROM projects 
            WHERE name LIKE ? OR description LIKE ? 
            ORDER BY name
            """, (search_pattern, search_pattern))
            
            projects = []
            for row in cursor.fetchall():
                project = dict(row)
                
                # Parse dates
                for date_field in ['start_date', 'planned_finish_date', 'created_at', 'updated_at']:
                    if project[date_field]:
                        project[date_field] = datetime.fromisoformat(project[date_field])
                
                projects.append(project)
                
            return projects
            
        except Exception as e:
            print(f"Error searching projects: {e}")
            return []

    def get_recent_user_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent user queries for analysis.
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List[Dict[str, Any]]: List of recent user queries as dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM user_queries 
            ORDER BY created_at DESC 
            LIMIT ?
            """, (limit,))
            
            queries = []
            for row in cursor.fetchall():
                query = dict(row)
                
                # Parse date
                if query['created_at']:
                    query['created_at'] = datetime.fromisoformat(query['created_at'])
                
                # Parse entities JSON
                if query['entities']:
                    query['entities'] = json.loads(query['entities'])
                
                queries.append(query)
                
            return queries
            
        except Exception as e:
            print(f"Error getting recent user queries: {e}")
            return []
