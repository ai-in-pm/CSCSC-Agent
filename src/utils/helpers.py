from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import random
import os
import json
from pathlib import Path

from src.models.schemas import Task, ProjectData, EVMMetrics, Forecast
from src.config.settings import settings


def format_currency(value: float) -> str:
    """Format a currency value with dollar sign and commas.
    
    Args:
        value: The value to format
        
    Returns:
        str: Formatted currency string
    """
    return f"${value:,.2f}"


def format_percent(value: float) -> str:
    """Format a value as a percentage.
    
    Args:
        value: The value to format (0.0 to 1.0)
        
    Returns:
        str: Formatted percentage string
    """
    return f"{value * 100:.1f}%"


def format_date(date: datetime) -> str:
    """Format a date in a human-readable format.
    
    Args:
        date: The date to format
        
    Returns:
        str: Formatted date string
    """
    return date.strftime("%B %d, %Y")


def format_duration(days: int) -> str:
    """Format a duration in days as a human-readable string.
    
    Args:
        days: Number of days
        
    Returns:
        str: Formatted duration string
    """
    if days < 0:
        return f"{abs(days)} days ahead of schedule"
    elif days > 0:
        return f"{days} days behind schedule"
    else:
        return "on schedule"


def generate_sample_data() -> ProjectData:
    """Generate sample project data for testing or demonstration.
    
    Returns:
        ProjectData: A sample project with tasks
    """
    # Current date as reference point
    now = datetime.now()
    
    # Create sample tasks
    tasks = [
        Task(
            id="T001",
            name="Requirements Analysis",
            wbs_element="1.1",
            control_account="CA001",
            responsible_person="John Analyst",
            planned_start_date=now - timedelta(days=30),
            planned_finish_date=now - timedelta(days=15),
            actual_start_date=now - timedelta(days=32),
            actual_finish_date=now - timedelta(days=14),
            budget_at_completion=15000.0,
            status="completed",
            percent_complete=1.0
        ),
        Task(
            id="T002",
            name="System Design",
            wbs_element="1.2",
            control_account="CA001",
            responsible_person="Sarah Designer",
            planned_start_date=now - timedelta(days=14),
            planned_finish_date=now + timedelta(days=1),
            actual_start_date=now - timedelta(days=13),
            budget_at_completion=30000.0,
            status="in_progress",
            percent_complete=0.8
        ),
        Task(
            id="T003",
            name="Frontend Development",
            wbs_element="1.3.1",
            control_account="CA002",
            responsible_person="Mike Developer",
            planned_start_date=now + timedelta(days=2),
            planned_finish_date=now + timedelta(days=22),
            budget_at_completion=40000.0,
            status="not_started",
            percent_complete=0.0
        ),
        Task(
            id="T004",
            name="Backend Development",
            wbs_element="1.3.2",
            control_account="CA002",
            responsible_person="Tom Developer",
            planned_start_date=now + timedelta(days=2),
            planned_finish_date=now + timedelta(days=32),
            budget_at_completion=50000.0,
            status="not_started",
            percent_complete=0.0
        ),
        Task(
            id="T005",
            name="Testing",
            wbs_element="1.4",
            control_account="CA003",
            responsible_person="Lisa Tester",
            planned_start_date=now + timedelta(days=33),
            planned_finish_date=now + timedelta(days=48),
            budget_at_completion=25000.0,
            status="not_started",
            percent_complete=0.0
        ),
        Task(
            id="T006",
            name="Deployment",
            wbs_element="1.5",
            control_account="CA003",
            responsible_person="David DevOps",
            planned_start_date=now + timedelta(days=49),
            planned_finish_date=now + timedelta(days=55),
            budget_at_completion=15000.0,
            status="not_started",
            percent_complete=0.0
        ),
        Task(
            id="T007",
            name="Documentation",
            wbs_element="1.6",
            control_account="CA004",
            responsible_person="Emily Writer",
            planned_start_date=now + timedelta(days=33),
            planned_finish_date=now + timedelta(days=55),
            budget_at_completion=10000.0,
            status="not_started",
            percent_complete=0.0
        ),
        Task(
            id="T008",
            name="Project Management",
            wbs_element="1.7",
            control_account="CA004",
            responsible_person="Robert Manager",
            planned_start_date=now - timedelta(days=30),
            planned_finish_date=now + timedelta(days=60),
            actual_start_date=now - timedelta(days=30),
            budget_at_completion=30000.0,
            status="in_progress",
            percent_complete=0.3
        )
    ]
    
    # Create sample project
    project = ProjectData(
        id="P001",
        name="Enterprise Software Development",
        description="Development of a new enterprise resource planning (ERP) system",
        start_date=now - timedelta(days=30),
        planned_finish_date=now + timedelta(days=60),
        budget_at_completion=215000.0,
        tasks=tasks
    )
    
    return project


def save_sample_data(file_path: Union[str, Path]):
    """Save sample project data to a JSON file.
    
    Args:
        file_path: Path to save the JSON file
    """
    # Generate sample data
    project = generate_sample_data()
    
    # Convert to dictionary (Pydantic models have a .dict() method)
    project_dict = project.dict()
    
    # Convert datetime objects to ISO format strings
    _convert_dates_to_iso(project_dict)
    
    # Ensure directory exists
    if isinstance(file_path, str):
        file_path = Path(file_path)
        
    os.makedirs(file_path.parent, exist_ok=True)
    
    # Save to file
    with open(file_path, 'w') as f:
        json.dump(project_dict, f, indent=2)
        
    print(f"Sample data saved to {file_path}")


def _convert_dates_to_iso(data: Dict[str, Any]):
    """Recursively convert datetime objects to ISO format strings in a dictionary.
    
    Args:
        data: Dictionary to process
    """
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        elif isinstance(value, dict):
            _convert_dates_to_iso(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    _convert_dates_to_iso(item)


def generate_evm_metrics_for_task(task: Task, as_of_date: datetime) -> EVMMetrics:
    """Generate sample EVM metrics for a task.
    
    Args:
        task: The task to generate metrics for
        as_of_date: The date to calculate metrics as of
        
    Returns:
        EVMMetrics: Sample EVM metrics
    """
    # Calculate planned values
    if not task.planned_start_date or not task.planned_finish_date or task.budget_at_completion <= 0:
        return None
        
    planned_duration = (task.planned_finish_date - task.planned_start_date).days
    if planned_duration <= 0:
        return None
        
    # Calculate BCWS (planned value)
    if as_of_date < task.planned_start_date:
        bcws = 0.0
    elif as_of_date >= task.planned_finish_date:
        bcws = task.budget_at_completion
    else:
        elapsed_days = (as_of_date - task.planned_start_date).days
        bcws = (elapsed_days / planned_duration) * task.budget_at_completion
    
    # Calculate BCWP (earned value)
    bcwp = task.percent_complete * task.budget_at_completion
    
    # Calculate ACWP (actual cost) with some random variation
    if task.percent_complete <= 0:
        acwp = 0.0
    else:
        # Add some variation to make it interesting
        cpi_factor = random.uniform(0.85, 1.15)
        acwp = bcwp / cpi_factor
    
    # Calculate variances
    cv = bcwp - acwp
    sv = bcwp - bcws
    
    # Calculate performance indices
    cpi = bcwp / acwp if acwp > 0 else 1.0
    spi = bcwp / bcws if bcws > 0 else 1.0
    
    # Calculate estimate at completion (EAC) and estimate to complete (ETC)
    if cpi < 0.8:
        # Pessimistic formula
        eac = acwp + ((task.budget_at_completion - bcwp) / (cpi * spi))
    elif cpi > 1.2:
        # Optimistic formula
        eac = acwp + ((task.budget_at_completion - bcwp) / cpi)
    else:
        # Typical formula
        eac = task.budget_at_completion / cpi
        
    etc = eac - acwp
    
    # Calculate to-complete performance index (TCPI)
    tcpi = (task.budget_at_completion - bcwp) / (task.budget_at_completion - acwp) if acwp < task.budget_at_completion else 1.0
    
    # Calculate variance at completion (VAC)
    vac = task.budget_at_completion - eac
    
    return EVMMetrics(
        task_id=task.id,
        date=as_of_date,
        bcws=bcws,
        bcwp=bcwp,
        acwp=acwp,
        bac=task.budget_at_completion,
        eac=eac,
        etc=etc,
        cv=cv,
        sv=sv,
        cpi=cpi,
        spi=spi,
        tcpi=tcpi,
        vac=vac
    )


def generate_forecast_for_project(project: ProjectData, as_of_date: datetime) -> Forecast:
    """Generate a sample forecast for a project.
    
    Args:
        project: The project to generate a forecast for
        as_of_date: The date to generate the forecast as of
        
    Returns:
        Forecast: Sample forecast
    """
    # Aggregate metrics across all tasks
    total_bcws = 0.0
    total_bcwp = 0.0
    total_acwp = 0.0
    
    for task in project.tasks:
        metrics = generate_evm_metrics_for_task(task, as_of_date)
        if metrics:
            total_bcws += metrics.bcws
            total_bcwp += metrics.bcwp
            total_acwp += metrics.acwp
    
    # Calculate project-level performance indices
    project_cpi = total_bcwp / total_acwp if total_acwp > 0 else 1.0
    project_spi = total_bcwp / total_bcws if total_bcws > 0 else 1.0
    
    # Calculate EAC using different methods
    eac_cpi = project.budget_at_completion / project_cpi if project_cpi > 0 else project.budget_at_completion
    eac_cpi_spi = project.budget_at_completion / (project_cpi * project_spi) if project_cpi * project_spi > 0 else project.budget_at_completion
    
    # Choose EAC and methodology based on performance
    if project_cpi < 0.9 and project_spi < 0.9:
        eac = eac_cpi_spi
        methodology = "CPI*SPI"
    elif project_cpi < 0.9:
        eac = eac_cpi
        methodology = "CPI"
    else:
        eac = (total_acwp + (project.budget_at_completion - total_bcwp))
        methodology = "Remaining Budget"
    
    # Calculate ETC
    etc = eac - total_acwp
    
    # Estimate finish date
    planned_duration = (project.planned_finish_date - project.start_date).days
    if project_spi > 0 and planned_duration > 0:
        estimated_duration = planned_duration / project_spi
        estimated_finish_date = project.start_date + timedelta(days=int(estimated_duration))
    else:
        estimated_finish_date = project.planned_finish_date
    
    # Generate key factors based on performance
    key_factors = []
    
    if project_cpi < 0.9:
        key_factors.append("Cost performance below threshold")
    elif project_cpi > 1.1:
        key_factors.append("Cost performance exceeding expectations")
        
    if project_spi < 0.9:
        key_factors.append("Schedule performance below threshold")
    elif project_spi > 1.1:
        key_factors.append("Schedule performance exceeding expectations")
        
    key_factors.append(f"Using {methodology} forecasting method")
    
    # Calculate probability based on variance and historical performance
    variance_factor = min(1.0, max(0.5, (project_cpi + project_spi) / 2))
    probability = 0.5 + (variance_factor * 0.3)
    
    return Forecast(
        project_id=project.id,
        date=as_of_date,
        eac=eac,
        etc=etc,
        estimated_finish_date=estimated_finish_date,
        probability=probability,
        methodology=methodology,
        key_factors=key_factors
    )


def generate_sample_physical_data() -> Dict[str, Any]:
    """Generate sample physical project data for demonstrations.
    
    Returns:
        Dict containing various physical project elements
    """
    # Generate sample environmental factors
    environmental_factors = [
        {
            "id": "E001",
            "project_id": "P001",
            "factor_type": "weather",
            "description": "Heavy rainfall causing flooding in excavation areas",
            "severity": "high",
            "start_date": datetime.now() - timedelta(days=2),
            "end_date": datetime.now() + timedelta(days=1),
            "duration_days": 3,
            "affected_wbs_elements": ["1.3.1", "1.3.2"],
            "affected_tasks": ["T003", "T004"],
            "status": "active"
        },
        {
            "id": "E002",
            "project_id": "P001",
            "factor_type": "site_condition",
            "description": "Unexpected rock formation requiring additional excavation equipment",
            "severity": "medium",
            "start_date": datetime.now() - timedelta(days=1),
            "duration_days": 4,
            "affected_wbs_elements": ["1.3.1"],
            "affected_tasks": ["T003"],
            "status": "active"
        },
        {
            "id": "E003",
            "project_id": "P001",
            "factor_type": "regulatory",
            "description": "Additional environmental permits required for wetland area",
            "severity": "medium",
            "start_date": datetime.now() + timedelta(days=5),
            "duration_days": 10,
            "affected_wbs_elements": ["1.2.3", "1.3.4"],
            "affected_tasks": ["T007", "T008"],
            "status": "pending"
        }
    ]
    
    # Generate sample delayed materials for supply chain impacts
    delayed_materials = [
        {
            "material_id": "M001",
            "project_id": "P001",
            "material_name": "Structural Steel",
            "supplier_name": "Steel Supply Co.",
            "original_delivery_date": datetime.now() + timedelta(days=3),
            "revised_delivery_date": datetime.now() + timedelta(days=8),
            "delay_days": 5,
            "dependent_tasks": ["T003", "T004"],
            "on_critical_path": True,
            "alternatives_available": False,
            "cost_impact": 7500.0,
            "description": "20-ton shipment of structural steel beams delayed due to transportation issues"
        },
        {
            "material_id": "M002",
            "project_id": "P001",
            "material_name": "Electrical Components",
            "supplier_name": "Electro Systems Inc.",
            "original_delivery_date": datetime.now() + timedelta(days=5),
            "revised_delivery_date": datetime.now() + timedelta(days=8),
            "delay_days": 3,
            "dependent_tasks": ["T005"],
            "on_critical_path": False,
            "alternatives_available": True,
            "cost_impact": 2500.0,
            "description": "Control panel components delayed due to manufacturing backlog"
        }
    ]
    
    # Generate sample site observations for progress verification
    site_observations = [
        {
            "observation_id": "O001",
            "project_id": "P001",
            "task_id": "T002",
            "observation_date": datetime.now() - timedelta(days=2),
            "observer": "John Smith",
            "observed_progress": 0.65,
            "reported_progress": 0.75,
            "cost_implication": 2500.0,
            "notes": "Site inspection revealed that only 65% of concrete work is complete, contrary to 75% reported. Additional rebar needed."
        },
        {
            "observation_id": "O002",
            "project_id": "P001",
            "task_id": "T002",
            "observation_date": datetime.now() - timedelta(days=1),
            "observer": "Jane Doe",
            "observed_progress": 0.60,
            "reported_progress": 0.75,
            "cost_implication": 0.0,
            "notes": "Second inspector confirmed progress discrepancy in concrete work."
        }
    ]
    
    # Generate sample site conditions for risk assessment
    site_conditions = {
        "scan_date": datetime.now(),
        "project_id": "P001",
        "weather": {
            "current": {
                "temperature": 72,
                "conditions": "Partly Cloudy",
                "precipitation": 0.1,
                "wind_speed": 8,
                "humidity": 65
            },
            "forecast": [
                {
                    "date": datetime.now() + timedelta(days=1),
                    "conditions": "Thunderstorms",
                    "high_temp": 78,
                    "low_temp": 65,
                    "precipitation_chance": 80,
                    "work_impact": "high"
                },
                {
                    "date": datetime.now() + timedelta(days=2),
                    "conditions": "Rain",
                    "high_temp": 72,
                    "low_temp": 62,
                    "precipitation_chance": 60,
                    "work_impact": "medium"
                },
                {
                    "date": datetime.now() + timedelta(days=3),
                    "conditions": "Partly Cloudy",
                    "high_temp": 75,
                    "low_temp": 60,
                    "precipitation_chance": 20,
                    "work_impact": "low"
                }
            ],
            "weather_alerts": [
                {
                    "type": "Thunderstorm Warning",
                    "severity": "moderate",
                    "issued_date": datetime.now(),
                    "expiry_date": datetime.now() + timedelta(days=1),
                    "description": "Thunderstorms with potential for heavy rain, lightning, and strong winds expected in the project area."
                }
            ]
        },
        "site_access": {
            "status": "limited",
            "restrictions": [
                "Heavy equipment access limited to north entrance only",
                "South access road closed due to utility work"
            ],
            "delivery_access": "restricted"
        },
        "labor": {
            "shortage": True,
            "affected_trades": [
                {
                    "trade_name": "Electricians",
                    "wbs_element": "1.4.1",
                    "impact_description": "electrical rough-in work"
                }
            ]
        },
        "equipment": {
            "issues": [
                {
                    "critical": True,
                    "no_alternative": True,
                    "wbs_element": "1.3.2",
                    "description": "Crane malfunction",
                    "recommended_action": "Schedule emergency repair or rent replacement"
                }
            ]
        },
        "materials": {
            "delayed": [
                {
                    "wbs_element": "1.5",
                    "criticality": "medium",
                    "description": "HVAC equipment delayed by 1 week",
                    "delay_days": 7,
                    "mitigation_strategy": "Resequence installation tasks to minimize impact"
                }
            ]
        },
        "iot_sensors": {
            "temperature_sensors": [
                {
                    "sensor_id": "TS001",
                    "location": "Concrete pour area - Section A",
                    "current_reading": 76,
                    "status": "normal",
                    "last_updated": datetime.now() - timedelta(minutes=15)
                },
                {
                    "sensor_id": "TS002",
                    "location": "Concrete pour area - Section B",
                    "current_reading": 79,
                    "status": "alert",
                    "alert_message": "Temperature exceeding optimal curing range",
                    "last_updated": datetime.now() - timedelta(minutes=10)
                }
            ],
            "moisture_sensors": [
                {
                    "sensor_id": "MS001",
                    "location": "Foundation - North side",
                    "current_reading": 45,
                    "status": "normal",
                    "last_updated": datetime.now() - timedelta(minutes=20)
                }
            ],
            "equipment_sensors": [
                {
                    "sensor_id": "ES001",
                    "equipment_id": "Crane-01",
                    "metrics": {
                        "utilization": 0.65,
                        "fuel_level": 0.42,
                        "maintenance_status": "warning",
                        "warning_detail": "Scheduled maintenance overdue by 2 days"
                    },
                    "last_updated": datetime.now() - timedelta(minutes=5)
                }
            ]
        }
    }
    
    # Resource productivity data
    resource_productivity = [
        {
            "resource_id": "R001",
            "resource_name": "Excavator #1",
            "resource_type": "heavy_equipment",
            "planned_productivity": 40.0,  # cubic yards per day
            "actual_productivity": 35.0,
            "productivity_index": 0.875,  # actual/planned
            "utilization_rate": 0.92,
            "downtime_hours": 4,
            "notes": "Performance affected by unexpected rock formation"
        },
        {
            "resource_id": "R002",
            "resource_name": "Concrete Crew A",
            "resource_type": "labor",
            "planned_productivity": 30.0,  # cubic yards per day
            "actual_productivity": 33.0,
            "productivity_index": 1.1,
            "utilization_rate": 0.95,
            "overtime_hours": 12,
            "notes": "Exceeding targets with current crew composition"
        },
        {
            "resource_id": "R003",
            "resource_name": "Crane #2",
            "resource_type": "heavy_equipment",
            "planned_productivity": 24.0,  # lifts per day
            "actual_productivity": 20.0,
            "productivity_index": 0.833,
            "utilization_rate": 0.85,
            "downtime_hours": 8,
            "notes": "Below planned performance due to operator inexperience"
        }
    ]
    
    # Physical vs reported progress
    physical_vs_reported = {
        "as_of_date": datetime.now(),
        "metrics": [
            {
                "date": datetime.now() - timedelta(days=30),
                "physical_percent_complete": 0.1,
                "reported_percent_complete": 0.1,
                "variance_percentage": 0.0
            },
            {
                "date": datetime.now() - timedelta(days=25),
                "physical_percent_complete": 0.15,
                "reported_percent_complete": 0.18,
                "variance_percentage": -3.0
            },
            {
                "date": datetime.now() - timedelta(days=20),
                "physical_percent_complete": 0.22,
                "reported_percent_complete": 0.27,
                "variance_percentage": -5.0
            },
            {
                "date": datetime.now() - timedelta(days=15),
                "physical_percent_complete": 0.30,
                "reported_percent_complete": 0.37,
                "variance_percentage": -7.0
            },
            {
                "date": datetime.now() - timedelta(days=10),
                "physical_percent_complete": 0.42,
                "reported_percent_complete": 0.48,
                "variance_percentage": -6.0
            },
            {
                "date": datetime.now() - timedelta(days=5),
                "physical_percent_complete": 0.51,
                "reported_percent_complete": 0.60,
                "variance_percentage": -9.0
            },
            {
                "date": datetime.now(),
                "physical_percent_complete": 0.62,
                "reported_percent_complete": 0.72,
                "variance_percentage": -10.0
            }
        ]
    }
    
    # Compile all data
    physical_data = {
        "project_id": "P001",
        "project_name": "Commercial Building Construction",
        "environmental_factors": environmental_factors,
        "delayed_materials": delayed_materials,
        "site_observations": site_observations,
        "site_conditions": site_conditions,
        "resource_productivity": resource_productivity,
        "physical_vs_reported_progress": physical_vs_reported
    }
    
    return physical_data


def save_sample_physical_data(file_path: Union[str, Path]) -> None:
    """Save sample physical project data to a JSON file.
    
    Args:
        file_path: Path to save the JSON file
    """
    file_path = Path(file_path)
    data = generate_sample_physical_data()
    
    # Convert data to serializable format
    serializable_data = data.copy()
    _convert_dates_to_iso(serializable_data)
    
    with open(file_path, 'w') as f:
        json.dump(serializable_data, f, indent=2)
        
    print(f"Sample physical project data saved to {file_path}")
