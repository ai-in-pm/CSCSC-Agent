import json
import csv
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

from src.models.schemas import Task, ProjectData, EVMMetrics
from src.data_ingestion.database import Database
from src.config.settings import settings


class DataLoader:
    """Data loader for importing project data from various formats."""

    def __init__(self, db: Optional[Database] = None):
        """Initialize the data loader.
        
        Args:
            db: Optional database instance to use
        """
        self.db = db if db is not None else Database()

    def load_json_project(self, file_path: Union[str, Path]) -> bool:
        """Load project data from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert to Path if string
            if isinstance(file_path, str):
                file_path = Path(file_path)
                
            # Check if file exists
            if not file_path.exists():
                print(f"Error: File {file_path} does not exist")
                return False
                
            # Read JSON file
            with open(file_path, 'r') as f:
                project_data = json.load(f)
                
            # Convert dates from strings to datetime objects
            self._convert_dates(project_data)
            
            # Convert to ProjectData object
            project = ProjectData(**project_data)
            
            # Insert into database
            return self.db.insert_project(project)
            
        except Exception as e:
            print(f"Error loading JSON project: {e}")
            return False

    def load_csv_tasks(self, file_path: Union[str, Path], project_id: str) -> bool:
        """Load task data from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            project_id: ID of the project to associate tasks with
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert to Path if string
            if isinstance(file_path, str):
                file_path = Path(file_path)
                
            # Check if file exists
            if not file_path.exists():
                print(f"Error: File {file_path} does not exist")
                return False
                
            # Read CSV file using pandas for better column handling
            tasks_df = pd.read_csv(file_path)
            
            # Insert each task into database
            success_count = 0
            total_count = 0
            
            for _, row in tasks_df.iterrows():
                try:
                    # Convert row to dictionary and handle missing values
                    task_dict = row.to_dict()
                    
                    # Clean dictionary - remove NaN values and convert date strings
                    task_dict = {k: v for k, v in task_dict.items() if pd.notna(v)}
                    self._convert_dict_dates(task_dict)
                    
                    # Add project_id if not present
                    if 'project_id' not in task_dict:
                        task_dict['project_id'] = project_id
                    
                    # Create Task object and insert into database
                    task = Task(**task_dict)
                    if self.db.insert_task(task, project_id):
                        success_count += 1
                        
                    total_count += 1
                    
                except Exception as e:
                    print(f"Error processing task row: {e}")
                    continue
                    
            print(f"Loaded {success_count} of {total_count} tasks successfully")
            return success_count > 0
            
        except Exception as e:
            print(f"Error loading CSV tasks: {e}")
            return False

    def load_excel_project_data(self, file_path: Union[str, Path]) -> bool:
        """Load project data from an Excel file with multiple sheets.
        
        Expected sheet names: 'Project', 'Tasks', 'Metrics'
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert to Path if string
            if isinstance(file_path, str):
                file_path = Path(file_path)
                
            # Check if file exists
            if not file_path.exists():
                print(f"Error: File {file_path} does not exist")
                return False
                
            # Read Excel file with multiple sheets
            excel_data = pd.read_excel(file_path, sheet_name=None)
            
            # Check if required sheets exist
            if 'Project' not in excel_data:
                print("Error: Excel file missing 'Project' sheet")
                return False
                
            # Process project sheet
            project_df = excel_data['Project']
            if len(project_df) == 0:
                print("Error: Project sheet is empty")
                return False
                
            # Convert first row to dictionary
            project_dict = project_df.iloc[0].to_dict()
            
            # Clean dictionary and convert dates
            project_dict = {k: v for k, v in project_dict.items() if pd.notna(v)}
            self._convert_dict_dates(project_dict)
            
            # Initialize tasks list
            project_dict['tasks'] = []
            
            # Process tasks sheet if it exists
            if 'Tasks' in excel_data:
                tasks_df = excel_data['Tasks']
                
                for _, row in tasks_df.iterrows():
                    try:
                        task_dict = row.to_dict()
                        task_dict = {k: v for k, v in task_dict.items() if pd.notna(v)}
                        self._convert_dict_dates(task_dict)
                        
                        # Add to tasks list
                        project_dict['tasks'].append(task_dict)
                        
                    except Exception as e:
                        print(f"Error processing task row: {e}")
                        continue
            
            # Create ProjectData object
            project = ProjectData(**project_dict)
            
            # Insert project into database
            success = self.db.insert_project(project)
            
            # Process metrics sheet if it exists
            if success and 'Metrics' in excel_data:
                metrics_df = excel_data['Metrics']
                
                for _, row in metrics_df.iterrows():
                    try:
                        metrics_dict = row.to_dict()
                        metrics_dict = {k: v for k, v in metrics_dict.items() if pd.notna(v)}
                        self._convert_dict_dates(metrics_dict)
                        
                        # Create EVMMetrics object and insert into database
                        metrics = EVMMetrics(**metrics_dict)
                        self.db.insert_evm_metrics(metrics)
                        
                    except Exception as e:
                        print(f"Error processing metrics row: {e}")
                        continue
            
            return success
            
        except Exception as e:
            print(f"Error loading Excel project data: {e}")
            return False

    def load_ms_project_xml(self, file_path: Union[str, Path]) -> bool:
        """Load project data from Microsoft Project XML format.
        
        Args:
            file_path: Path to the MS Project XML file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert to Path if string
            if isinstance(file_path, str):
                file_path = Path(file_path)
                
            # Check if file exists
            if not file_path.exists():
                print(f"Error: File {file_path} does not exist")
                return False
                
            # Parse XML file
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract project information
            project_dict = {}
            
            # Find project element - namespace handling may vary
            project_elem = root.find('./Project') or root
            
            # Extract basic project info
            name_elem = project_elem.find('./Name')
            if name_elem is not None and name_elem.text:
                project_dict['name'] = name_elem.text
            else:
                # Generate a name if none exists
                project_dict['name'] = f"Imported Project {datetime.now().strftime('%Y-%m-%d')}"
            
            # Extract project ID or create one
            project_id_elem = project_elem.find('./GUID') or project_elem.find('./ID')
            if project_id_elem is not None and project_id_elem.text:
                project_dict['id'] = f"P{project_id_elem.text[-3:]}"  # Use last 3 chars
            else:
                # Generate an ID if none exists
                import uuid
                project_dict['id'] = f"P{str(uuid.uuid4())[:3]}"
            
            # Extract dates
            start_date_elem = project_elem.find('./StartDate')
            if start_date_elem is not None and start_date_elem.text:
                project_dict['start_date'] = self._parse_date(start_date_elem.text)
            else:
                project_dict['start_date'] = datetime.now()
            
            finish_date_elem = project_elem.find('./FinishDate')
            if finish_date_elem is not None and finish_date_elem.text:
                project_dict['planned_finish_date'] = self._parse_date(finish_date_elem.text)
            else:
                # Default to 3 months from start if not specified
                from datetime import timedelta
                project_dict['planned_finish_date'] = project_dict['start_date'] + timedelta(days=90)
            
            # Extract budget
            budget_elem = project_elem.find('./Cost') or project_elem.find('./Budget')
            if budget_elem is not None and budget_elem.text:
                try:
                    project_dict['budget_at_completion'] = float(budget_elem.text)
                except ValueError:
                    project_dict['budget_at_completion'] = 100000.0  # Default value
            else:
                project_dict['budget_at_completion'] = 100000.0  # Default value
            
            # Initialize tasks list
            project_dict['tasks'] = []
            
            # Find tasks elements
            tasks_elem = project_elem.find('./Tasks') or project_elem.findall('./Task')
            
            if tasks_elem is not None:
                # If we have a Tasks container, get individual Task elements
                if project_elem.find('./Tasks'):
                    tasks = tasks_elem.findall('./Task')
                else:
                    tasks = tasks_elem  # tasks_elem is already the list of Task elements
                
                # Process each task
                for i, task_elem in enumerate(tasks, 1):
                    try:
                        task_dict = {}
                        
                        # Extract task ID
                        task_id_elem = task_elem.find('./ID') or task_elem.find('./UID')
                        if task_id_elem is not None and task_id_elem.text:
                            task_dict['id'] = f"T{task_id_elem.text}"
                        else:
                            task_dict['id'] = f"T{i:03d}"
                        
                        # Extract task name
                        name_elem = task_elem.find('./Name')
                        if name_elem is not None and name_elem.text:
                            task_dict['name'] = name_elem.text
                        else:
                            task_dict['name'] = f"Task {i}"
                        
                        # Extract WBS
                        wbs_elem = task_elem.find('./WBS')
                        if wbs_elem is not None and wbs_elem.text:
                            task_dict['wbs_element'] = wbs_elem.text
                        
                        # Extract dates
                        start_elem = task_elem.find('./Start')
                        if start_elem is not None and start_elem.text:
                            task_dict['planned_start_date'] = self._parse_date(start_elem.text)
                        
                        finish_elem = task_elem.find('./Finish')
                        if finish_elem is not None and finish_elem.text:
                            task_dict['planned_finish_date'] = self._parse_date(finish_elem.text)
                        
                        # Extract budget
                        cost_elem = task_elem.find('./Cost')
                        if cost_elem is not None and cost_elem.text:
                            try:
                                task_dict['budget_at_completion'] = float(cost_elem.text)
                            except ValueError:
                                task_dict['budget_at_completion'] = 10000.0  # Default
                        else:
                            task_dict['budget_at_completion'] = 10000.0  # Default
                        
                        # Extract percent complete
                        pct_elem = task_elem.find('./PercentComplete') or task_elem.find('./PercentWorkComplete')
                        if pct_elem is not None and pct_elem.text:
                            try:
                                pct = float(pct_elem.text)
                                # MS Project may store as 0-100 or 0-1
                                task_dict['percent_complete'] = pct / 100 if pct > 1 else pct
                            except ValueError:
                                task_dict['percent_complete'] = 0.0
                        else:
                            task_dict['percent_complete'] = 0.0
                        
                        # Determine status based on percent complete
                        if task_dict['percent_complete'] >= 0.9999:
                            task_dict['status'] = 'completed'
                        elif task_dict['percent_complete'] > 0:
                            task_dict['status'] = 'in_progress'
                        else:
                            # Check if scheduled to start in future
                            if 'planned_start_date' in task_dict and task_dict['planned_start_date'] > datetime.now():
                                task_dict['status'] = 'not_started'
                            else:
                                task_dict['status'] = 'not_started'
                        
                        # Add to tasks list
                        project_dict['tasks'].append(task_dict)
                        
                    except Exception as e:
                        print(f"Error processing task element: {e}")
                        continue
            
            # Create ProjectData object
            project = ProjectData(**project_dict)
            
            # Insert into database
            return self.db.insert_project(project)
            
        except Exception as e:
            print(f"Error loading MS Project XML: {e}")
            return False

    def _convert_dates(self, data: Dict[str, Any]):
        """Recursively convert date strings to datetime objects in a dictionary.
        
        Args:
            data: Dictionary to process
        """
        date_fields = ['start_date', 'planned_finish_date', 'actual_start_date', 'actual_finish_date', 
                      'planned_start_date', 'date', 'estimated_finish_date']
        
        for key, value in data.items():
            if key in date_fields and isinstance(value, str):
                data[key] = self._parse_date(value)
            elif isinstance(value, dict):
                self._convert_dates(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._convert_dates(item)

    def _convert_dict_dates(self, data: Dict[str, Any]):
        """Convert date strings to datetime objects in a flat dictionary.
        
        Args:
            data: Dictionary to process
        """
        date_fields = ['start_date', 'planned_finish_date', 'actual_start_date', 'actual_finish_date', 
                      'planned_start_date', 'date', 'estimated_finish_date']
        
        for key in list(data.keys()):
            if key in date_fields and isinstance(data[key], str):
                data[key] = self._parse_date(data[key])

    def _parse_date(self, date_str: str) -> datetime:
        """Parse a date string into a datetime object.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            datetime: Parsed datetime object
        """
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        # Try various common formats
        formats = [
            '%Y-%m-%d',            # 2023-01-15
            '%Y/%m/%d',            # 2023/01/15
            '%m/%d/%Y',            # 01/15/2023
            '%d/%m/%Y',            # 15/01/2023
            '%m-%d-%Y',            # 01-15-2023
            '%d-%m-%Y',            # 15-01-2023
            '%Y-%m-%d %H:%M:%S',   # 2023-01-15 14:30:00
            '%m/%d/%Y %H:%M:%S',   # 01/15/2023 14:30:00
            '%d/%m/%Y %H:%M:%S',   # 15/01/2023 14:30:00
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If all parsing attempts fail, return current date
        print(f"Warning: Could not parse date '{date_str}', using current date")
        return datetime.now()
