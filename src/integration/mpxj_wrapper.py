# MPXJ Wrapper for CSCSC AI Agent
# This module provides Python interfaces to the MPXJ Java library for project file conversions

import os
import logging
import tempfile
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path

# Import MPXJ Python bindings
try:
    import mpxj
    from mpxj import ProjectFile, Duration, TimeUnit, Task, Resource, Assignment
    from mpxj.reader import UniversalProjectReader
    from mpxj.writer import ProjectWriterUtility
    HAS_MPXJ = True
except ImportError:
    logging.warning("MPXJ library not available. Install with 'pip install mpxj'")
    HAS_MPXJ = False

class MPXJConverter:
    """Utility class for converting between different project file formats using MPXJ"""
    
    # Supported input formats
    SUPPORTED_READ_FORMATS = {
        ".mpp": "Microsoft Project MPP",
        ".mpx": "Microsoft Project Exchange",
        ".xml": "Microsoft Project MSPDI XML",
        ".xer": "Primavera P6 XER",
        ".pmxml": "Primavera P6 PMXML",
        ".pp": "Asta Powerproject",
        ".planner": "Planner",
        ".mpd": "Microsoft Project Database",
        ".gan": "GanttProject",
        ".pod": "Primavera P3",
        ".pp": "Asta Powerproject",
        ".prx": "Phoenix",
        ".sch": "SureTrak",
        ".xlsx": "Excel",
        ".sdef": "SDEF",
    }
    
    # Supported output formats
    SUPPORTED_WRITE_FORMATS = {
        ".mpx": "Microsoft Project Exchange",
        ".xml": "Microsoft Project MSPDI XML",
        ".xer": "Primavera P6 XER",
        ".pmxml": "Primavera P6 PMXML",
        ".sdef": "SDEF",
        ".planner": "Planner",
        ".json": "JSON",
    }
    
    def __init__(self):
        """Initialize the MPXJ converter"""
        if not HAS_MPXJ:
            raise ImportError("MPXJ library is required but not installed or available")
        self.reader = UniversalProjectReader()
        self.logger = logging.getLogger(__name__)

    def detect_file_format(self, file_path: str) -> str:
        """Detect the format of a project file
        
        Args:
            file_path: Path to the project file
            
        Returns:
            String describing the detected file format
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        return self.SUPPORTED_READ_FORMATS.get(file_extension, "Unknown")
    
    def is_readable(self, file_path: str) -> bool:
        """Check if a file can be read with MPXJ
        
        Args:
            file_path: Path to the project file
            
        Returns:
            True if the file format is supported for reading
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in self.SUPPORTED_READ_FORMATS
    
    def is_writable(self, file_path: str) -> bool:
        """Check if a file can be written with MPXJ
        
        Args:
            file_path: Path to the project file
            
        Returns:
            True if the file format is supported for writing
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in self.SUPPORTED_WRITE_FORMATS
    
    def read_project(self, file_path: str) -> ProjectFile:
        """Read a project file using MPXJ
        
        Args:
            file_path: Path to the project file
            
        Returns:
            MPXJ ProjectFile object
        """
        self.logger.info(f"Reading project file: {file_path}")
        if not self.is_readable(file_path):
            raise ValueError(f"File format not supported for reading: {file_path}")
        
        try:
            return self.reader.read(file_path)
        except Exception as e:
            self.logger.error(f"Error reading project file: {e}")
            raise
    
    def write_project(self, project: ProjectFile, output_path: str) -> str:
        """Write a project file using MPXJ
        
        Args:
            project: MPXJ ProjectFile object
            output_path: Path to write the project file
            
        Returns:
            Path to the written file
        """
        self.logger.info(f"Writing project file: {output_path}")
        if not self.is_writable(output_path):
            raise ValueError(f"File format not supported for writing: {output_path}")
        
        try:
            writer = ProjectWriterUtility.get_project_writer(output_path)
            writer.write(project, output_path)
            return output_path
        except Exception as e:
            self.logger.error(f"Error writing project file: {e}")
            raise
    
    def convert_file(self, input_path: str, output_path: str) -> str:
        """Convert a project file from one format to another
        
        Args:
            input_path: Path to the input project file
            output_path: Path to write the output project file
            
        Returns:
            Path to the output file
        """
        self.logger.info(f"Converting {input_path} to {output_path}")
        if not self.is_readable(input_path):
            raise ValueError(f"Input file format not supported: {input_path}")
        if not self.is_writable(output_path):
            raise ValueError(f"Output file format not supported: {output_path}")
        
        try:
            project = self.read_project(input_path)
            return self.write_project(project, output_path)
        except Exception as e:
            self.logger.error(f"Error converting file: {e}")
            raise
    
    def project_to_dataframes(self, project: Union[ProjectFile, str]) -> Dict[str, pd.DataFrame]:
        """Convert a project file to pandas DataFrames
        
        Args:
            project: MPXJ ProjectFile object or path to project file
            
        Returns:
            Dictionary of pandas DataFrames containing project data
                - 'tasks': DataFrame of tasks/activities
                - 'resources': DataFrame of resources
                - 'assignments': DataFrame of resource assignments
                - 'relationships': DataFrame of task relationships
                - 'calendars': DataFrame of calendars
        """
        if isinstance(project, str):
            project = self.read_project(project)
        
        # Extract tasks
        tasks_data = []
        for task in project.getTasks():
            if task is None:
                continue
                
            # Get predecessors and successors
            predecessors = []
            for pred in task.getPredecessors():
                if pred is not None and pred.getTargetTask() is not None:
                    predecessors.append({
                        'id': pred.getTargetTask().getID(),
                        'type': str(pred.getType()),
                        'lag': pred.getLag().getDuration() if pred.getLag() else 0
                    })
            
            successors = []
            for succ in task.getSuccessors():
                if succ is not None and succ.getTargetTask() is not None:
                    successors.append({
                        'id': succ.getTargetTask().getID(),
                        'type': str(succ.getType()),
                        'lag': succ.getLag().getDuration() if succ.getLag() else 0
                    })
            
            # Build task dict
            task_dict = {
                'id': task.getID(),
                'unique_id': task.getUniqueID(),
                'name': task.getName(),
                'wbs': task.getWBS(),
                'outline_level': task.getOutlineLevel(),
                'outline_number': task.getOutlineNumber(),
                'duration': task.getDuration().getDuration() if task.getDuration() else None,
                'duration_units': str(task.getDuration().getUnits()) if task.getDuration() else None,
                'start': task.getStart(),
                'finish': task.getFinish(),
                'actual_start': task.getActualStart(),
                'actual_finish': task.getActualFinish(),
                'percent_complete': task.getPercentageComplete(),
                'milestone': task.getMilestone(),
                'summary': task.getSummary(),
                'critical': task.getCritical(),
                'constraint_type': str(task.getConstraintType()) if task.getConstraintType() else None,
                'constraint_date': task.getConstraintDate(),
                'total_slack': task.getTotalSlack().getDuration() if task.getTotalSlack() else None,
                'free_slack': task.getFreeSlack().getDuration() if task.getFreeSlack() else None,
                'priority': task.getPriority(),
                'status_date': task.getStatusDate(),
                'predecessors': predecessors,
                'successors': successors,
            }
            tasks_data.append(task_dict)
        
        # Extract resources
        resources_data = []
        for resource in project.getResources():
            if resource is None:
                continue
                
            resource_dict = {
                'id': resource.getID(),
                'unique_id': resource.getUniqueID(),
                'name': resource.getName(),
                'type': str(resource.getType()) if resource.getType() else None,
                'email': resource.getEmailAddress(),
                'material': resource.getMaterial(),
                'cost_per_use': resource.getCostPerUse(),
                'standard_rate': resource.getStandardRate().getAmount() if resource.getStandardRate() else None,
                'overtime_rate': resource.getOvertimeRate().getAmount() if resource.getOvertimeRate() else None,
                'max_units': resource.getMaxUnits(),
                'calendar': resource.getCalendar().getName() if resource.getCalendar() else None,
            }
            resources_data.append(resource_dict)
        
        # Extract assignments
        assignments_data = []
        for resource in project.getResources():
            if resource is None:
                continue
                
            for assignment in resource.getTaskAssignments():
                if assignment is None or assignment.getTask() is None:
                    continue
                    
                assignment_dict = {
                    'task_id': assignment.getTask().getID(),
                    'task_name': assignment.getTask().getName(),
                    'resource_id': resource.getID(),
                    'resource_name': resource.getName(),
                    'work': assignment.getWork().getDuration() if assignment.getWork() else None,
                    'actual_work': assignment.getActualWork().getDuration() if assignment.getActualWork() else None,
                    'remaining_work': assignment.getRemainingWork().getDuration() if assignment.getRemainingWork() else None,
                    'units': assignment.getUnits(),
                    'cost': assignment.getCost(),
                    'actual_cost': assignment.getActualCost(),
                    'remaining_cost': assignment.getRemainingCost(),
                }
                assignments_data.append(assignment_dict)
        
        # Extract relationships
        relationships_data = []
        for task in project.getTasks():
            if task is None:
                continue
                
            for relation in task.getSuccessors():
                if relation is None or relation.getTargetTask() is None:
                    continue
                    
                relationship_dict = {
                    'predecessor_id': task.getID(),
                    'predecessor_name': task.getName(),
                    'successor_id': relation.getTargetTask().getID(),
                    'successor_name': relation.getTargetTask().getName(),
                    'type': str(relation.getType()),
                    'lag': relation.getLag().getDuration() if relation.getLag() else 0,
                    'lag_units': str(relation.getLag().getUnits()) if relation.getLag() else None,
                }
                relationships_data.append(relationship_dict)
        
        # Extract calendars
        calendars_data = []
        for calendar in project.getCalendars():
            if calendar is None:
                continue
                
            calendar_dict = {
                'unique_id': calendar.getUniqueID(),
                'name': calendar.getName(),
                'working_days': [calendar.isWorkingDay(i) for i in range(1, 8)],  # 1=Sunday to 7=Saturday
            }
            calendars_data.append(calendar_dict)
        
        # Create DataFrames
        return {
            'tasks': pd.DataFrame(tasks_data),
            'resources': pd.DataFrame(resources_data),
            'assignments': pd.DataFrame(assignments_data),
            'relationships': pd.DataFrame(relationships_data),
            'calendars': pd.DataFrame(calendars_data),
        }
    
    def extract_critical_path(self, project: Union[ProjectFile, str]) -> List[Task]:
        """Extract the critical path tasks from a project
        
        Args:
            project: MPXJ ProjectFile object or path to project file
            
        Returns:
            List of tasks on the critical path
        """
        if isinstance(project, str):
            project = self.read_project(project)
            
        return [task for task in project.getTasks() if task and task.getCritical()]
    
    def get_project_statistics(self, project: Union[ProjectFile, str]) -> Dict[str, Any]:
        """Get statistics about a project
        
        Args:
            project: MPXJ ProjectFile object or path to project file
            
        Returns:
            Dictionary of project statistics
        """
        if isinstance(project, str):
            project = self.read_project(project)
            
        tasks = [task for task in project.getTasks() if task is not None]
        resources = [res for res in project.getResources() if res is not None]
        
        # Count task types
        normal_tasks = [task for task in tasks if not task.getMilestone() and not task.getSummary()]
        milestones = [task for task in tasks if task.getMilestone()]
        summary_tasks = [task for task in tasks if task.getSummary()]
        
        # Calculate durations
        total_duration = project.getProjectProperties().getDuration()
        total_duration_days = total_duration.convertUnits(TimeUnit.DAYS).getDuration() if total_duration else 0
        
        # Get dates
        start_date = project.getProjectProperties().getStartDate()
        finish_date = project.getProjectProperties().getFinishDate()
        status_date = project.getProjectProperties().getStatusDate()
        
        return {
            'name': project.getProjectProperties().getName(),
            'task_count': len(tasks),
            'normal_task_count': len(normal_tasks),
            'milestone_count': len(milestones),
            'summary_task_count': len(summary_tasks),
            'resource_count': len(resources),
            'total_duration_days': total_duration_days,
            'start_date': start_date,
            'finish_date': finish_date,
            'status_date': status_date,
            'critical_path_length': len(self.extract_critical_path(project)),
        }

    def import_to_database(self, project_file: Union[str, ProjectFile], db_path: str) -> None:
        """Import a project file into an SQLite database
        
        Args:
            project_file: Path to project file or MPXJ ProjectFile object
            db_path: Path to SQLite database file
        """
        import sqlite3
        
        # Read project if string path provided
        if isinstance(project_file, str):
            project = self.read_project(project_file)
        else:
            project = project_file
        
        # Convert to dataframes
        dataframes = self.project_to_dataframes(project)
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        try:
            # Write dataframes to database
            for table_name, df in dataframes.items():
                # For the complex columns, convert to string representation
                for col in df.columns:
                    if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                        df[col] = df[col].apply(lambda x: str(x) if x is not None else None)
                
                # Convert datetime objects to strings
                for col in df.columns:
                    if df[col].apply(lambda x: isinstance(x, datetime) if x is not None else False).any():
                        df[col] = df[col].apply(lambda x: x.isoformat() if x is not None else None)
                
                # Write to database
                df.to_sql(f'mpxj_{table_name}', conn, if_exists='replace', index=False)
            
            # Write project properties
            project_props = project.getProjectProperties()
            props = {
                'name': project_props.getName(),
                'title': project_props.getTitle(),
                'subject': project_props.getSubject(),
                'author': project_props.getAuthor(),
                'last_saved_by': project_props.getLastAuthor(),
                'company': project_props.getCompany(),
                'comments': project_props.getComments(),
                'start_date': project_props.getStartDate().isoformat() if project_props.getStartDate() else None,
                'finish_date': project_props.getFinishDate().isoformat() if project_props.getFinishDate() else None,
                'status_date': project_props.getStatusDate().isoformat() if project_props.getStatusDate() else None,
                'current_date': project_props.getCurrentDate().isoformat() if project_props.getCurrentDate() else None,
                'file_name': project_file if isinstance(project_file, str) else 'project_object',
                'file_format': os.path.splitext(project_file)[1].lower() if isinstance(project_file, str) else None,
                'imported_at': datetime.now().isoformat(),
            }
            
            # Convert dict to DataFrame and write to database
            pd.DataFrame([props]).to_sql('mpxj_project_properties', conn, if_exists='replace', index=False)
            
            # Commit changes
            conn.commit()
            
        finally:
            # Close connection
            conn.close()

# Testing function
def test_mpxj_wrapper(test_file: str = None):
    """Test the MPXJ wrapper functionality"""
    if not HAS_MPXJ:
        print("MPXJ library not available. Install with 'pip install mpxj'")
        return
        
    converter = MPXJConverter()
    
    if test_file is None:
        # Create a simple test project
        project = ProjectFile()
        
        # Set project properties
        props = project.getProjectProperties()
        props.setName("Test Project")
        props.setAuthor("CSCSC AI Agent")
        
        # Add some tasks
        task1 = project.addTask()
        task1.setName("Task 1")
        task1.setID(1)
        task1.setDuration(Duration.getInstance(5, TimeUnit.DAYS))
        
        task2 = project.addTask()
        task2.setName("Task 2")
        task2.setID(2)
        task2.setDuration(Duration.getInstance(3, TimeUnit.DAYS))
        
        # Add a relationship
        task1.addSuccessor(task2)
        
        # Add a resource
        resource = project.addResource()
        resource.setName("Resource 1")
        resource.setID(1)
        
        # Add an assignment
        assignment = task1.addResourceAssignment(resource)
        assignment.setUnits(100)
        
        # Create a temporary MSPDI XML file
        temp_dir = tempfile.gettempdir()
        xml_file = os.path.join(temp_dir, "test_project.xml")
        converter.write_project(project, xml_file)
        print(f"Created test project file: {xml_file}")
        
        # Test reading the file
        test_file = xml_file
    
    # Read and display project information
    print(f"\nReading project file: {test_file}")
    project = converter.read_project(test_file)
    
    # Get project statistics
    stats = converter.get_project_statistics(project)
    print("\nProject Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Convert to dataframes
    print("\nConverting to DataFrames...")
    dfs = converter.project_to_dataframes(project)
    
    # Display task information
    print(f"\nTasks: {len(dfs['tasks'])} rows")
    if not dfs['tasks'].empty:
        print(dfs['tasks'][[c for c in ['id', 'name', 'start', 'finish', 'duration'] if c in dfs['tasks'].columns]].head())
    
    # Display resource information
    print(f"\nResources: {len(dfs['resources'])} rows")
    if not dfs['resources'].empty:
        print(dfs['resources'][[c for c in ['id', 'name', 'type'] if c in dfs['resources'].columns]].head())
    
    # Create SQLite database
    db_file = os.path.join(os.path.dirname(test_file), "test_project.db")
    print(f"\nImporting to database: {db_file}")
    converter.import_to_database(project, db_file)
    print("Import complete")
    
    # Test file format conversion if possible
    if test_file.lower().endswith(".xml"):
        mpx_file = test_file.replace(".xml", ".mpx")
        print(f"\nConverting {test_file} to {mpx_file}")
        converter.convert_file(test_file, mpx_file)
        print("Conversion complete")


if __name__ == "__main__":
    # Run test function if module is executed directly
    test_mpxj_wrapper()
