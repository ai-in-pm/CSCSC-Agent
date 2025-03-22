import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from src.models.schemas import Task, EVMMetrics, VarianceExplanation, Forecast
from src.evm_engine.calculator import EVMCalculator


class EVMAnalyzer:
    """AI/ML module for analyzing EVM data, detecting anomalies, and forecasting outcomes."""

    def __init__(self, evm_calculator: EVMCalculator = None):
        """Initialize the EVM Analyzer with optional calculator reference.
        
        Args:
            evm_calculator: Optional reference to an EVMCalculator instance
        """
        self.evm_calculator = evm_calculator or EVMCalculator()
        self.scaler = StandardScaler()
        self.cost_model = None  # Will be initialized when trained
        self.schedule_model = None  # Will be initialized when trained

    def analyze_variance(self, metrics: EVMMetrics, 
                        context_data: Optional[Dict[str, Any]] = None) -> VarianceExplanation:
        """Analyze cost and schedule variances to determine causes and impacts.
        
        Args:
            metrics: The EVM metrics to analyze
            context_data: Optional contextual data (e.g., risk logs, issue records)
            
        Returns:
            VarianceExplanation: Explanation of the variance with recommendations
        """
        # Determine which variance to focus on (cost or schedule)
        # For this example, we'll analyze the most significant variance
        cv_significant = self.evm_calculator.is_variance_significant(metrics.cv, metrics.bcwp)
        sv_significant = self.evm_calculator.is_variance_significant(metrics.sv, metrics.bcws)
        
        # If both are significant, analyze the one with greater relative impact
        if cv_significant and sv_significant:
            cv_relative = abs(metrics.cv / metrics.bcwp) if metrics.bcwp != 0 else 0
            sv_relative = abs(metrics.sv / metrics.bcws) if metrics.bcws != 0 else 0
            
            variance_type = "cost" if cv_relative > sv_relative else "schedule"
        elif cv_significant:
            variance_type = "cost"
        elif sv_significant:
            variance_type = "schedule"
        else:
            # If neither variance is significant, still provide an explanation but note this
            variance_type = "cost" if abs(metrics.cv) > abs(metrics.sv) else "schedule"
        
        # Generate explanation based on variance type and available context
        if variance_type == "cost":
            explanation, factors, impact, confidence = self._analyze_cost_variance(metrics, context_data)
        else:
            explanation, factors, impact, confidence = self._analyze_schedule_variance(metrics, context_data)
            
        # Generate recommendations based on the analysis
        recommendations = self._generate_recommendations(variance_type, metrics, factors)
        
        return VarianceExplanation(
            metric_id=f"{metrics.task_id}_{metrics.date.isoformat()}",
            variance_type=variance_type,
            explanation=explanation,
            factors=factors,
            impact=impact,
            recommendations=recommendations,
            confidence=confidence
        )

    def _analyze_cost_variance(self, metrics: EVMMetrics, 
                             context_data: Optional[Dict[str, Any]]) -> Tuple[str, List[str], str, float]:
        """Analyze cost variance to determine causes and impacts.
        
        Args:
            metrics: The EVM metrics to analyze
            context_data: Optional contextual data
            
        Returns:
            Tuple[str, List[str], str, float]: explanation, factors, impact, confidence
        """
        # Default values in case we don't have enough context
        explanation = "Cost variance detected in this work package."
        factors = ["Unknown factors"]
        impact = "Impact not yet determined."
        confidence = 0.5
        
        # If we have a significant negative cost variance (over budget)
        if metrics.cv < 0 and metrics.cpi < 1.0:
            explanation = f"This work package is over budget with a CPI of {metrics.cpi:.2f}, indicating cost inefficiency."
            
            # Determine possible factors based on patterns and context
            potential_factors = [
                "Labor costs exceeding estimates",
                "Material price increases",
                "Rework due to quality issues",
                "Unexpected technical challenges",
                "Scope creep without budget adjustment"
            ]
            
            # In a real implementation, we would use context_data and perhaps NLP to filter these factors
            # For this example, we'll select a subset based on simple heuristics
            severity = abs(metrics.cv) / metrics.bac  # Relative to BAC
            
            # More severe variances likely have multiple factors
            num_factors = min(3, max(1, int(severity * 5)))
            factors = potential_factors[:num_factors]
            
            # Impact assessment
            impact_percent = abs(metrics.cv / metrics.bac) * 100 if metrics.bac > 0 else 0
            
            if metrics.vac < 0 and abs(metrics.vac) > 0.1 * metrics.bac:
                impact = f"Significant impact on final cost. Current projection shows {abs(metrics.vac):.2f} cost overrun at completion ({impact_percent:.1f}% of budget)."
            else:
                impact = f"Moderate impact on cost performance. May need budget adjustment of approximately {abs(metrics.cv):.2f} ({impact_percent:.1f}% of budget)."
            
            confidence = 0.7  # Higher confidence for negative cost variance with clear metrics
            
        # Positive cost variance (under budget)
        elif metrics.cv > 0 and metrics.cpi > 1.0:
            explanation = f"This work package is under budget with a CPI of {metrics.cpi:.2f}, indicating cost efficiency."
            
            factors = [
                "Efficient resource utilization",
                "Lower than estimated material costs",
                "Process improvements"
            ]
            
            impact = f"Positive impact. Continued performance may result in {metrics.vac:.2f} cost savings at completion."
            confidence = 0.65  # Slightly lower confidence for positive variance (may be due to incomplete work)
            
        # Return the analysis results
        return explanation, factors, impact, confidence

    def _analyze_schedule_variance(self, metrics: EVMMetrics, 
                                context_data: Optional[Dict[str, Any]]) -> Tuple[str, List[str], str, float]:
        """Analyze schedule variance to determine causes and impacts.
        
        Args:
            metrics: The EVM metrics to analyze
            context_data: Optional contextual data
            
        Returns:
            Tuple[str, List[str], str, float]: explanation, factors, impact, confidence
        """
        # Default values
        explanation = "Schedule variance detected in this work package."
        factors = ["Unknown factors"]
        impact = "Impact not yet determined."
        confidence = 0.5
        
        # If we have a significant negative schedule variance (behind schedule)
        if metrics.sv < 0 and metrics.spi < 1.0:
            explanation = f"This work package is behind schedule with an SPI of {metrics.spi:.2f}."
            
            # Determine possible factors
            potential_factors = [
                "Late start on critical activities",
                "Resource constraints or unavailability",
                "Dependencies with other delayed tasks",
                "Technical challenges requiring more time",
                "Optimistic duration estimates"
            ]
            
            # Similar to cost variance, use simple heuristics for factors
            severity = abs(metrics.sv) / metrics.bcws if metrics.bcws > 0 else 0
            num_factors = min(3, max(1, int(severity * 5)))
            factors = potential_factors[:num_factors]
            
            # Impact assessment
            delay_factor = 1 / metrics.spi if metrics.spi > 0.1 else 10  # Avoid division by very small numbers
            delay_estimate = delay_factor - 1  # e.g., SPI=0.5 implies 2x duration, so 100% delay
            
            if delay_estimate > 0.5:  # More than 50% delay
                impact = f"Significant schedule impact. At current rate, may delay completion by approximately {int(delay_estimate * 100)}%."
            else:
                impact = f"Moderate schedule impact. May delay completion by approximately {int(delay_estimate * 100)}%."
            
            confidence = 0.7
            
        # Positive schedule variance (ahead of schedule)
        elif metrics.sv > 0 and metrics.spi > 1.0:
            explanation = f"This work package is ahead of schedule with an SPI of {metrics.spi:.2f}."
            
            factors = [
                "Efficient execution of activities",
                "Early start on critical tasks",
                "Conservative duration estimates"
            ]
            
            ahead_factor = metrics.spi - 1  # e.g., SPI=1.2 implies 20% ahead
            impact = f"Positive schedule impact. Work progressing {int(ahead_factor * 100)}% faster than planned."
            confidence = 0.65
            
        # Return the analysis results
        return explanation, factors, impact, confidence

    def _generate_recommendations(self, variance_type: str, metrics: EVMMetrics, 
                                factors: List[str]) -> List[str]:
        """Generate recommendations based on variance analysis.
        
        Args:
            variance_type: Type of variance ("cost" or "schedule")
            metrics: The EVM metrics
            factors: Identified factors contributing to the variance
            
        Returns:
            List[str]: List of recommended actions
        """
        recommendations = []
        
        # Cost variance recommendations
        if variance_type == "cost" and metrics.cv < 0:
            # Recommendations for negative cost variance
            recommendations.append("Review cost estimation methodology for similar future tasks")
            
            if "Labor costs exceeding estimates" in factors:
                recommendations.append("Analyze labor utilization and productivity")
                recommendations.append("Consider adjusting resource mix or skills")
                
            if "Material price increases" in factors:
                recommendations.append("Explore alternative suppliers or materials")
                recommendations.append("Consider bulk purchasing to reduce unit costs")
                
            if metrics.vac < 0 and abs(metrics.vac) > 0.1 * metrics.bac:
                recommendations.append("Initiate formal EAC review and potential budget change request")
                recommendations.append("Assess scope for possible reduction to align with budget constraints")
                
        # Schedule variance recommendations
        elif variance_type == "schedule" and metrics.sv < 0:
            # Recommendations for negative schedule variance
            recommendations.append("Review and update remaining duration estimates")
            
            if "Resource constraints" in factors or "Resource unavailability" in factors:
                recommendations.append("Assess resource allocation and consider adding resources")
                
            if "Dependencies with other delayed tasks" in factors:
                recommendations.append("Review critical path and task dependencies")
                recommendations.append("Consider fast-tracking or schedule compression techniques")
                
            if metrics.spi < 0.8:  # Significant delay
                recommendations.append("Develop a recovery plan with specific milestones")
                recommendations.append("Consider re-baselining if recovery is not feasible")
                
        # Default recommendations if specific ones weren't generated
        if not recommendations:
            if metrics.cv < 0 or metrics.sv < 0:
                recommendations.append("Investigate root causes and document lessons learned")
                recommendations.append("Monitor closely in the next reporting period")
            else:
                recommendations.append("Document successful practices for future reference")
                recommendations.append("Consider adjusting estimates for similar future tasks")
                
        return recommendations

    def train_forecast_models(self, historical_data: List[Dict[str, Any]]):
        """Train ML models for cost and schedule forecasting using historical project data.
        
        Args:
            historical_data: List of dictionaries containing historical project performance data
        """
        if not historical_data or len(historical_data) < 10:
            # Not enough data for meaningful training
            self.cost_model = LinearRegression()  # Fallback to simple linear model
            self.schedule_model = LinearRegression()
            return
        
        # Extract features and targets for training
        features = []
        cost_targets = []
        schedule_targets = []
        
        for project in historical_data:
            # Extract features like CPI, SPI, % complete, etc.
            project_features = [
                project.get('cpi', 1.0),
                project.get('spi', 1.0),
                project.get('percent_complete', 0.0),
                project.get('cv_trend', 0.0),  # Trend of CV over time
                project.get('sv_trend', 0.0),  # Trend of SV over time
                project.get('risk_score', 0.0),  # Project risk score
                project.get('complexity', 0.5)   # Project complexity score
            ]
            
            features.append(project_features)
            
            # Extract targets - actual final outcomes
            cost_targets.append(project.get('final_cost_ratio', 1.0))  # Actual/Budget ratio
            schedule_targets.append(project.get('final_duration_ratio', 1.0))  # Actual/Planned duration ratio
        
        # Convert to numpy arrays
        X = np.array(features)
        y_cost = np.array(cost_targets)
        y_schedule = np.array(schedule_targets)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train models
        self.cost_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.cost_model.fit(X_scaled, y_cost)
        
        self.schedule_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.schedule_model.fit(X_scaled, y_schedule)

    def generate_forecast(self, project_id: str, tasks: List[Task], metrics_dict: Dict[str, EVMMetrics],
                         context_data: Optional[Dict[str, Any]] = None) -> Forecast:
        """Generate a project forecast using ML models and/or EVM formulas.
        
        Args:
            project_id: The ID of the project to forecast
            tasks: List of all tasks in the project
            metrics_dict: Dictionary mapping task IDs to their EVM metrics
            context_data: Optional contextual data for better forecasting
            
        Returns:
            Forecast: Project forecast with EAC, finish date, and confidence
        """
        # If we don't have enough metrics, return a basic formula-based forecast
        if not metrics_dict or len(metrics_dict) == 0:
            return self._generate_basic_forecast(project_id, tasks)
        
        # Prepare data for aggregated analysis
        metrics_list = list(metrics_dict.values())
        aggregated_metrics = self.evm_calculator.aggregate_metrics(metrics_list)
        
        if not aggregated_metrics:
            return self._generate_basic_forecast(project_id, tasks)
        
        # Determine the forecast method based on available models and data
        use_ml = self.cost_model is not None and self.schedule_model is not None
        
        if use_ml:
            return self._generate_ml_forecast(project_id, tasks, aggregated_metrics, context_data)
        else:
            return self._generate_formula_forecast(project_id, tasks, aggregated_metrics)

    def _generate_basic_forecast(self, project_id: str, tasks: List[Task]) -> Forecast:
        """Generate a basic forecast when we don't have EVM metrics available.
        
        Args:
            project_id: The ID of the project to forecast
            tasks: List of all tasks in the project
            
        Returns:
            Forecast: Basic project forecast
        """
        # Find the latest planned finish date among all tasks
        if not tasks:
            # No tasks, return a default forecast
            return Forecast(
                project_id=project_id,
                date=datetime.now(),
                eac=0.0,
                etc=0.0,
                estimated_finish_date=datetime.now() + timedelta(days=30),
                probability=0.5,
                methodology="default",
                key_factors=["No tasks available for forecasting"]
            )
        
        # Calculate total BAC and estimated finish date
        total_bac = sum(task.budget_at_completion for task in tasks)
        latest_finish = max(task.planned_finish_date for task in tasks)
        
        return Forecast(
            project_id=project_id,
            date=datetime.now(),
            eac=total_bac,  # Assume on budget for now
            etc=total_bac,  # Assume no actual costs yet
            estimated_finish_date=latest_finish,
            probability=0.6,
            methodology="planned-values",
            key_factors=["Based on planned values only", "No performance data available"]
        )

    def _generate_formula_forecast(self, project_id: str, tasks: List[Task], 
                                metrics: EVMMetrics) -> Forecast:
        """Generate a forecast using traditional EVM formulas.
        
        Args:
            project_id: The ID of the project to forecast
            tasks: List of all tasks in the project
            metrics: Aggregated EVM metrics for the project
            
        Returns:
            Forecast: Project forecast based on EVM formulas
        """
        # Use CPI method for cost forecast
        eac = metrics.eac
        etc = metrics.etc
        
        # Find the critical task and adjust its finish date based on SPI
        critical_tasks = [task for task in tasks if not task.dependencies]  # Simplified critical path
        
        if not critical_tasks:
            critical_tasks = tasks  # If no leaf tasks, use all tasks
        
        # Find the latest planned finish among critical tasks
        latest_task = max(critical_tasks, key=lambda t: t.planned_finish_date)
        
        # Get a reference to a task that might have an actual start date
        started_tasks = [task for task in tasks if task.actual_start_date]
        reference_task = started_tasks[0] if started_tasks else latest_task
        
        # Estimate finish date based on SPI
        planned_duration = (latest_task.planned_finish_date - reference_task.planned_start_date).days
        adjusted_duration = planned_duration / metrics.spi if metrics.spi > 0.1 else planned_duration * 10
        
        start_date = reference_task.actual_start_date or reference_task.planned_start_date
        estimated_finish_date = start_date + timedelta(days=adjusted_duration)
        
        # Probability based on performance indices
        probability = 0.5  # Base probability
        
        # Adjust probability based on performance
        if metrics.cpi > 0.95 and metrics.spi > 0.95:  # Good performance
            probability += 0.2
        elif metrics.cpi < 0.8 or metrics.spi < 0.8:  # Poor performance
            probability -= 0.2
        
        # Key factors
        key_factors = [
            f"CPI = {metrics.cpi:.2f}, indicating {'favorable' if metrics.cpi >= 1 else 'unfavorable'} cost efficiency",
            f"SPI = {metrics.spi:.2f}, indicating {'ahead of' if metrics.spi >= 1 else 'behind'} schedule"
        ]
        
        if metrics.cpi < 0.9 and metrics.spi < 0.9:
            key_factors.append("Both cost and schedule performance are concerning")
        
        return Forecast(
            project_id=project_id,
            date=datetime.now(),
            eac=eac,
            etc=etc,
            estimated_finish_date=estimated_finish_date,
            probability=max(0.1, min(0.9, probability)),  # Constrain to 0.1-0.9 range
            methodology="evm-formula",
            key_factors=key_factors
        )

    def _generate_ml_forecast(self, project_id: str, tasks: List[Task], metrics: EVMMetrics,
                           context_data: Optional[Dict[str, Any]]) -> Forecast:
        """Generate a forecast using ML models for greater accuracy.
        
        Args:
            project_id: The ID of the project to forecast
            tasks: List of all tasks in the project
            metrics: Aggregated EVM metrics for the project
            context_data: Optional contextual data for better forecasting
            
        Returns:
            Forecast: Project forecast based on ML models
        """
        # Prepare features for prediction
        features = [
            metrics.cpi,
            metrics.spi,
            self._calculate_percent_complete(tasks),
            context_data.get('cv_trend', 0.0) if context_data else 0.0,
            context_data.get('sv_trend', 0.0) if context_data else 0.0,
            context_data.get('risk_score', 0.5) if context_data else 0.5,
            context_data.get('complexity', 0.5) if context_data else 0.5
        ]
        
        # Scale features using the same scaler used during training
        features_scaled = self.scaler.transform(np.array(features).reshape(1, -1))
        
        # Predict cost and schedule ratios
        cost_ratio = self.cost_model.predict(features_scaled)[0]
        schedule_ratio = self.schedule_model.predict(features_scaled)[0]
        
        # Calculate EAC based on ML prediction
        total_bac = sum(task.budget_at_completion for task in tasks)
        eac = total_bac * cost_ratio
        etc = eac - metrics.acwp
        
        # Calculate finish date based on ML prediction
        # Find a reference task for dating
        started_tasks = [task for task in tasks if task.actual_start_date]
        reference_task = started_tasks[0] if started_tasks else tasks[0]
        
        # Get original planned duration and adjust by ML prediction
        planned_duration = sum((task.planned_finish_date - task.planned_start_date).days for task in tasks) / len(tasks)
        adjusted_duration = planned_duration * schedule_ratio
        
        start_date = reference_task.actual_start_date or reference_task.planned_start_date
        estimated_finish_date = start_date + timedelta(days=adjusted_duration)
        
        # Calculate probability based on model confidence
        # This would typically come from the model's confidence score or prediction interval
        probability = 0.6  # Base probability
        
        # Adjust based on performance consistency
        consistency = context_data.get('performance_consistency', 0.5) if context_data else 0.5
        probability += consistency * 0.2
        
        # Key factors that influenced this forecast
        key_factors = [
            f"ML forecast predicts final cost will be {cost_ratio:.2f}x the original budget",
            f"ML forecast predicts schedule will be {schedule_ratio:.2f}x the original duration"
        ]
        
        # Add feature importance insights (in a real system, we'd extract from the model)
        top_feature = "CPI" if metrics.cpi < metrics.spi else "SPI"
        key_factors.append(f"{top_feature} is the most influential factor in this forecast")
        
        if context_data and context_data.get('risk_events'):
            key_factors.append("Risk events have been factored into this forecast")
        
        return Forecast(
            project_id=project_id,
            date=datetime.now(),
            eac=eac,
            etc=etc,
            estimated_finish_date=estimated_finish_date,
            probability=max(0.1, min(0.9, probability)),  # Constrain to 0.1-0.9 range
            methodology="machine-learning",
            key_factors=key_factors
        )

    def _calculate_percent_complete(self, tasks: List[Task]) -> float:
        """Calculate overall percent complete for a list of tasks.
        
        Args:
            tasks: List of tasks to calculate percent complete for
            
        Returns:
            float: Overall percent complete (0-1)
        """
        if not tasks:
            return 0.0
            
        total_budget = sum(task.budget_at_completion for task in tasks)
        
        if total_budget == 0:
            # Equal weighting if no budget information
            return sum(task.percent_complete for task in tasks) / len(tasks)
            
        # Weighted by budget
        weighted_sum = sum(task.percent_complete * task.budget_at_completion for task in tasks)
        return weighted_sum / total_budget

    def detect_anomalies(self, metrics_history: List[EVMMetrics]) -> List[Dict[str, Any]]:
        """Detect anomalies in EVM metrics over time.
        
        Args:
            metrics_history: List of historical metrics ordered by date
            
        Returns:
            List[Dict[str, Any]]: List of anomalies detected with details
        """
        if not metrics_history or len(metrics_history) < 3:
            return []  # Need at least 3 data points for trend analysis
            
        anomalies = []
        
        # Extract time series for key metrics
        dates = [m.date for m in metrics_history]
        cpi_values = [m.cpi for m in metrics_history]
        spi_values = [m.spi for m in metrics_history]
        cv_values = [m.cv for m in metrics_history]
        sv_values = [m.sv for m in metrics_history]
        
        # Check for sudden changes in CPI
        for i in range(1, len(cpi_values)):
            cpi_change = cpi_values[i] - cpi_values[i-1]
            
            # If CPI changes by more than 0.2 in one period, flag as anomaly
            if abs(cpi_change) > 0.2:
                anomalies.append({
                    "date": dates[i],
                    "type": "cpi_change",
                    "description": f"Sudden {'improvement' if cpi_change > 0 else 'deterioration'} in CPI",
                    "from_value": cpi_values[i-1],
                    "to_value": cpi_values[i],
                    "severity": abs(cpi_change) / 0.2  # Normalized severity
                })
        
        # Check for sudden changes in SPI
        for i in range(1, len(spi_values)):
            spi_change = spi_values[i] - spi_values[i-1]
            
            # If SPI changes by more than 0.2 in one period, flag as anomaly
            if abs(spi_change) > 0.2:
                anomalies.append({
                    "date": dates[i],
                    "type": "spi_change",
                    "description": f"Sudden {'improvement' if spi_change > 0 else 'deterioration'} in SPI",
                    "from_value": spi_values[i-1],
                    "to_value": spi_values[i],
                    "severity": abs(spi_change) / 0.2  # Normalized severity
                })
        
        # Check for trend reversals in cost variance
        if len(cv_values) >= 3:
            for i in range(2, len(cv_values)):
                # Check if trend direction changed
                prev_trend = cv_values[i-1] - cv_values[i-2]
                current_trend = cv_values[i] - cv_values[i-1]
                
                if (prev_trend > 0 and current_trend < 0) or (prev_trend < 0 and current_trend > 0):
                    anomalies.append({
                        "date": dates[i],
                        "type": "cv_trend_reversal",
                        "description": "Cost variance trend reversal detected",
                        "from_trend": "improving" if prev_trend > 0 else "deteriorating",
                        "to_trend": "deteriorating" if current_trend < 0 else "improving",
                        "severity": min(1.0, (abs(prev_trend) + abs(current_trend)) / 1000)  # Normalize based on typical CV values
                    })
        
        # Sort anomalies by date (newest first)
        anomalies.sort(key=lambda x: x["date"], reverse=True)
        
        return anomalies
