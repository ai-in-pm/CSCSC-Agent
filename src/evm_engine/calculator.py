from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from src.models.schemas import Task, ActualCost, EVMMetrics, EVMTechnique


class EVMCalculator:
    """Core EVM calculation engine that computes standard earned value metrics."""

    def __init__(self, threshold: float = 0.1):
        """Initialize the EVM calculator with a variance threshold.
        
        Args:
            threshold: The threshold for considering variances significant (default: 0.1 or 10%)
        """
        self.threshold = threshold

    def calculate_bcws(self, task: Task, as_of_date: datetime) -> float:
        """Calculate Budgeted Cost of Work Scheduled (Planned Value) for a task.
        
        Args:
            task: The task to calculate BCWS for
            as_of_date: The date to calculate BCWS as of
            
        Returns:
            float: The BCWS value
        """
        # If as_of_date is before planned start, BCWS is 0
        if as_of_date < task.planned_start_date:
            return 0.0
        
        # If as_of_date is after planned finish, BCWS is the full BAC
        if as_of_date >= task.planned_finish_date:
            return task.budget_at_completion
        
        # Otherwise, calculate based on linear interpolation between start and finish
        total_planned_days = (task.planned_finish_date - task.planned_start_date).days
        if total_planned_days <= 0:  # Safeguard against zero or negative duration
            return task.budget_at_completion
        
        days_elapsed = (as_of_date - task.planned_start_date).days
        planned_pct_complete = min(1.0, max(0.0, days_elapsed / total_planned_days))
        
        return task.budget_at_completion * planned_pct_complete

    def calculate_bcwp(self, task: Task) -> float:
        """Calculate Budgeted Cost of Work Performed (Earned Value) for a task.
        
        Args:
            task: The task to calculate BCWP for
            
        Returns:
            float: The BCWP value
        """
        # Calculate based on the EVM technique specified for the task
        if task.evm_technique == EVMTechnique.ZERO_HUNDRED:
            # 0/100 rule: No credit until 100% complete
            return task.budget_at_completion if task.percent_complete == 1.0 else 0.0
            
        elif task.evm_technique == EVMTechnique.FIFTY_FIFTY:
            # 50/50 rule: 50% when started, 50% when complete
            if task.percent_complete == 0.0:
                return 0.0
            elif task.percent_complete == 1.0:
                return task.budget_at_completion
            else:
                return task.budget_at_completion * 0.5
                
        elif task.evm_technique == EVMTechnique.PERCENT_COMPLETE:
            # Based on percent complete
            return task.budget_at_completion * task.percent_complete
            
        elif task.evm_technique == EVMTechnique.LEVEL_OF_EFFORT:
            # Time-based, based on elapsed calendar time
            if not task.actual_start_date:
                return 0.0
                
            total_planned_days = (task.planned_finish_date - task.planned_start_date).days
            if total_planned_days <= 0:
                return 0.0
                
            current_date = datetime.now()
            if task.actual_finish_date:
                current_date = task.actual_finish_date
                
            days_elapsed = (current_date - task.actual_start_date).days
            time_pct_complete = min(1.0, max(0.0, days_elapsed / total_planned_days))
            
            return task.budget_at_completion * time_pct_complete
            
        # Default to percent complete method if unknown technique
        return task.budget_at_completion * task.percent_complete

    def calculate_acwp(self, task_id: str, actual_costs: List[ActualCost], as_of_date: datetime) -> float:
        """Calculate Actual Cost of Work Performed for a task.
        
        Args:
            task_id: The ID of the task to calculate ACWP for
            actual_costs: List of all actual costs recorded
            as_of_date: The date to calculate ACWP as of
            
        Returns:
            float: The ACWP value
        """
        # Sum all actual costs for this task up to as_of_date
        task_costs = [cost.amount for cost in actual_costs 
                    if cost.task_id == task_id and cost.date <= as_of_date]
        
        return sum(task_costs)

    def calculate_metrics(self, task: Task, actual_costs: List[ActualCost], 
                         as_of_date: datetime) -> EVMMetrics:
        """Calculate all EVM metrics for a task as of a specific date.
        
        Args:
            task: The task to calculate metrics for
            actual_costs: List of actual costs recorded
            as_of_date: The date to calculate metrics as of
            
        Returns:
            EVMMetrics: All calculated EVM metrics
        """
        # Calculate base metrics
        bcws = self.calculate_bcws(task, as_of_date)
        bcwp = self.calculate_bcwp(task)
        acwp = self.calculate_acwp(task.id, actual_costs, as_of_date)
        bac = task.budget_at_completion
        
        # Calculate variances
        cv = bcwp - acwp  # Cost Variance
        sv = bcwp - bcws  # Schedule Variance
        
        # Calculate performance indices (with safety checks for division by zero)
        cpi = bcwp / acwp if acwp > 0 else 1.0
        spi = bcwp / bcws if bcws > 0 else 1.0
        
        # Calculate forecasts
        # Estimate at Completion (EAC) using CPI method
        eac = bac / cpi if cpi > 0 else float('inf')
        
        # Estimate To Complete (ETC)
        etc = eac - acwp
        
        # To-Complete Performance Index (TCPI)
        tcpi = (bac - bcwp) / (eac - acwp) if (eac - acwp) > 0 else float('inf')
        
        # Variance at Completion (VAC)
        vac = bac - eac
        
        return EVMMetrics(
            task_id=task.id,
            date=as_of_date,
            bcws=bcws,
            bcwp=bcwp,
            acwp=acwp,
            bac=bac,
            eac=eac,
            etc=etc,
            cv=cv,
            sv=sv,
            cpi=cpi,
            spi=spi,
            tcpi=tcpi,
            vac=vac
        )

    def is_variance_significant(self, variance: float, base_value: float) -> bool:
        """Determine if a variance is significant based on the threshold.
        
        Args:
            variance: The variance amount
            base_value: The base value to compare against
            
        Returns:
            bool: True if the variance is significant, False otherwise
        """
        if base_value == 0:
            return abs(variance) > 0
        
        relative_variance = abs(variance / base_value)
        return relative_variance > self.threshold

    def analyze_project_metrics(self, tasks: List[Task], actual_costs: List[ActualCost],
                              as_of_date: datetime = None) -> Dict[str, EVMMetrics]:
        """Calculate EVM metrics for all tasks in a project.
        
        Args:
            tasks: List of all tasks in the project
            actual_costs: List of all actual costs recorded
            as_of_date: The date to calculate metrics as of (default: current date)
            
        Returns:
            Dict[str, EVMMetrics]: Dictionary mapping task IDs to their metrics
        """
        if as_of_date is None:
            as_of_date = datetime.now()
            
        return {task.id: self.calculate_metrics(task, actual_costs, as_of_date) for task in tasks}

    def aggregate_metrics(self, metrics: List[EVMMetrics]) -> Optional[EVMMetrics]:
        """Aggregate EVM metrics from multiple tasks (e.g., for a control account or project).
        
        Args:
            metrics: List of EVMMetrics objects to aggregate
            
        Returns:
            Optional[EVMMetrics]: The aggregated metrics, or None if the list is empty
        """
        if not metrics:
            return None
            
        # Use the first metric's date and task_id (with prefix to indicate it's aggregated)
        reference_metric = metrics[0]
        
        # Sum up the base values
        total_bcws = sum(m.bcws for m in metrics)
        total_bcwp = sum(m.bcwp for m in metrics)
        total_acwp = sum(m.acwp for m in metrics)
        total_bac = sum(m.bac for m in metrics)
        
        # Calculate aggregated variances
        cv = total_bcwp - total_acwp
        sv = total_bcwp - total_bcws
        
        # Calculate aggregated indices
        cpi = total_bcwp / total_acwp if total_acwp > 0 else 1.0
        spi = total_bcwp / total_bcws if total_bcws > 0 else 1.0
        
        # Calculate aggregated forecasts
        eac = total_bac / cpi if cpi > 0 else float('inf')
        etc = eac - total_acwp
        tcpi = (total_bac - total_bcwp) / (eac - total_acwp) if (eac - total_acwp) > 0 else float('inf')
        vac = total_bac - eac
        
        return EVMMetrics(
            task_id="aggregate",
            date=reference_metric.date,
            bcws=total_bcws,
            bcwp=total_bcwp,
            acwp=total_acwp,
            bac=total_bac,
            eac=eac,
            etc=etc,
            cv=cv,
            sv=sv,
            cpi=cpi,
            spi=spi,
            tcpi=tcpi,
            vac=vac
        )

    def forecast_completion_date(self, task: Task, metrics: EVMMetrics) -> Tuple[datetime, float]:
        """Forecast the completion date for a task based on its current performance.
        
        Args:
            task: The task to forecast completion for
            metrics: The current EVM metrics for the task
            
        Returns:
            Tuple[datetime, float]: Estimated completion date and confidence (0-1)
        """
        # If SPI is 0 or very close to 0, we can't make a reasonable forecast
        if metrics.spi < 0.01:
            # Return a very far future date with low confidence
            future_date = datetime.now() + timedelta(days=365*10)  # 10 years in future
            return future_date, 0.01
        
        # If task is complete, return actual finish date
        if task.percent_complete >= 1.0 and task.actual_finish_date:
            return task.actual_finish_date, 1.0
        
        # Calculate remaining duration based on SPI
        if not task.actual_start_date:
            # Task hasn't started yet, estimate based on planned dates adjusted by SPI
            planned_duration = (task.planned_finish_date - task.planned_start_date).days
            adjusted_duration = planned_duration / metrics.spi
            
            # Estimated start remains the planned start
            est_start = task.planned_start_date
            est_finish = est_start + timedelta(days=adjusted_duration)
            
            # Lower confidence since task hasn't started
            confidence = 0.7
        else:
            # Task has started, calculate based on actual start and progress
            current_date = datetime.now()
            elapsed_days = (current_date - task.actual_start_date).days
            
            # If no progress made, can't use SPI effectively
            if metrics.bcwp == 0:
                return task.planned_finish_date, 0.5
            
            # Calculate percent of work remaining
            remaining_percent = 1.0 - task.percent_complete
            
            # If progress is 0% after starting, use a conservative estimate
            if task.percent_complete == 0:
                days_to_completion = (task.planned_finish_date - current_date).days
                est_finish = current_date + timedelta(days=days_to_completion * 1.5)  # Add 50% buffer
                return est_finish, 0.4
            
            # Calculate days per % complete so far
            days_per_percent = elapsed_days / task.percent_complete
            
            # Apply SPI adjustment
            adjusted_days_remaining = remaining_percent * days_per_percent / metrics.spi
            
            est_finish = current_date + timedelta(days=adjusted_days_remaining)
            
            # Confidence based on % complete and SPI stability
            confidence = 0.5 + task.percent_complete * 0.5  # Higher % complete, higher confidence
        
        return est_finish, confidence
