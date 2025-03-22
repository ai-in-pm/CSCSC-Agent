from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class EnvironmentalFactor(BaseModel):
    """Model for environmental factors impacting project performance."""
    id: str = Field(..., description="Unique identifier for the environmental factor")
    project_id: str = Field(..., description="ID of the project affected by this factor")
    factor_type: str = Field(..., description="Type of factor (weather, site_condition, regulatory, other)")
    description: str = Field(..., description="Detailed description of the environmental factor")
    severity: str = Field(..., description="Severity level (low, medium, high, critical)")
    start_date: datetime = Field(..., description="Date when the factor began affecting the project")
    end_date: Optional[datetime] = Field(None, description="Date when the factor stopped affecting the project")
    duration_days: Optional[int] = Field(None, description="Duration of the impact in days")
    affected_wbs_elements: Optional[List[str]] = Field(None, description="List of WBS elements affected by this factor")
    affected_tasks: Optional[List[str]] = Field(None, description="List of task IDs affected by this factor")
    mitigation_actions: Optional[List[str]] = Field(None, description="Actions taken to mitigate the impact")
    status: str = Field("active", description="Status of the factor (active, mitigated, resolved)")
    created_at: datetime = Field(default_factory=datetime.now, description="When this record was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When this record was last updated")


class SiteObservation(BaseModel):
    """Model for on-site observations related to project progress."""
    id: str = Field(..., description="Unique identifier for the observation")
    project_id: str = Field(..., description="ID of the project this observation relates to")
    task_id: Optional[str] = Field(None, description="ID of the specific task observed, if applicable")
    wbs_element: Optional[str] = Field(None, description="WBS element this observation relates to")
    observation_date: datetime = Field(..., description="Date and time of the observation")
    observer: str = Field(..., description="Name or ID of the person who made the observation")
    observation_type: str = Field(..., description="Type of observation (progress, quality, safety, etc.)")
    description: str = Field(..., description="Detailed description of what was observed")
    reported_progress: Optional[float] = Field(None, description="Progress as reported in the system (0.0 to 1.0)")
    observed_progress: Optional[float] = Field(None, description="Progress as observed on site (0.0 to 1.0)")
    cost_implication: Optional[float] = Field(None, description="Cost implication of the observation, if any")
    schedule_implication: Optional[int] = Field(None, description="Schedule implication in days, if any")
    photo_urls: Optional[List[str]] = Field(None, description="URLs to photos documenting the observation")
    action_required: Optional[bool] = Field(False, description="Whether this observation requires action")
    action_description: Optional[str] = Field(None, description="Description of required action")
    action_status: Optional[str] = Field(None, description="Status of required action")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime = Field(default_factory=datetime.now, description="When this record was created")


class SupplyChainIssue(BaseModel):
    """Model for supply chain issues affecting the project."""
    id: str = Field(..., description="Unique identifier for the supply chain issue")
    project_id: str = Field(..., description="ID of the project affected by this issue")
    material_name: str = Field(..., description="Name of the material or equipment affected")
    supplier_name: str = Field(..., description="Name of the supplier")
    issue_type: str = Field(..., description="Type of issue (delay, shortage, quality, price)")
    description: str = Field(..., description="Detailed description of the issue")
    identified_date: datetime = Field(..., description="When the issue was identified")
    expected_resolution_date: Optional[datetime] = Field(None, description="When resolution is expected")
    delay_days: Optional[int] = Field(None, description="Number of days delayed, if applicable")
    dependent_tasks: List[str] = Field([], description="IDs of tasks dependent on this material")
    on_critical_path: bool = Field(False, description="Whether this affects the critical path")
    alternatives_available: bool = Field(False, description="Whether alternatives are available")
    impact_level: str = Field(..., description="Impact level (low, medium, high, critical)")
    mitigation_strategy: Optional[str] = Field(None, description="Strategy to mitigate impact")
    mitigation_status: Optional[str] = Field(None, description="Status of mitigation efforts")
    created_at: datetime = Field(default_factory=datetime.now, description="When this record was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When this record was last updated")


class ResourceAllocation(BaseModel):
    """Model for resource allocation in physical projects."""
    id: str = Field(..., description="Unique identifier for this resource allocation")
    project_id: str = Field(..., description="ID of the project")
    resource_type: str = Field(..., description="Type of resource (labor, equipment, material)")
    resource_name: str = Field(..., description="Name of the specific resource")
    assigned_to: str = Field(..., description="Task ID or WBS element this resource is assigned to")
    quantity: float = Field(..., description="Quantity of resource allocated")
    unit: str = Field(..., description="Unit of measure for the quantity")
    allocation_start: datetime = Field(..., description="When allocation starts")
    allocation_end: datetime = Field(..., description="When allocation ends")
    utilization_target: float = Field(1.0, description="Target utilization rate (0.0 to 1.0)")
    utilization_actual: Optional[float] = Field(None, description="Actual utilization rate (0.0 to 1.0)")
    cost_rate: float = Field(..., description="Cost rate per unit per time period")
    time_period: str = Field("day", description="Time period for the cost rate (hour, day, week)")
    status: str = Field("planned", description="Status (planned, active, complete)")
    created_at: datetime = Field(default_factory=datetime.now, description="When this record was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When this record was last updated")


class SiteCondition(BaseModel):
    """Model for current site conditions."""
    id: str = Field(..., description="Unique identifier for site condition record")
    project_id: str = Field(..., description="ID of the project")
    date: datetime = Field(..., description="Date of the site condition assessment")
    weather: Dict[str, Any] = Field(..., description="Weather conditions (temperature, precipitation, etc.)")
    labor: Dict[str, Any] = Field(..., description="Labor status (availability, shortages, etc.)")
    equipment: Dict[str, Any] = Field(..., description="Equipment status (operational, issues)")
    materials: Dict[str, Any] = Field(..., description="Material status (on-site, delayed, etc.)")
    safety_issues: List[Dict[str, Any]] = Field([], description="Active safety issues on site")
    site_access: str = Field("normal", description="Site access status (normal, restricted, closed)")
    notes: Optional[str] = Field(None, description="General notes on site conditions")
    created_by: str = Field(..., description="ID or name of person who created this record")
    created_at: datetime = Field(default_factory=datetime.now, description="When this record was created")


class RiskAssessment(BaseModel):
    """Model for physical project risk assessment."""
    id: str = Field(..., description="Unique identifier for the risk assessment")
    project_id: str = Field(..., description="ID of the project")
    assessment_date: datetime = Field(..., description="Date of the risk assessment")
    assessor: str = Field(..., description="ID or name of the person who performed the assessment")
    wbs_element: str = Field(..., description="WBS element being assessed")
    risk_factor: str = Field(..., description="Primary risk factor (weather, labor, material, etc.)")
    risk_level: str = Field(..., description="Risk level (low, medium, high, critical)")
    description: str = Field(..., description="Detailed description of the risk")
    likelihood: float = Field(..., description="Likelihood of occurrence (0.0 to 1.0)")
    impact: float = Field(..., description="Impact severity if it occurs (0.0 to 1.0)")
    risk_score: float = Field(..., description="Combined risk score (likelihood * impact)")
    recommended_action: str = Field(..., description="Recommended risk mitigation action")
    action_status: Optional[str] = Field(None, description="Status of the mitigation action")
    created_at: datetime = Field(default_factory=datetime.now, description="When this record was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When this record was last updated")


class IotSensorData(BaseModel):
    """Model for IoT sensor data from the physical project."""
    id: str = Field(..., description="Unique identifier for this sensor reading")
    project_id: str = Field(..., description="ID of the project")
    sensor_id: str = Field(..., description="ID of the sensor")
    sensor_type: str = Field(..., description="Type of sensor (temperature, humidity, motion, etc.)")
    location: str = Field(..., description="Location of the sensor on site")
    timestamp: datetime = Field(..., description="Timestamp of the reading")
    reading_value: float = Field(..., description="Value of the reading")
    unit: str = Field(..., description="Unit of measure for the reading")
    wbs_element: Optional[str] = Field(None, description="WBS element associated with this sensor")
    status: str = Field("normal", description="Status of the reading (normal, warning, alert)")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime = Field(default_factory=datetime.now, description="When this record was created")


class PhysicalProgressMetrics(BaseModel):
    """Model for physical progress metrics beyond standard EVM."""
    id: str = Field(..., description="Unique identifier for these metrics")
    project_id: str = Field(..., description="ID of the project")
    task_id: Optional[str] = Field(None, description="ID of the task, if applicable")
    wbs_element: Optional[str] = Field(None, description="WBS element, if applicable")
    date: datetime = Field(..., description="Date of the metrics")
    physical_percent_complete: float = Field(..., description="Physical percent complete (0.0 to 1.0)")
    reported_percent_complete: float = Field(..., description="Percent complete as reported (0.0 to 1.0)")
    variance_percentage: float = Field(..., description="Variance between physical and reported (physical - reported)")
    physical_units_complete: Optional[float] = Field(None, description="Physical units completed")
    physical_units_total: Optional[float] = Field(None, description="Total physical units planned")
    unit_type: Optional[str] = Field(None, description="Type of units being measured")
    quality_index: Optional[float] = Field(None, description="Quality index (0.0 to 1.0)")
    productivity_rate: Optional[float] = Field(None, description="Productivity rate (units per time period)")
    productivity_variance: Optional[float] = Field(None, description="Variance from planned productivity rate")
    assessment_method: str = Field(..., description="Method used for assessment (visual, measurement, calculation)")
    assessor: str = Field(..., description="Person who performed the assessment")
    notes: Optional[str] = Field(None, description="Additional notes on the metrics")
    created_at: datetime = Field(default_factory=datetime.now, description="When this record was created")
