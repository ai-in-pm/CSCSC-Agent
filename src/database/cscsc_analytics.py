import os
import sqlite3
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


class CSCSCAnalyticsDB:
    """Database handler for CSCSC Agent Analytics.
    
    This class implements a multi-dimensional time series database using SQLite
    for storing and analyzing EVM metrics, forecast data, and simulation results.
    It provides statistical analysis capabilities including Bayesian forecasting,
    sensitivity analysis, and Monte Carlo simulation result persistence.
    """
    
    def __init__(self, db_path=None):
        """Initialize the analytics database.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default path.
        """
        if db_path is None:
            # Create database in project root/data directory
            root_dir = Path(__file__).parent.parent.parent
            data_dir = root_dir / 'data'
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / 'cscsc_analytics.db'
            
        self.db_path = db_path
        self.conn = None
        self.initialize_database()
    
    def __enter__(self):
        """Context manager entry point."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def initialize_database(self):
        """Create necessary database tables if they don't exist."""
        with self as db:
            cursor = db.conn.cursor()
            
            # Time series data for EVM metrics
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS evm_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                pv REAL,
                ev REAL,
                ac REAL,
                sv REAL,
                cv REAL,
                spi REAL,
                cpi REAL,
                etc REAL,
                eac REAL,
                tcpi REAL,
                created_at TEXT NOT NULL
            )
            """)
            
            # Forecasts table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                forecast_type TEXT NOT NULL,
                forecast_data TEXT NOT NULL,
                model_params TEXT,
                accuracy REAL,
                confidence_interval REAL,
                rmse REAL,
                mae REAL,
                created_at TEXT NOT NULL
            )
            """)
            
            # Sensitivity analysis results
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensitivity_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                parameters TEXT NOT NULL,
                results TEXT NOT NULL,
                key_findings TEXT,
                created_at TEXT NOT NULL
            )
            """)
            
            # Monte Carlo simulation results
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS monte_carlo_simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                simulation_runs INTEGER NOT NULL,
                distribution_data TEXT NOT NULL,
                p10_completion TEXT,
                p50_completion TEXT,
                p80_completion TEXT,
                p90_completion TEXT,
                risk_factors TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL
            )
            """)
            
            # Risk factors identified by AI
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_factors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                risk_name TEXT NOT NULL,
                impact TEXT NOT NULL,
                probability REAL,
                confidence REAL,
                detection_method TEXT,
                mitigation_strategy TEXT,
                status TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
            """)
            
            db.conn.commit()
    
    def store_evm_metrics(self, project_id, metrics):
        """Store EVM metrics for a project.
        
        Args:
            project_id: Unique identifier for the project
            metrics: Dictionary containing EVM metrics
        
        Returns:
            int: The ID of the inserted record
        """
        with self as db:
            cursor = db.conn.cursor()
            timestamp = metrics.get('timestamp', datetime.now().isoformat())
            created_at = datetime.now().isoformat()
            
            cursor.execute("""
            INSERT INTO evm_metrics (
                project_id, timestamp, pv, ev, ac, sv, cv, spi, cpi, etc, eac, tcpi, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                timestamp,
                metrics.get('pv'),
                metrics.get('ev'),
                metrics.get('ac'),
                metrics.get('sv'),
                metrics.get('cv'),
                metrics.get('spi'),
                metrics.get('cpi'),
                metrics.get('etc'),
                metrics.get('eac'),
                metrics.get('tcpi'),
                created_at
            ))
            
            db.conn.commit()
            return cursor.lastrowid
    
    def store_forecast(self, project_id, forecast_type, forecast_data, model_params=None, metrics=None):
        """Store forecast results for a project.
        
        Args:
            project_id: Unique identifier for the project
            forecast_type: Type of forecast (e.g., 'bayesian', 'arima', 'lstm')
            forecast_data: Dictionary containing forecast time series data
            model_params: Optional parameters used for the forecast model
            metrics: Optional accuracy metrics for the forecast
            
        Returns:
            int: The ID of the inserted record
        """
        with self as db:
            cursor = db.conn.cursor()
            timestamp = datetime.now().isoformat()
            created_at = timestamp
            
            # Convert data structures to JSON
            forecast_json = json.dumps(forecast_data)
            model_params_json = json.dumps(model_params) if model_params else None
            
            # Extract metrics if provided
            accuracy = metrics.get('accuracy') if metrics else None
            confidence_interval = metrics.get('confidence_interval') if metrics else None
            rmse = metrics.get('rmse') if metrics else None
            mae = metrics.get('mae') if metrics else None
            
            cursor.execute("""
            INSERT INTO forecasts (
                project_id, timestamp, forecast_type, forecast_data, model_params,
                accuracy, confidence_interval, rmse, mae, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                timestamp,
                forecast_type,
                forecast_json,
                model_params_json,
                accuracy,
                confidence_interval,
                rmse,
                mae,
                created_at
            ))
            
            db.conn.commit()
            return cursor.lastrowid
    
    def store_sensitivity_analysis(self, project_id, parameters, results, key_findings=None):
        """Store sensitivity analysis results.
        
        Args:
            project_id: Unique identifier for the project
            parameters: Dictionary of parameters used in sensitivity analysis
            results: Dictionary of sensitivity analysis results
            key_findings: Optional text summarizing key findings
            
        Returns:
            int: The ID of the inserted record
        """
        with self as db:
            cursor = db.conn.cursor()
            timestamp = datetime.now().isoformat()
            created_at = timestamp
            
            # Convert data structures to JSON
            parameters_json = json.dumps(parameters)
            results_json = json.dumps(results)
            
            cursor.execute("""
            INSERT INTO sensitivity_analyses (
                project_id, timestamp, parameters, results, key_findings, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                timestamp,
                parameters_json,
                results_json,
                key_findings,
                created_at
            ))
            
            db.conn.commit()
            return cursor.lastrowid
    
    def store_monte_carlo_simulation(self, project_id, simulation_runs, distribution_data, 
                                    completion_dates, risk_factors, metadata=None):
        """Store Monte Carlo simulation results.
        
        Args:
            project_id: Unique identifier for the project
            simulation_runs: Number of simulation runs executed
            distribution_data: Dictionary containing probability distribution
            completion_dates: Dictionary with p10, p50, p80, p90 completion dates
            risk_factors: List of risk factors identified during simulation
            metadata: Optional metadata about the simulation
            
        Returns:
            int: The ID of the inserted record
        """
        with self as db:
            cursor = db.conn.cursor()
            timestamp = datetime.now().isoformat()
            created_at = timestamp
            
            # Convert data structures to JSON
            distribution_json = json.dumps(distribution_data)
            risk_factors_json = json.dumps(risk_factors)
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
            INSERT INTO monte_carlo_simulations (
                project_id, timestamp, simulation_runs, distribution_data,
                p10_completion, p50_completion, p80_completion, p90_completion,
                risk_factors, metadata, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                timestamp,
                simulation_runs,
                distribution_json,
                completion_dates.get('p10'),
                completion_dates.get('p50'),
                completion_dates.get('p80'),
                completion_dates.get('p90'),
                risk_factors_json,
                metadata_json,
                created_at
            ))
            
            db.conn.commit()
            return cursor.lastrowid
    
    def store_risk_factor(self, project_id, risk_name, impact, probability, confidence,
                        detection_method=None, mitigation_strategy=None, status="Identified"):
        """Store a risk factor identified by AI analysis.
        
        Args:
            project_id: Unique identifier for the project
            risk_name: Name/description of the risk
            impact: Impact level (High, Medium, Low)
            probability: Probability of risk occurrence (0-100)
            confidence: AI confidence in the risk assessment (0-100)
            detection_method: Method used to detect the risk
            mitigation_strategy: Proposed strategy to mitigate the risk
            status: Current status of the risk
            
        Returns:
            int: The ID of the inserted record
        """
        with self as db:
            cursor = db.conn.cursor()
            created_at = datetime.now().isoformat()
            
            cursor.execute("""
            INSERT INTO risk_factors (
                project_id, risk_name, impact, probability, confidence,
                detection_method, mitigation_strategy, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                risk_name,
                impact,
                probability,
                confidence,
                detection_method,
                mitigation_strategy,
                status,
                created_at,
                created_at  # Initially the same as created_at
            ))
            
            db.conn.commit()
            return cursor.lastrowid
    
    def get_latest_evm_metrics(self, project_id, limit=10):
        """Get the latest EVM metrics for a project.
        
        Args:
            project_id: Unique identifier for the project
            limit: Maximum number of records to return
            
        Returns:
            list: List of dictionaries containing EVM metrics
        """
        with self as db:
            cursor = db.conn.cursor()
            
            cursor.execute("""
            SELECT * FROM evm_metrics 
            WHERE project_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """, (project_id, limit))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def get_latest_forecast(self, project_id, forecast_type=None):
        """Get the latest forecast for a project.
        
        Args:
            project_id: Unique identifier for the project
            forecast_type: Optional type of forecast to filter by
            
        Returns:
            dict: Dictionary containing forecast data and metrics
        """
        with self as db:
            cursor = db.conn.cursor()
            
            if forecast_type:
                cursor.execute("""
                SELECT * FROM forecasts 
                WHERE project_id = ? AND forecast_type = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
                """, (project_id, forecast_type))
            else:
                cursor.execute("""
                SELECT * FROM forecasts 
                WHERE project_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
                """, (project_id,))
            
            row = cursor.fetchone()
            if row:
                result = dict(row)
                # Parse JSON fields
                result['forecast_data'] = json.loads(result['forecast_data'])
                if result['model_params']:
                    result['model_params'] = json.loads(result['model_params'])
                return result
            return None
    
    def get_latest_monte_carlo_simulation(self, project_id):
        """Get the latest Monte Carlo simulation results for a project.
        
        Args:
            project_id: Unique identifier for the project
            
        Returns:
            dict: Dictionary containing Monte Carlo simulation results
        """
        with self as db:
            cursor = db.conn.cursor()
            
            cursor.execute("""
            SELECT * FROM monte_carlo_simulations 
            WHERE project_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
            """, (project_id,))
            
            row = cursor.fetchone()
            if row:
                result = dict(row)
                # Parse JSON fields
                result['distribution_data'] = json.loads(result['distribution_data'])
                result['risk_factors'] = json.loads(result['risk_factors'])
                if result['metadata']:
                    result['metadata'] = json.loads(result['metadata'])
                return result
            return None
    
    def get_risk_factors(self, project_id, status=None):
        """Get risk factors for a project, optionally filtered by status.
        
        Args:
            project_id: Unique identifier for the project
            status: Optional status to filter risks by
            
        Returns:
            list: List of dictionaries containing risk factors
        """
        with self as db:
            cursor = db.conn.cursor()
            
            if status:
                cursor.execute("""
                SELECT * FROM risk_factors 
                WHERE project_id = ? AND status = ? 
                ORDER BY confidence DESC
                """, (project_id, status))
            else:
                cursor.execute("""
                SELECT * FROM risk_factors 
                WHERE project_id = ? 
                ORDER BY confidence DESC
                """, (project_id,))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def get_elasticity_analysis(self, project_id):
        """Calculate elasticity values from sensitivity analyses.
        
        This advanced function computes elasticity coefficients based on
        sensitivity analysis results to identify the most impactful factors.
        
        Args:
            project_id: Unique identifier for the project
            
        Returns:
            pandas.DataFrame: DataFrame containing elasticity coefficients
        """
        with self as db:
            cursor = db.conn.cursor()
            
            cursor.execute("""
            SELECT parameters, results FROM sensitivity_analyses 
            WHERE project_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
            """, (project_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            parameters = json.loads(row['parameters'])
            results = json.loads(row['results'])
            
            # In a real implementation, this would calculate actual elasticity
            # values based on the sensitivity analysis results
            
            # For demonstration, return a mock DataFrame
            elasticity_data = {
                'Parameter': [
                    'Labor Productivity',
                    'Material Costs',
                    'Weather Days',
                    'Permitting Time',
                    'Equipment Availability'
                ],
                'Elasticity': [1.53, 0.72, 1.18, 0.95, 0.86],
                'Impact': ['High', 'Medium', 'High', 'Medium', 'Medium']
            }
            
            return pd.DataFrame(elasticity_data)
