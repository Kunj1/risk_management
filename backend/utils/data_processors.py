"""
Data processing utilities for the Project Risk Management System.
These utilities help transform raw data into useful insights for risk management.
"""
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from backend.data.models import (Alert, MarketIndicator, Project, Risk,
                          RiskCategory, RiskProbability, RiskSeverity)


class MarketDataProcessor:
    """Process external market data to identify potential risks."""
    
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))
    
    def process_financial_news(self, news_data: List[Dict]) -> List[Dict]:
        """
        Analyze financial news articles for risk indicators.
        
        Args:
            news_data: List of news articles with title, content, and date fields
            
        Returns:
            List of risk indicators with category, severity, and relevance
        """
        risk_indicators = []
        
        # Define keywords for different risk categories
        financial_risk_keywords = ['bankruptcy', 'debt', 'deficit', 'recession', 'inflation']
        market_risk_keywords = ['market crash', 'volatility', 'downturn', 'bear market']
        regulatory_risk_keywords = ['regulation', 'compliance', 'lawsuit', 'legal action', 'fine']
        
        for article in news_data:
            content = article.get('content', '').lower()
            title = article.get('title', '').lower()
            date = article.get('date', datetime.now())
            
            # Calculate risk severity based on keyword frequency and recency
            risk_indicators.extend(self._extract_risk_indicators(content, title, date, 
                                                               financial_risk_keywords, 
                                                               RiskCategory.FINANCIAL))
            risk_indicators.extend(self._extract_risk_indicators(content, title, date, 
                                                               market_risk_keywords, 
                                                               RiskCategory.MARKET))
            risk_indicators.extend(self._extract_risk_indicators(content, title, date, 
                                                               regulatory_risk_keywords, 
                                                               RiskCategory.LEGAL))
        
        return risk_indicators
    
    def _extract_risk_indicators(self, content: str, title: str, date: datetime, 
                              keywords: List[str], category: RiskCategory) -> List[Dict]:
        """Extract risk indicators based on keyword matches."""
        indicators = []
        
        # Calculate days since publication (for recency weighting)
        days_old = (datetime.now() - date).days if isinstance(date, datetime) else 0
        recency_weight = max(0, 1 - (days_old / 30))  # Higher weight for more recent news
        
        for keyword in keywords:
            title_matches = len(re.findall(r'\b' + keyword + r'\b', title))
            content_matches = len(re.findall(r'\b' + keyword + r'\b', content))
            
            # Title matches are weighted more heavily
            total_matches = (title_matches * 3) + content_matches
            
            if total_matches > 0:
                # Calculate severity based on matches and recency
                raw_severity = total_matches * recency_weight
                
                severity = RiskSeverity.LOW
                if raw_severity >= 5:
                    severity = RiskSeverity.CRITICAL
                elif raw_severity >= 3:
                    severity = RiskSeverity.HIGH
                elif raw_severity >= 1:
                    severity = RiskSeverity.MEDIUM
                
                indicators.append({
                    'keyword': keyword,
                    'category': category,
                    'matches': total_matches,
                    'severity': severity,
                    'date': date,
                    'relevance_score': raw_severity
                })
        
        return indicators
    
    def analyze_economic_indicators(self, indicators: List[MarketIndicator]) -> List[Dict]:
        """
        Analyze economic indicators to identify potential market risks.
        
        Args:
            indicators: List of MarketIndicator objects
            
        Returns:
            List of risk assessments based on indicators
        """
        risk_assessments = []
        
        # Group indicators by category
        indicators_by_category = {}
        for indicator in indicators:
            if indicator.category not in indicators_by_category:
                indicators_by_category[indicator.category] = []
            indicators_by_category[indicator.category].append(indicator)
        
        # Analyze each category
        for category, category_indicators in indicators_by_category.items():
            # Calculate average change
            avg_change = np.mean([ind.change_percentage for ind in category_indicators])
            
            # Calculate volatility (standard deviation of changes)
            volatility = np.std([ind.change_percentage for ind in category_indicators])
            
            # Determine risk probability based on volatility
            probability = RiskProbability.UNLIKELY
            if volatility > 10:
                probability = RiskProbability.VERY_LIKELY
            elif volatility > 5:
                probability = RiskProbability.LIKELY
            elif volatility > 2:
                probability = RiskProbability.POSSIBLE
            
            # Determine risk severity based on average change direction and magnitude
            severity = RiskSeverity.LOW
            if abs(avg_change) > 10:
                severity = RiskSeverity.CRITICAL
            elif abs(avg_change) > 5:
                severity = RiskSeverity.HIGH
            elif abs(avg_change) > 2:
                severity = RiskSeverity.MEDIUM
            
            risk_assessments.append({
                'category': category,
                'avg_change': avg_change,
                'volatility': volatility,
                'probability': probability,
                'severity': severity,
                'impacted_indicators': [ind.name for ind in category_indicators]
            })
        
        return risk_assessments


class ProjectDataProcessor:
    """Process internal project data to identify potential risks."""
    
    def analyze_project_metrics(self, project: Project) -> List[Dict]:
        """
        Analyze project metrics to identify potential internal risks.
        
        Args:
            project: Project object with current metrics
            
        Returns:
            List of risk indicators based on project metrics
        """
        risk_indicators = []
        
        # Check budget overrun risk
        if project.budget > 0:
            budget_usage_percentage = (project.expenditure_to_date / project.budget) * 100
            expected_completion_percentage = self._calculate_expected_completion_percentage(project)
            
            # Budget is being consumed faster than project completion
            if budget_usage_percentage > expected_completion_percentage + 10:
                budget_variance = budget_usage_percentage - expected_completion_percentage
                
                severity = RiskSeverity.LOW
                if budget_variance > 30:
                    severity = RiskSeverity.CRITICAL
                elif budget_variance > 20:
                    severity = RiskSeverity.HIGH
                elif budget_variance > 10:
                    severity = RiskSeverity.MEDIUM
                
                risk_indicators.append({
                    'type': 'budget_overrun',
                    'category': RiskCategory.FINANCIAL,
                    'severity': severity,
                    'description': f"Budget usage ({budget_usage_percentage:.1f}%) exceeds expected project completion ({expected_completion_percentage:.1f}%)",
                    'metrics': {
                        'budget_usage': budget_usage_percentage,
                        'expected_completion': expected_completion_percentage,
                        'variance': budget_variance
                    }
                })
        
        # Check schedule delay risk
        if project.expected_end_date:
            days_remaining = (project.expected_end_date - datetime.now()).days
            total_days = (project.expected_end_date - project.start_date).days
            
            if total_days > 0:
                time_elapsed_percentage = ((total_days - days_remaining) / total_days) * 100
                expected_completion_percentage = self._calculate_expected_completion_percentage(project)
                
                # Project completion is lagging behind schedule
                if expected_completion_percentage < time_elapsed_percentage - 10:
                    schedule_variance = time_elapsed_percentage - expected_completion_percentage
                    
                    severity = RiskSeverity.LOW
                    if schedule_variance > 30:
                        severity = RiskSeverity.CRITICAL
                    elif schedule_variance > 20:
                        severity = RiskSeverity.HIGH
                    elif schedule_variance > 10:
                        severity = RiskSeverity.MEDIUM
                    
                    risk_indicators.append({
                        'type': 'schedule_delay',
                        'category': RiskCategory.SCHEDULE,
                        'severity': severity,
                        'description': f"Project completion ({expected_completion_percentage:.1f}%) lags behind time elapsed ({time_elapsed_percentage:.1f}%)",
                        'metrics': {
                            'time_elapsed': time_elapsed_percentage,
                            'completion_percentage': expected_completion_percentage,
                            'variance': schedule_variance
                        }
                    })
        
        # Check resource allocation risk
        if not project.team_members:
            risk_indicators.append({
                'type': 'resource_shortage',
                'category': RiskCategory.RESOURCE,
                'severity': RiskSeverity.HIGH,
                'description': "No team members assigned to the project",
                'metrics': {
                    'team_size': 0
                }
            })
        
        return risk_indicators
    
    def _calculate_expected_completion_percentage(self, project: Project) -> float:
        """
        Estimate project completion percentage based on available metrics.
        This is a simplified calculation and would be more complex in a real system.
        """
        # If we have a health score, use it as a proxy for completion
        if project.health_score > 0:
            # Convert health score (0-10) to completion percentage (0-100)
            return project.health_score * 10
        
        # Otherwise, use time elapsed as a proxy
        if project.expected_end_date:
            total_days = (project.expected_end_date - project.start_date).days
            days_elapsed = (datetime.now() - project.start_date).days
            
            if total_days > 0:
                return min(100, (days_elapsed / total_days) * 100)
        
        # Default return if we can't calculate
        return 50.0


class RiskAnalyzer:
    """Analyze and score risks based on multiple data sources."""
    
    def prioritize_risks(self, risks: List[Risk]) -> List[Risk]:
        """
        Prioritize risks based on severity, probability, and calculated score.
        
        Args:
            risks: List of Risk objects
            
        Returns:
            Sorted list of risks by priority
        """
        # Ensure risk scores are up to date
        for risk in risks:
            risk.calculate_risk_score()
        
        # Sort risks by score (descending)
        return sorted(risks, key=lambda x: x.risk_score, reverse=True)
    
    def generate_alerts(self, projects: List[Project], risks: List[Risk]) -> List[Alert]:
        """
        Generate alerts for high-priority risks.
        
        Args:
            projects: List of Project objects
            risks: List of Risk objects
            
        Returns:
            List of Alert objects for critical risks
        """
        alerts = []
        
        # Group risks by project
        risks_by_project = {}
        for risk in risks:
            if risk.project_id not in risks_by_project:
                risks_by_project[risk.project_id] = []
            risks_by_project[risk.project_id].append(risk)
        
        # Generate alerts for critical and high risks
        for project in projects:
            project_risks = risks_by_project.get(project.id, [])
            
            for risk in project_risks:
                if risk.severity in [RiskSeverity.CRITICAL, RiskSeverity.HIGH]:
                    alert = Alert(
                        project_id=project.id,
                        risk_id=risk.id,
                        title=f"High Risk Alert: {risk.title}",
                        description=f"Critical risk detected in project '{project.name}': {risk.description}",
                        severity=risk.severity,
                        action_required=True,
                        action_description="Immediate review and mitigation planning required"
                    )
                    alerts.append(alert)
        
        return alerts
    
    def correlate_market_and_project_risks(
        self, project_risks: List[Risk], market_indicators: List[MarketIndicator]
    ) -> Dict[str, List[Tuple[Risk, MarketIndicator, float]]]:
        """
        Find correlations between market indicators and project risks.
        
        Args:
            project_risks: List of project-specific Risk objects
            market_indicators: List of MarketIndicator objects
            
        Returns:
            Dictionary mapping risk categories to lists of correlated risks and indicators
        """
        correlations = {}
        
        # Group risks by category
        risks_by_category = {}
        for risk in project_risks:
            category = risk.category.value
            if category not in risks_by_category:
                risks_by_category[category] = []
            risks_by_category[category].append(risk)
        
        # Find correlations
        for category, risks in risks_by_category.items():
            correlations[category] = []
            
            for risk in risks:
                for indicator in market_indicators:
                    correlation_strength = self._calculate_correlation(risk, indicator)
                    
                    if correlation_strength > 0.5:  # Only include strong correlations
                        correlations[category].append((risk, indicator, correlation_strength))
        
        return correlations
    
    def _calculate_correlation(self, risk: Risk, indicator: MarketIndicator) -> float:
        """
        Calculate correlation strength between a risk and market indicator.
        This is a simplified correlation calculation.
        """
        # Get correlation from indicator risk_correlation if available
        if risk.category.value in indicator.risk_correlation:
            return indicator.risk_correlation[risk.category.value]
        
        # Otherwise, use category-based correlation (simplified)
        category_correlations = {
            RiskCategory.FINANCIAL: {
                "economic": 0.8,
                "market": 0.7,
                "interest_rates": 0.9,
                "inflation": 0.8
            },
            RiskCategory.MARKET: {
                "economic": 0.7,
                "market": 0.9,
                "technology": 0.6,
                "consumer_confidence": 0.8
            },
            RiskCategory.TECHNICAL: {
                "technology": 0.8,
                "innovation": 0.7,
                "research": 0.6
            },
            RiskCategory.RESOURCE: {
                "labor_market": 0.8,
                "skills_shortage": 0.9,
                "unemployment": 0.7
            },
            RiskCategory.LEGAL: {
                "regulatory": 0.9,
                "compliance": 0.8,
                "legal": 0.9
            }
        }
        
        # Default correlation strength
        default_strength = 0.3
        
        return category_correlations.get(risk.category, {}).get(indicator.category, default_strength)


def format_risk_data_for_gemini(projects: List[Project], risks: List[Risk]) -> Dict:
    """
    Format project and risk data for the Gemini API.
    
    Args:
        projects: List of Project objects
        risks: List of Risk objects
        
    Returns:
        Dictionary with structured data for Gemini processing
    """
    # Group risks by project
    risks_by_project = {}
    for risk in risks:
        if risk.project_id not in risks_by_project:
            risks_by_project[risk.project_id] = []
        risks_by_project[risk.project_id].append(risk)
    
    # Create project summaries with associated risks
    project_summaries = []
    for project in projects:
        project_risks = risks_by_project.get(project.id, [])
        
        # Calculate risk statistics
        risk_counts = {
            "low": len([r for r in project_risks if r.severity == RiskSeverity.LOW]),
            "medium": len([r for r in project_risks if r.severity == RiskSeverity.MEDIUM]),
            "high": len([r for r in project_risks if r.severity == RiskSeverity.HIGH]),
            "critical": len([r for r in project_risks if r.severity == RiskSeverity.CRITICAL])
        }
        
        # Format top risks (highest scores)
        top_risks = sorted(project_risks, key=lambda r: r.risk_score, reverse=True)[:3]
        formatted_top_risks = [
            {
                "id": risk.id,
                "title": risk.title,
                "severity": risk.severity.value,
                "score": risk.risk_score,
                "status": risk.status.value
            }
            for risk in top_risks
        ]
        
        # Create project summary
        project_summary = {
            "id": project.id,
            "name": project.name,
            "status": project.status,
            "health_score": project.health_score,
            "budget": {
                "total": project.budget,
                "spent": project.expenditure_to_date,
                "remaining": project.budget - project.expenditure_to_date
            },
            "timeline": {
                "start_date": project.start_date.strftime("%Y-%m-%d"),
                "expected_end_date": project.expected_end_date.strftime("%Y-%m-%d") if project.expected_end_date else "Unknown",
                "days_remaining": (project.expected_end_date - datetime.now()).days if project.expected_end_date else None
            },
            "risks": {
                "total_count": len(project_risks),
                "by_severity": risk_counts,
                "top_risks": formatted_top_risks
            }
        }
        
        project_summaries.append(project_summary)
    
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_projects": len(projects),
        "projects": project_summaries
    }


def prepare_chatbot_context(
    project_id: Optional[str] = None,
    projects: Optional[List[Project]] = None,
    risks: Optional[List[Risk]] = None,
    market_indicators: Optional[List[MarketIndicator]] = None
) -> str:
    """
    Prepare context for the Gemini chatbot about project risks.
    
    Args:
        project_id: Optional ID to filter for a specific project
        projects: List of Project objects
        risks: List of Risk objects
        market_indicators: List of MarketIndicator objects
        
    Returns:
        String context for the Gemini API
    """
    context_parts = []
    
    if project_id and projects:
        # Filter for specific project
        target_projects = [p for p in projects if p.id == project_id]
        if target_projects:
            project = target_projects[0]
            context_parts.append(f"Project: {project.name}\n")
            context_parts.append(f"Description: {project.description}\n")
            context_parts.append(f"Status: {project.status}\n")
            context_parts.append(f"Health Score: {project.health_score:.1f}/10\n")
            context_parts.append(f"Budget: ${project.budget:,.2f}\n")
            context_parts.append(f"Spent: ${project.expenditure_to_date:,.2f}\n")
            
            # Add timeline info
            if project.expected_end_date:
                days_remaining = (project.expected_end_date - datetime.now()).days
                context_parts.append(f"Timeline: {days_remaining} days remaining\n")
            
            # Add risk info if available
            if risks:
                project_risks = [r for r in risks if r.project_id == project_id]
                context_parts.append(f"Total Risks: {len(project_risks)}\n")
                
                # Count risks by severity
                critical = len([r for r in project_risks if r.severity == RiskSeverity.CRITICAL])
                high = len([r for r in project_risks if r.severity == RiskSeverity.HIGH])
                medium = len([r for r in project_risks if r.severity == RiskSeverity.MEDIUM])
                low = len([r for r in project_risks if r.severity == RiskSeverity.LOW])
                
                context_parts.append(f"Risk Summary: {critical} Critical, {high} High, {medium} Medium, {low} Low\n")
                
                # Add top 3 risks
                top_risks = sorted(project_risks, key=lambda r: r.risk_score, reverse=True)[:3]
                if top_risks:
                    context_parts.append("Top Risks:\n")
                    for risk in top_risks:
                        context_parts.append(f"- {risk.title} ({risk.severity.value}): {risk.description}\n")
    else:
        # Summary of all projects
        if projects:
            context_parts.append(f"Total Projects: {len(projects)}\n")
            
            # Count projects by status
            status_counts = {}
            for project in projects:
                if project.status not in status_counts:
                    status_counts[project.status] = 0
                status_counts[project.status] += 1
            
            status_summary = ", ".join([f"{count} {status}" for status, count in status_counts.items()])
            context_parts.append(f"Project Status Summary: {status_summary}\n")
            
            # Add overall risk summary if available
            if risks:
                critical = len([r for r in risks if r.severity == RiskSeverity.CRITICAL])
                high = len([r for r in risks if r.severity == RiskSeverity.HIGH])
                medium = len([r for r in risks if r.severity == RiskSeverity.MEDIUM])
                low = len([r for r in risks if r.severity == RiskSeverity.LOW])
                
                context_parts.append(f"Overall Risk Summary: {critical} Critical, {high} High, {medium} Medium, {low} Low\n")
                
                # Add projects with critical risks
                projects_with_critical = set([r.project_id for r in risks if r.severity == RiskSeverity.CRITICAL])
                if projects_with_critical:
                    critical_project_names = [p.name for p in projects if p.id in projects_with_critical]
                    context_parts.append("Projects with Critical Risks:\n")
                    for name in critical_project_names:
                        context_parts.append(f"- {name}\n")
    
    # Add market indicators if available
    if market_indicators:
        context_parts.append("\nMarket Indicators:\n")
        for indicator in market_indicators[:5]:  # Limit to 5 most recent indicators
            context_parts.append(f"- {indicator.name}: {indicator.current_value} ({indicator.change_percentage:+.1f}%)\n")
    
    return "".join(context_parts)