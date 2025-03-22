from typing import Dict, List, Any, Optional
from datetime import datetime

from src.models.schemas import EVMMetrics, VarianceExplanation, Forecast


class NLGGenerator:
    """Natural Language Generation engine for creating human-like EVM commentary."""

    def __init__(self):
        """Initialize the NLG generator with templates and language models."""
        # In a full implementation, this might load language models or templates
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, List[str]]:
        """Initialize the templates used for various types of commentary.
        
        Returns:
            Dict[str, List[str]]: Dictionary of template categories and their variations
        """
        return {
            # Status templates
            "status_on_track": [
                "The project is currently on track with key metrics within expected ranges.",
                "Performance indicators show the project is proceeding according to plan.",
                "The project is performing as expected against the baseline."
            ],
            "status_cost_issue": [
                "The project is experiencing cost overruns that require attention.",
                "Cost metrics indicate performance below the established baseline.",
                "Budget variances have been identified that need management focus."
            ],
            "status_schedule_issue": [
                "The project is behind schedule based on earned value metrics.",
                "Schedule performance indicates delays against the baseline.",
                "Timeline variances have been detected that may impact delivery dates."
            ],
            "status_both_issues": [
                "The project is facing both cost and schedule challenges.",
                "Performance metrics show variances in both budget and timeline.",
                "Both cost and schedule indicators are outside acceptable thresholds."
            ],
            
            # Metric templates
            "metric_cpi_good": [
                "CPI of {cpi:.2f} indicates cost efficiency.",
                "The Cost Performance Index is {cpi:.2f}, showing good budget management.",
                "With a CPI of {cpi:.2f}, the project is delivering more value than budgeted."
            ],
            "metric_cpi_bad": [
                "CPI of {cpi:.2f} shows cost inefficiency requiring intervention.",
                "The Cost Performance Index is {cpi:.2f}, indicating budget overruns.",
                "With a CPI of {cpi:.2f}, costs are exceeding planned values."
            ],
            "metric_spi_good": [
                "SPI of {spi:.2f} indicates the project is ahead of schedule.",
                "The Schedule Performance Index is {spi:.2f}, showing efficient time management.",
                "With an SPI of {spi:.2f}, work is being completed faster than planned."
            ],
            "metric_spi_bad": [
                "SPI of {spi:.2f} shows the project is behind schedule.",
                "The Schedule Performance Index is {spi:.2f}, indicating timeline delays.",
                "With an SPI of {spi:.2f}, work is progressing slower than planned."
            ],
            
            # Forecast templates
            "forecast_on_track": [
                "Current forecasts indicate the project will complete within budget and schedule constraints.",
                "Projected outcomes align with the baseline plan for both cost and schedule.",
                "Forecasts show the project is on track to meet its baseline objectives."
            ],
            "forecast_cost_overrun": [
                "The Estimate at Completion (EAC) of ${eac:,.2f} exceeds the budget by ${overrun:,.2f}.",
                "Forecast models predict a cost overrun of ${overrun:,.2f}, with a final cost of ${eac:,.2f}.",
                "Budget forecasts indicate the project will exceed its BAC by ${overrun:,.2f}, resulting in an EAC of ${eac:,.2f}."
            ],
            "forecast_schedule_delay": [
                "The project is forecast to complete on {finish_date}, which is {delay_days} days later than planned.",
                "Schedule projections indicate completion by {finish_date}, representing a {delay_days}-day delay.",
                "Timeline analysis suggests the project will finish on {finish_date}, {delay_days} days behind the baseline schedule."
            ],
            
            # Recommendation templates
            "recommendation_general": [
                "Based on current performance, it is recommended to {action}.",
                "The analysis suggests that management should {action}.",
                "To address the identified variances, consider {action}."
            ],
            "recommendation_specific": [
                "Specifically, {specific_action} could help improve the {area} performance.",
                "For the {area} concerns, implementing {specific_action} is recommended.",
                "{specific_action} would be beneficial to address the {area} challenges."
            ]
        }

    def _select_template(self, category: str, variables: Dict[str, Any] = None) -> str:
        """Select and fill a template from the specified category.
        
        Args:
            category: The template category to select from
            variables: Optional variables to fill into the template
            
        Returns:
            str: The filled template
        """
        if category not in self.templates or not self.templates[category]:
            return f"[No template available for {category}]"
            
        # Select a template (in a real implementation, we might choose based on context)
        import random
        template = random.choice(self.templates[category])
        
        # Fill in variables if provided
        if variables:
            try:
                return template.format(**variables)
            except KeyError as e:
                return f"[Template error: missing variable {e}]"
        
        return template

    def generate_status_update(self, metrics: EVMMetrics) -> str:
        """Generate a natural language status update based on EVM metrics.
        
        Args:
            metrics: The EVM metrics to generate status for
            
        Returns:
            str: A natural language status update
        """
        # Determine overall status
        cpi_good = metrics.cpi >= 0.95
        spi_good = metrics.spi >= 0.95
        
        if cpi_good and spi_good:
            status = self._select_template("status_on_track")
        elif not cpi_good and spi_good:
            status = self._select_template("status_cost_issue")
        elif cpi_good and not spi_good:
            status = self._select_template("status_schedule_issue")
        else:
            status = self._select_template("status_both_issues")
        
        # Add metric details
        cpi_template = "metric_cpi_good" if cpi_good else "metric_cpi_bad"
        spi_template = "metric_spi_good" if spi_good else "metric_spi_bad"
        
        cpi_text = self._select_template(cpi_template, {"cpi": metrics.cpi})
        spi_text = self._select_template(spi_template, {"spi": metrics.spi})
        
        # Combine into a coherent update
        update = f"{status} {cpi_text} {spi_text}"
        
        # Add variance information if significant
        if abs(metrics.cv) > 0.05 * metrics.bac:
            cv_percent = (metrics.cv / metrics.bac) * 100
            cv_direction = "under budget" if metrics.cv > 0 else "over budget"
            update += f" Cost variance is ${abs(metrics.cv):,.2f} ({abs(cv_percent):.1f}% {cv_direction})."
        
        if abs(metrics.sv) > 0.05 * metrics.bcws and metrics.bcws > 0:
            sv_percent = (metrics.sv / metrics.bcws) * 100
            sv_direction = "ahead of schedule" if metrics.sv > 0 else "behind schedule"
            update += f" Schedule variance is ${abs(metrics.sv):,.2f} ({abs(sv_percent):.1f}% {sv_direction})."
        
        return update

    def generate_forecast_commentary(self, forecast: Forecast, baseline_finish: datetime, 
                                   budget_at_completion: float) -> str:
        """Generate a natural language commentary on the project forecast.
        
        Args:
            forecast: The forecast to generate commentary for
            baseline_finish: The baseline finish date for comparison
            budget_at_completion: The budget at completion for comparison
            
        Returns:
            str: A natural language forecast commentary
        """
        # Determine if forecasts are within acceptable ranges
        cost_variance = forecast.eac - budget_at_completion
        cost_variance_percent = (cost_variance / budget_at_completion) * 100 if budget_at_completion > 0 else 0
        
        schedule_variance_days = (forecast.estimated_finish_date - baseline_finish).days
        
        # Generate forecast commentary
        if abs(cost_variance_percent) < 5 and abs(schedule_variance_days) < 10:
            commentary = self._select_template("forecast_on_track")
        else:
            commentary = ""
            
            # Add cost forecast if significant
            if cost_variance > 0 and cost_variance_percent >= 5:
                cost_text = self._select_template("forecast_cost_overrun", {
                    "eac": forecast.eac,
                    "overrun": cost_variance
                })
                commentary += cost_text + " "
            
            # Add schedule forecast if significant
            if schedule_variance_days >= 10:
                schedule_text = self._select_template("forecast_schedule_delay", {
                    "finish_date": forecast.estimated_finish_date.strftime("%B %d, %Y"),
                    "delay_days": schedule_variance_days
                })
                commentary += schedule_text
                
            if not commentary:  # Fallback if neither is significant but we already determined they weren't on track
                commentary = "The project is showing minor deviations from the baseline plan."
        
        # Add methodology and confidence information
        commentary += f" This forecast is based on {forecast.methodology} methodology "
        commentary += f"with {int(forecast.probability * 100)}% confidence."
        
        # Add key factors if available
        if forecast.key_factors:
            commentary += f" Key factors influencing this forecast include: {'; '.join(forecast.key_factors[:2])}"
            
        return commentary

    def generate_variance_explanation(self, explanation: VarianceExplanation) -> str:
        """Generate a natural language explanation of a variance.
        
        Args:
            explanation: The variance explanation to convert to natural language
            
        Returns:
            str: A natural language explanation of the variance
        """
        variance_type = "cost" if explanation.variance_type == "cost" else "schedule"
        
        # Core explanation
        output = f"{explanation.explanation} "
        
        # Add factors
        if explanation.factors and explanation.factors[0] != "Unknown factors":
            output += f"Contributing factors include: {', '.join(explanation.factors)}. "
        
        # Add impact
        output += f"{explanation.impact} "
        
        # Add recommendations if available
        if explanation.recommendations:
            output += f"\n\nRecommendations: \n"
            for i, rec in enumerate(explanation.recommendations, 1):
                output += f"{i}. {rec}\n"
                
        return output

    def generate_recommendations(self, metrics: EVMMetrics, 
                               explanation: Optional[VarianceExplanation] = None) -> str:
        """Generate natural language recommendations based on EVM metrics and explanations.
        
        Args:
            metrics: The EVM metrics to generate recommendations for
            explanation: Optional variance explanation with pre-generated recommendations
            
        Returns:
            str: Natural language recommendations
        """
        # If we have an explanation with recommendations, use those
        if explanation and explanation.recommendations:
            recommendations = "Based on the analysis, the following actions are recommended:\n"
            for i, rec in enumerate(explanation.recommendations, 1):
                recommendations += f"{i}. {rec}\n"
            return recommendations
        
        # Otherwise, generate basic recommendations based on metrics
        recommendations = []
        
        # Cost recommendations
        if metrics.cpi < 0.9:
            recommendations.append(self._select_template("recommendation_general", 
                                                      {"action": "review cost control measures"}))
            recommendations.append(self._select_template("recommendation_specific", 
                                                      {"specific_action": "conduct a detailed cost analysis", 
                                                       "area": "cost"}))
        
        # Schedule recommendations
        if metrics.spi < 0.9:
            recommendations.append(self._select_template("recommendation_general", 
                                                      {"action": "assess schedule recovery options"}))
            recommendations.append(self._select_template("recommendation_specific", 
                                                      {"specific_action": "evaluate critical path activities for acceleration", 
                                                       "area": "schedule"}))
        
        # General recommendations for smaller variances
        if metrics.cpi < 0.95 or metrics.spi < 0.95:
            recommendations.append(self._select_template("recommendation_general", 
                                                      {"action": "increase monitoring frequency for affected work packages"}))
        
        # Format recommendations
        if recommendations:
            output = "Based on current performance metrics, the following recommendations are offered:\n"
            for i, rec in enumerate(recommendations, 1):
                output += f"{i}. {rec}\n"
            return output
        else:
            return "Current performance is within acceptable thresholds. Continue with the established management approach."

    def generate_stream_response(self, update_text: str) -> List[str]:
        """Generate a streamed response that simulates real-time typing.
        
        This breaks up a response into smaller chunks for streaming output
        that gives the appearance of being typed in real-time.
        
        Args:
            update_text: The full text to be streamed
            
        Returns:
            List[str]: The text broken into chunks for streaming
        """
        # Break the text into sentences
        import re
        sentences = re.split(r'(?<=[.!?])\s+', update_text)
        
        # Break long sentences into phrases
        chunks = []
        for sentence in sentences:
            if len(sentence) < 50:  # Short sentence
                chunks.append(sentence + " ")
            else:  # Long sentence, break at commas or other logical points
                phrases = re.split(r'(?<=[,;:])\s+', sentence)
                for phrase in phrases:
                    chunks.append(phrase + " ")
        
        return chunks

    def generate_dashboard_summary(self, metrics: EVMMetrics, forecast: Forecast) -> str:
        """Generate a concise summary for a dashboard display.
        
        Args:
            metrics: The EVM metrics to summarize
            forecast: The project forecast to include
            
        Returns:
            str: A concise dashboard summary
        """
        # Status indicators
        status = "ON TRACK" if metrics.cpi >= 0.95 and metrics.spi >= 0.95 else "NEEDS ATTENTION"
        
        # Generate summary
        summary = f"STATUS: {status}\n\n"
        summary += f"CPI: {metrics.cpi:.2f} | SPI: {metrics.spi:.2f}\n"
        summary += f"CV: ${metrics.cv:,.2f} | SV: ${metrics.sv:,.2f}\n\n"
        summary += f"EAC: ${forecast.eac:,.2f}\n"
        summary += f"Forecast Completion: {forecast.estimated_finish_date.strftime('%b %d, %Y')}\n"
        summary += f"Confidence: {int(forecast.probability * 100)}%"
        
        return summary

    def generate_alert_message(self, anomaly: Dict[str, Any]) -> str:
        """Generate an alert message for a detected anomaly.
        
        Args:
            anomaly: The anomaly details
            
        Returns:
            str: An alert message
        """
        anomaly_type = anomaly.get("type", "unknown")
        description = anomaly.get("description", "An anomaly has been detected")
        severity = anomaly.get("severity", 0.5)
        
        # Convert severity to text
        severity_text = "Critical" if severity > 0.8 else "High" if severity > 0.5 else "Moderate"
        
        alert = f"{severity_text} ALERT: {description}\n"
        
        # Add type-specific details
        if anomaly_type == "cpi_change":
            from_value = anomaly.get("from_value", 0)
            to_value = anomaly.get("to_value", 0)
            alert += f"CPI changed from {from_value:.2f} to {to_value:.2f} in a single reporting period.\n"
            alert += f"This represents a {'significant improvement' if to_value > from_value else 'concerning deterioration'} in cost performance."
            
        elif anomaly_type == "spi_change":
            from_value = anomaly.get("from_value", 0)
            to_value = anomaly.get("to_value", 0)
            alert += f"SPI changed from {from_value:.2f} to {to_value:.2f} in a single reporting period.\n"
            alert += f"This represents a {'significant improvement' if to_value > from_value else 'concerning deterioration'} in schedule performance."
            
        elif anomaly_type == "cv_trend_reversal":
            from_trend = anomaly.get("from_trend", "unknown")
            to_trend = anomaly.get("to_trend", "unknown")
            alert += f"Cost variance trend has reversed from {from_trend} to {to_trend}.\n"
            alert += f"This may indicate a fundamental change in project cost performance."
            
        # Add date information
        if "date" in anomaly:
            alert += f"\n\nDetected on: {anomaly['date'].strftime('%Y-%m-%d')}"
            
        return alert

    def generate_environmental_impact_explanation(self, project_id: str, impact_analysis: Dict[str, Any]) -> str:
        """Generate a natural language explanation of environmental impact analysis.
        
        Args:
            project_id: ID of the project being analyzed
            impact_analysis: The environmental impact analysis results
            
        Returns:
            str: Natural language explanation of the analysis
        """
        # Extract key information from the analysis
        schedule_impact = impact_analysis.get("schedule_impact", {})
        cost_impact = impact_analysis.get("cost_impact", {})
        affected_wbs = impact_analysis.get("affected_wbs_elements", [])
        recommendations = impact_analysis.get("recommendations", [])
        
        # Generate the explanation
        explanation = []
        
        # Overall impact summary
        schedule_days = schedule_impact.get("total_days", 0)
        schedule_level = schedule_impact.get("impact_level", "unknown")
        cost_amount = cost_impact.get("total_amount", 0)
        cost_level = cost_impact.get("impact_level", "unknown")
        
        explanation.append(f"Based on current environmental conditions, the project is experiencing a {schedule_level} schedule impact of {schedule_days} days and a {cost_level} cost impact of ${cost_amount:,.2f}.")
        
        # Add schedule impact details
        schedule_desc = schedule_impact.get("description", "")
        if schedule_desc:
            explanation.append(schedule_desc)
        
        # Add cost impact details
        cost_desc = cost_impact.get("description", "")
        if cost_desc:
            explanation.append(cost_desc)
        
        # Add affected WBS elements
        if affected_wbs:
            wbs_count = len(affected_wbs)
            if wbs_count <= 3:
                wbs_list = ", ".join(affected_wbs)
                explanation.append(f"The environmental factors are specifically affecting these work elements: {wbs_list}.")
            else:
                explanation.append(f"The environmental factors are affecting {wbs_count} work elements across the project.")
        
        # Add recommendations
        if recommendations:
            if len(recommendations) == 1:
                explanation.append(f"Recommended action: {recommendations[0]}")
            else:
                rec_text = "\n- " + "\n- ".join(recommendations)
                explanation.append(f"Recommended actions: {rec_text}")
        
        return " ".join(explanation)

    def generate_supply_chain_impact_explanation(self, project_id: str, impact_analysis: Dict[str, Any]) -> str:
        """Generate a natural language explanation of supply chain impact analysis.
        
        Args:
            project_id: ID of the project being analyzed
            impact_analysis: The supply chain impact analysis results
            
        Returns:
            str: Natural language explanation of the analysis
        """
        # Extract key information from the analysis
        critical_path_impact = impact_analysis.get("critical_path_impact", False)
        delay_days = impact_analysis.get("schedule_delay_days", 0)
        affected_tasks = impact_analysis.get("affected_tasks", [])
        strategies = impact_analysis.get("mitigation_strategies", [])
        
        # Generate the explanation
        explanation = []
        
        # Overall impact summary
        if critical_path_impact:
            explanation.append(f"Supply chain issues are critically impacting the project schedule, with an estimated delay of {delay_days} days on the critical path.")
        else:
            explanation.append(f"Current supply chain issues are affecting the project but not impacting the critical path. The estimated schedule impact is {delay_days} days on non-critical activities.")
        
        # Add affected tasks information
        tasks_count = len(affected_tasks)
        if tasks_count > 0:
            explanation.append(f"These delays are affecting {tasks_count} tasks within the project schedule.")
            
        # Add mitigation strategies
        if strategies:
            if len(strategies) == 1:
                explanation.append(f"Recommended mitigation strategy: {strategies[0]}")
            else:
                strat_text = "\n- " + "\n- ".join(strategies)
                explanation.append(f"Recommended mitigation strategies: {strat_text}")
                
        # Add final impact assessment
        if critical_path_impact and delay_days > 10:
            explanation.append("This situation requires immediate management attention and potential project replanning to address the significant schedule impact.")
        elif critical_path_impact:
            explanation.append("This situation should be closely monitored, and mitigation strategies should be implemented promptly to minimize schedule impact.")
        else:
            explanation.append("While not currently affecting the critical path, these supply chain issues should be monitored to prevent cascading delays into critical activities.")
        
        return " ".join(explanation)

    def generate_site_adjustment_explanation(self, task_id: str, adjustment: Dict[str, Any]) -> str:
        """Generate a natural language explanation of site progress adjustments.
        
        Args:
            task_id: ID of the task being adjusted
            adjustment: The site progress adjustment data
            
        Returns:
            str: Natural language explanation of the adjustments
        """
        # Extract key information from the adjustment
        percent_adj = adjustment.get("percent_complete_adjustment", 0.0)
        cost_adj = adjustment.get("actual_cost_adjustment", 0.0)
        confidence = adjustment.get("confidence_level", "medium")
        justification = adjustment.get("justification", "")
        
        # Generate the explanation
        explanation = []
        
        # Overall adjustment summary
        if abs(percent_adj) > 0.05 or abs(cost_adj) > 5000:
            explanation.append(f"Based on physical site observations, significant adjustments to the reported EVM metrics for task {task_id} are recommended.")
        else:
            explanation.append(f"Based on physical site observations, minor adjustments to the reported EVM metrics for task {task_id} are recommended.")
        
        # Add progress adjustment details
        if abs(percent_adj) > 0.001:
            direction = "increase" if percent_adj > 0 else "decrease"
            explanation.append(f"The physical percent complete should be {direction}d by {abs(percent_adj)*100:.1f} percentage points.")
            
        # Add cost adjustment details
        if abs(cost_adj) > 0.001:
            direction = "increase" if cost_adj > 0 else "decrease"
            explanation.append(f"The actual cost should be {direction}d by ${abs(cost_adj):,.2f}.")
            
        # Add confidence level
        explanation.append(f"These recommendations are made with {confidence} confidence based on site observations.")
        
        # Add justification if available
        if justification:
            explanation.append(f"Justification: {justification}")
            
        # Add final recommendation
        if confidence == "high":
            explanation.append("These adjustments should be applied to the EVM system immediately to maintain data accuracy.")
        elif confidence == "medium":
            explanation.append("Consider applying these adjustments after verification by the project manager.")
        else:  # low confidence
            explanation.append("Further on-site verification is recommended before applying these adjustments.")
        
        return " ".join(explanation)

    def generate_risk_assessment_explanation(self, project_id: str, at_risk_elements: List[Dict[str, Any]]) -> str:
        """Generate a natural language explanation of at-risk WBS elements.
        
        Args:
            project_id: ID of the project being analyzed
            at_risk_elements: List of at-risk WBS elements with their details
            
        Returns:
            str: Natural language explanation of the risk assessment
        """
        # Process the at-risk elements
        high_risk = []
        medium_risk = []
        low_risk = []
        
        for element in at_risk_elements:
            risk_level = element.get("risk_level", "")
            if risk_level == "high" or risk_level == "critical":
                high_risk.append(element)
            elif risk_level == "medium":
                medium_risk.append(element)
            else:
                low_risk.append(element)
        
        # Generate the explanation
        explanation = []
        
        # Overall risk summary
        total_elements = len(at_risk_elements)
        if total_elements == 0:
            explanation.append("Based on current site conditions, no WBS elements are identified as being at significant risk.")
            return " ".join(explanation)
            
        explanation.append(f"Based on current site conditions, {total_elements} WBS elements have been identified as at risk of schedule or cost impacts.")
        
        # Summarize risk levels
        if high_risk:
            explanation.append(f"{len(high_risk)} elements are at high or critical risk.")
        if medium_risk:
            explanation.append(f"{len(medium_risk)} elements are at medium risk.")
        if low_risk:
            explanation.append(f"{len(low_risk)} elements are at low risk.")
            
        # Detail high risk elements
        if high_risk:
            explanation.append("The following WBS elements require immediate attention:")
            for element in high_risk:
                wbs = element.get("wbs_element", "")
                desc = element.get("description", "")
                action = element.get("recommended_action", "")
                explanation.append(f"- WBS {wbs}: {desc}. Recommended action: {action}")
                
        # Add risk factors summary
        risk_factors = {}
        for element in at_risk_elements:
            factor = element.get("risk_factor", "other")
            if factor in risk_factors:
                risk_factors[factor] += 1
            else:
                risk_factors[factor] = 1
                
        if risk_factors:
            factor_text = ", ".join([f"{count} related to {factor}" for factor, count in risk_factors.items()])
            explanation.append(f"The identified risks include: {factor_text}.")
            
        # Add final guidance
        if high_risk:
            explanation.append("These high-risk elements should be addressed immediately to prevent significant schedule and cost impacts.")
        elif medium_risk:
            explanation.append("The medium-risk elements should be closely monitored and mitigation plans developed within the next planning cycle.")
        else:
            explanation.append("Continue monitoring these low-risk elements as part of regular project oversight.")
        
        return " ".join(explanation)
