import logging
from datetime import datetime, timedelta
from uuid import UUID
from typing import Dict, List, Optional, Any, Tuple
import json

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models import Project, RiskLog, Alert, User
from app.agents.market_analysis import MarketAnalysisAgent
from app.agents.risk_scoring import RiskScoringAgent
from app.agents.project_status import ProjectStatusAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ReportingAgent:
    """
    Agent responsible for collating data from other agents,
    generating comprehensive risk reports, and creating alerts
    for project managers and leadership teams.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.market_agent = MarketAnalysisAgent(db)
        self.risk_scoring_agent = RiskScoringAgent(db)
        self.project_status_agent = ProjectStatusAgent(db)
        
    def generate_comprehensive_report(self, project_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive risk report combining data from all agent sources.
        
        Args:
            project_id: Optional UUID to filter for a specific project (None for all projects)
            
        Returns:
            Dictionary containing consolidated risk report
        """
        try:
            # Get market analysis data
            market_data = self.market_agent.get_current_market_analysis()
            
            # Get project data
            projects_data = []
            if project_id:
                project_status = self.project_status_agent.analyze_project_status(project_id)
                if "error" not in project_status:
                    project_risk_score = self.risk_scoring_agent.calculate_project_risk_score(project_id)
                    project_status["financial_risk_score"] = project_risk_score["risk_score"]
                    projects_data.append(project_status)
            else:
                # Get all projects
                projects = self.db.query(Project).all()
                for project in projects:
                    project_status = self.project_status_agent.analyze_project_status(project.project_id)
                    if "error" not in project_status:
                        project_risk_score = self.risk_scoring_agent.calculate_project_risk_score(project.project_id)
                        project_status["financial_risk_score"] = project_risk_score["risk_score"]
                        projects_data.append(project_status)
            
            # Compile overall report
            timestamp = datetime.now()
            report = {
                "timestamp": timestamp,
                "market_analysis": market_data,
                "projects_data": projects_data,
                "overall_summary": self._generate_overall_summary(projects_data, market_data),
                "recommendations": self._generate_recommendations(projects_data, market_data)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {str(e)}")
            return {"error": str(e)}
    
    def generate_risk_trend_report(self, project_id: Optional[UUID] = None, days: int = 30) -> Dict[str, Any]:
        """
        Generate a report showing risk trends over time.
        
        Args:
            project_id: Optional UUID to filter for a specific project (None for all projects)
            days: Number of days of historical data to include
            
        Returns:
            Dictionary containing risk trend data
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Query risk logs
            query = self.db.query(
                RiskLog.timestamp,
                RiskLog.risk_type,
                func.avg(RiskLog.risk_score).label("avg_risk_score")
            ).filter(RiskLog.timestamp >= start_date)
            
            if project_id:
                query = query.filter(RiskLog.project_id == project_id)
                
            # Group by day and risk type
            risk_trend_data = query.group_by(
                func.date_trunc('day', RiskLog.timestamp),
                RiskLog.risk_type
            ).order_by(RiskLog.timestamp).all()
            
            # Format data for visualization
            trend_data = {}
            for date, risk_type, avg_score in risk_trend_data:
                date_str = date.strftime("%Y-%m-%d")
                if date_str not in trend_data:
                    trend_data[date_str] = {}
                trend_data[date_str][risk_type] = float(avg_score)
            
            # Get project details if needed
            project_info = None
            if project_id:
                project = self.db.query(Project).filter(Project.project_id == project_id).first()
                if project:
                    project_info = {
                        "project_id": project.project_id,
                        "name": project.name,
                        "description": project.description,
                        "start_date": project.start_date,
                        "end_date": project.end_date
                    }
            
            return {
                "trend_data": trend_data,
                "project_info": project_info,
                "date_range": {
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": datetime.now().strftime("%Y-%m-%d")
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating risk trend report: {str(e)}")
            return {"error": str(e)}
    
    def get_active_alerts(self, project_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Get all active (unacknowledged) alerts, optionally filtered by project.
        
        Args:
            project_id: Optional UUID to filter for a specific project (None for all projects)
            
        Returns:
            Dictionary containing active alerts
        """
        try:
            query = self.db.query(Alert).filter(Alert.is_acknowledged == False)
            
            if project_id:
                query = query.filter(Alert.project_id == project_id)
                
            alerts = query.order_by(desc(Alert.created_at)).all()
            
            result = []
            for alert in alerts:
                # Get project name
                project = self.db.query(Project).filter(Project.project_id == alert.project_id).first()
                project_name = project.name if project else "Unknown Project"
                
                result.append({
                    "alert_id": alert.alert_id,
                    "project_id": alert.project_id,
                    "project_name": project_name,
                    "alert_type": alert.alert_type,
                    "message": alert.message,
                    "created_at": alert.created_at
                })
                
            return {"alerts": result}
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {str(e)}")
            return {"error": str(e)}
    
    def acknowledge_alert(self, alert_id: UUID) -> Dict[str, Any]:
        """
        Mark an alert as acknowledged.
        
        Args:
            alert_id: UUID of the alert to acknowledge
            
        Returns:
            Dictionary with success/error status
        """
        try:
            alert = self.db.query(Alert).filter(Alert.alert_id == alert_id).first()
            
            if not alert:
                return {"error": "Alert not found"}
                
            alert.is_acknowledged = True
            self.db.commit()
            
            return {"success": True, "message": "Alert acknowledged successfully"}
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {str(e)}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_high_risk_projects(self) -> Dict[str, Any]:
        """
        Get a list of high risk projects requiring immediate attention.
        
        Returns:
            Dictionary containing high risk projects and key metrics
        """
        try:
            # Get all projects first
            projects = self.db.query(Project).all()
            
            high_risk_projects = []
            for project in projects:
                # Get the latest risk logs for this project
                latest_logs = self.db.query(RiskLog).filter(
                    RiskLog.project_id == project.project_id
                ).order_by(desc(RiskLog.timestamp)).limit(5).all()
                
                # Calculate average risk score from latest logs
                if latest_logs:
                    avg_risk_score = sum(log.risk_score for log in latest_logs) / len(latest_logs)
                    
                    # If average risk is high, add to high risk list
                    if avg_risk_score >= 0.6:  # Threshold for high risk
                        # Get manager name
                        manager = self.db.query(User).filter(User.user_id == project.manager_id).first()
                        manager_name = manager.full_name if manager else "Unknown Manager"
                        
                        high_risk_projects.append({
                            "project_id": project.project_id,
                            "name": project.name,
                            "risk_score": avg_risk_score,
                            "risk_level": self._determine_risk_level(avg_risk_score),
                            "schedule_delay": project.schedule_delay,
                            "resource_availability": project.resource_availability,
                            "payment_received": project.customer_payment_received,
                            "manager": manager_name,
                            "days_to_deadline": (project.end_date - datetime.now().date()).days
                        })
            
            # Sort by risk score (highest first)
            high_risk_projects.sort(key=lambda x: x["risk_score"], reverse=True)
            
            return {
                "high_risk_projects": high_risk_projects,
                "count": len(high_risk_projects),
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting high risk projects: {str(e)}")
            return {"error": str(e)}
    
    def create_executive_summary(self) -> Dict[str, Any]:
        """
        Create an executive summary of all project risks for leadership.
        
        Returns:
            Dictionary with executive summary data
        """
        try:
            # Get total project stats
            total_projects = self.db.query(func.count(Project.project_id)).scalar()
            
            # Get market trend summary
            market_summary = self.market_agent.get_market_summary()
            
            # Get risk levels for all projects
            all_projects = self.db.query(Project).all()
            risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
            
            projects_at_risk = []
            for project in all_projects:
                # Get average risk from recent logs
                recent_logs = self.db.query(RiskLog).filter(
                    RiskLog.project_id == project.project_id
                ).order_by(desc(RiskLog.timestamp)).limit(5).all()
                
                if recent_logs:
                    avg_risk = sum(log.risk_score for log in recent_logs) / len(recent_logs)
                    risk_level = self._determine_risk_level(avg_risk)
                    risk_counts[risk_level] += 1
                    
                    if risk_level in ["HIGH", "CRITICAL"]:
                        projects_at_risk.append({
                            "name": project.name,
                            "risk_level": risk_level,
                            "key_issues": self._get_top_issues_for_project(project.project_id)
                        })
                else:
                    risk_counts["LOW"] += 1
            
            # Get unacknowledged alerts count
            alert_count = self.db.query(func.count(Alert.alert_id)).filter(
                Alert.is_acknowledged == False
            ).scalar()
            
            return {
                "timestamp": datetime.now(),
                "total_projects": total_projects,
                "risk_distribution": risk_counts,
                "high_risk_percentage": ((risk_counts["HIGH"] + risk_counts["CRITICAL"]) / total_projects) * 100 if total_projects > 0 else 0,
                "market_summary": market_summary,
                "projects_requiring_attention": projects_at_risk,
                "unacknowledged_alerts": alert_count,
                "recommendations": self._generate_executive_recommendations(risk_counts, projects_at_risk)
            }
            
        except Exception as e:
            logger.error(f"Error creating executive summary: {str(e)}")
            return {"error": str(e)}
    
    def _generate_overall_summary(self, projects_data: List[Dict[str, Any]], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an overall summary based on project and market data.
        
        Args:
            projects_data: List of project data dictionaries
            market_data: Market analysis data
            
        Returns:
            Dictionary with summary information
        """
        try:
            total_projects = len(projects_data)
            risk_levels = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
            
            for project in projects_data:
                if "risk_level" in project:
                    risk_levels[project["risk_level"]] += 1
            
            return {
                "total_projects": total_projects,
                "risk_distribution": risk_levels,
                "high_risk_percentage": ((risk_levels["HIGH"] + risk_levels["CRITICAL"]) / total_projects) * 100 if total_projects > 0 else 0,
                "market_risk_summary": market_data.get("risk_summary", "No market risk data available")
            }
            
        except Exception as e:
            logger.error(f"Error generating overall summary: {str(e)}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, projects_data: List[Dict[str, Any]], market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on project and market data.
        
        Args:
            projects_data: List of project data dictionaries
            market_data: Market analysis data
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        try:
            # Check for high market risks
            if market_data.get("market_risk_level", "LOW") in ["HIGH", "CRITICAL"]:
                recommendations.append({
                    "category": "Market Risk",
                    "recommendation": "Consider reviewing financial projections due to current market volatility.",
                    "priority": "HIGH"
                })
            
            # Check for projects with resource issues
            resource_issues = [p for p in projects_data if any(r["risk_type"] == "resource" and r["risk_identified"] for r in p.get("identified_risks", []))]
            if resource_issues:
                recommendations.append({
                    "category": "Resource Allocation",
                    "recommendation": f"Review resource allocation for {len(resource_issues)} projects with critical resource shortages.",
                    "priority": "HIGH" if len(resource_issues) > 2 else "MEDIUM",
                    "affected_projects": [p["project_name"] for p in resource_issues]
                })
            
            # Check for payment issues
            payment_issues = [p for p in projects_data if any(r["risk_type"] == "payment" and r["risk_identified"] for r in p.get("identified_risks", []))]
            if payment_issues:
                recommendations.append({
                    "category": "Financial",
                    "recommendation": f"Follow up on pending payments for {len(payment_issues)} projects to improve cash flow.",
                    "priority": "HIGH" if len(payment_issues) > 3 else "MEDIUM",
                    "affected_projects": [p["project_name"] for p in payment_issues]
                })
            
            # Check for schedule delays
            schedule_issues = [p for p in projects_data if any(r["risk_type"] == "schedule" and r["risk_identified"] and r["risk_score"] > 0.6 for r in p.get("identified_risks", []))]
            if schedule_issues:
                recommendations.append({
                    "category": "Schedule Management",
                    "recommendation": f"Implement recovery plans for {len(schedule_issues)} projects with significant schedule delays.",
                    "priority": "HIGH",
                    "affected_projects": [p["project_name"] for p in schedule_issues]
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return [{"category": "Error", "recommendation": "Error generating recommendations", "priority": "LOW"}]
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """
        Determine the textual risk level based on numerical risk score.
        
        Args:
            risk_score: Numerical risk score (0.0 to 1.0)
            
        Returns:
            Risk level as a string (LOW, MEDIUM, HIGH, CRITICAL)
        """
        if risk_score >= 0.8:
            return "CRITICAL"
        elif risk_score >= 0.6:
            return "HIGH"
        elif risk_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_top_issues_for_project(self, project_id: UUID) -> List[str]:
        """
        Get the top issues for a specific project.
        
        Args:
            project_id: UUID of the project
            
        Returns:
            List of issue descriptions
        """
        try:
            # Get recent risk logs for this project
            recent_logs = self.db.query(RiskLog).filter(
                RiskLog.project_id == project_id
            ).order_by(desc(RiskLog.timestamp), desc(RiskLog.risk_score)).limit(3).all()
            
            return [log.details for log in recent_logs]
            
        except Exception as e:
            logger.error(f"Error getting top issues for project: {str(e)}")
            return ["Error retrieving issues"]
    
    def _generate_executive_recommendations(self, risk_counts: Dict[str, int], high_risk_projects: List[Dict[str, Any]]) -> List[str]:
        """
        Generate executive-level recommendations.
        
        Args:
            risk_counts: Dictionary containing counts of projects at each risk level
            high_risk_projects: List of high risk projects
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Overall portfolio health recommendation
        total_projects = sum(risk_counts.values())
        high_risk_percentage = ((risk_counts["HIGH"] + risk_counts["CRITICAL"]) / total_projects) * 100 if total_projects > 0 else 0
        
        if high_risk_percentage > 30:
            recommendations.append("URGENT: Portfolio health critical. Consider organizational review of project management practices.")
        elif high_risk_percentage > 20:
            recommendations.append("IMPORTANT: Significant portion of projects at high risk. Schedule executive review session.")
        elif high_risk_percentage > 10:
            recommendations.append("ADVISORY: Monitor increasing risk trends in portfolio.")
        
        # Project-specific recommendations
        if len(high_risk_projects) > 0:
            recommendations.append(f"Prioritize intervention for {len(high_risk_projects)} high-risk projects, especially: " + 
                             ", ".join([p["name"] for p in high_risk_projects[:3]]))
        
        # Market conditions recommendation
        market_agent = MarketAnalysisAgent(self.db)
        market_data = market_agent.get_market_summary()
        
        if market_data.get("market_sentiment", "neutral") == "negative":
            recommendations.append("Consider financial strategy review due to negative market conditions.")
        
        return recommendations