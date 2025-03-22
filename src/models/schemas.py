from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class EVMTechnique(str, Enum):
    ZERO_HUNDRED = "0/100"  # No credit until 100% complete
    FIFTY_FIFTY = "50/50"  # 50% when started, 50% when complete
    PERCENT_COMPLETE = "percent_complete"  # Based on % complete
    MILESTONE = "milestone"  # Credit at predefined milestones
    APPORTIONED_EFFORT = "apportioned_effort"  # Tied to another task's progress
    LEVEL_OF_EFFORT = "level_of_effort"  # Time-based, not deliverable-based


class Task(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    wbs_element: str  # Work Breakdown Structure element
    control_account: str  # Control account this task belongs to
    responsible_person: str  # Person responsible for the task
    planned_start_date: datetime
    planned_finish_date: datetime
    actual_start_date: Optional[datetime] = None
    actual_finish_date: Optional[datetime] = None
    budget_at_completion: float  # The budgeted cost for this task
    status: TaskStatus = TaskStatus.NOT_STARTED
    percent_complete: float = 0.0  # 0 to 1.0
    evm_technique: EVMTechnique = EVMTechnique.PERCENT_COMPLETE
    parent_id: Optional[str] = None  # For hierarchical tasks
    dependencies: List[str] = []  # IDs of tasks this task depends on


class ActualCost(BaseModel):
    task_id: str
    date: datetime
    amount: float
    description: Optional[str] = None
    source: str  # e.g., "SAP", "Timesheet", etc.


class EVMMetrics(BaseModel):
    task_id: str
    date: datetime
    bcws: float  # Budgeted Cost of Work Scheduled (Planned Value)
    bcwp: float  # Budgeted Cost of Work Performed (Earned Value)
    acwp: float  # Actual Cost of Work Performed (Actual Cost)
    bac: float  # Budget At Completion
    eac: float  # Estimate At Completion
    etc: float  # Estimate To Complete
    cv: float  # Cost Variance (BCWP - ACWP)
    sv: float  # Schedule Variance (BCWP - BCWS)
    cpi: float  # Cost Performance Index (BCWP / ACWP)
    spi: float  # Schedule Performance Index (BCWP / BCWS)
    tcpi: float  # To-Complete Performance Index
    vac: float  # Variance At Completion (BAC - EAC)


class ProjectData(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    start_date: datetime
    planned_finish_date: datetime
    actual_finish_date: Optional[datetime] = None
    budget_at_completion: float
    tasks: List[Task] = []


class VarianceExplanation(BaseModel):
    metric_id: str  # ID of the EVMMetrics record
    variance_type: str  # "cost" or "schedule"
    explanation: str  # AI-generated explanation of the variance
    factors: List[str]  # Contributing factors
    impact: str  # Impact assessment
    recommendations: List[str]  # Recommended actions
    confidence: float  # AI confidence in the explanation (0-1)


class Forecast(BaseModel):
    project_id: str
    date: datetime
    eac: float  # Estimate At Completion
    etc: float  # Estimate To Complete
    estimated_finish_date: datetime
    probability: float  # Probability of meeting this forecast (0-1)
    methodology: str  # Method used for forecasting (e.g., "CPI", "ML-regression")
    key_factors: List[str]  # Factors influencing this forecast


class UserQuery(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    response: str
    data: Optional[Dict[str, Any]] = None
    confidence: float = 1.0  # AI confidence in the response (0-1)
    sources: List[str] = []  # Sources of information for this response
