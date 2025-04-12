import logging
from datetime import datetime, timedelta
from uuid import UUID
from typing import Dict, List, Optional, Tuple, Any

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Project, RiskLog, Alert
from app.schemas import RiskLogCreate
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ProjectStatusAgent:
    """
    Agent responsible for monitoring internal project metrics and identifying risks
    based on project parameters like resource availability, payment status, and schedule delays.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def analyze_project_status(self, project_id: UUID) -> Dict[str, Any]:
        """
        Analyze a single project's current status and identify potential internal risks.
        
        Args:
            project_id: UUID of the project to analyze
            
        Returns:
            Dictionary containing risk assessment and identified issues
        """
        try:
            project = self.db.query(Project).filter(Project.project_id == project_id).first()
            
            if not project:
                logger.error(f"Project with ID {project_id} not found")
                return {"error": "Project not found", "risk_identified": False}
            
            risks = []
            total_risk_score = 0.0
            risk_count = 0
            
            # Analyze resource availability
            resource_risk = self._evaluate_resource_risk(project.resource_availability)
            if resource_risk["risk_identified"]:
                risks.append(resource_risk)
                total_risk_score += resource_risk["risk_score"]
                risk_count += 1
            
            # Analyze payment status
            payment_risk = self._evaluate_payment_risk(project.customer_payment_received)
            if payment_risk["risk_identified"]:
                risks.append(payment_risk)
                total_risk_score += payment_risk["risk_score"]
                risk_count += 1
            
            # Analyze schedule delays
            schedule_risk = self._evaluate_schedule_risk(project.schedule_delay)
            if schedule_risk["risk_identified"]:
                risks.append(schedule_risk)
                total_risk_score += schedule_risk["risk_score"]
                risk_count += 1
            
            # Analyze timeline to completion
            timeline_risk = self._evaluate_timeline_risk(project.start_date, project.end_date)
            if timeline_risk["risk_identified"]:
                risks.append(timeline_risk)
                total_risk_score += timeline_risk["risk_score"]
                risk_count += 1
                
            # Calculate overall risk score
            overall_risk_score = total_risk_score / risk_count if risk_count > 0 else 0.0
            risk_level = self._determine_risk_level(overall_risk_score)
            
            # Record risks in the database
            for risk in risks:
                self._log_risk(project_id, risk)
                
            # Create alerts for high-risk items
            if risk_level in ["HIGH", "CRITICAL"]:
                self._create_alert(project_id, risks, risk_level)
            
            return {
                "project_id": project_id,
                "project_name": project.name,
                "overall_risk_score": overall_risk_score,
                "risk_level": risk_level,
                "identified_risks": risks,
                "resource_availability": project.resource_availability,
                "payment_status": "Received" if project.customer_payment_received else "Pending",
                "schedule_delay": project.schedule_delay,
                "start_date": project.start_date,
                "end_date": project.end_date
            }
            
        except Exception as e:
            logger.error(f"Error analyzing project status: {str(e)}")
            return {"error": str(e), "risk_identified": False}
    
    def analyze_all_projects(self) -> List[Dict[str, Any]]:
        """
        Analyze all projects in the database and identify potential risks.
        
        Returns:
            List of dictionaries containing risk assessments for each project
        """
        try:
            projects = self.db.query(Project).all()
            results = []
            
            for project in projects:
                result = self.analyze_project_status(project.project_id)
                results.append(result)
                
            return results
        
        except Exception as e:
            logger.error(f"Error analyzing all projects: {str(e)}")
            return [{"error": str(e), "risk_identified": False}]
    
    def _evaluate_resource_risk(self, resource_availability: int) -> Dict[str, Any]:
        """
        Evaluate risk based on resource availability (scale typically 0-100).
        
        Args:
            resource_availability: Numerical value indicating resource availability
            
        Returns:
            Dictionary with risk assessment details
        """
        risk = {
            "risk_type": "resource",
            "risk_identified": False,
            "risk_score": 0.0,
            "details": ""
        }
        
        if resource_availability < 50:
            risk["risk_identified"] = True
            
            if resource_availability < 25:
                risk["risk_score"] = 0.9
                risk["details"] = "Critical resource shortage detected. Project delivery at high risk."
            else:
                risk["risk_score"] = 0.6
                risk["details"] = "Resource availability below optimal levels. May impact delivery timelines."
                
        return risk
    
    def _evaluate_payment_risk(self, payment_received: bool) -> Dict[str, Any]:
        """
        Evaluate risk based on customer payment status.
        
        Args:
            payment_received: Boolean indicating if payment has been received
            
        Returns:
            Dictionary with risk assessment details
        """
        risk = {
            "risk_type": "payment",
            "risk_identified": False,
            "risk_score": 0.0,
            "details": ""
        }
        
        if not payment_received:
            risk["risk_identified"] = True
            risk["risk_score"] = 0.7
            risk["details"] = "Customer payment not received. Potential cash flow impact."
            
        return risk
    
    def _evaluate_schedule_risk(self, schedule_delay: int) -> Dict[str, Any]:
        """
        Evaluate risk based on current schedule delay in days.
        
        Args:
            schedule_delay: Number of days the project is behind schedule
            
        Returns:
            Dictionary with risk assessment details
        """
        risk = {
            "risk_type": "schedule",
            "risk_identified": False,
            "risk_score": 0.0,
            "details": ""
        }
        
        if schedule_delay > 0:
            risk["risk_identified"] = True
            
            if schedule_delay > 14:
                risk["risk_score"] = 0.8
                risk["details"] = f"Significant schedule delay of {schedule_delay} days. Immediate attention required."
            elif schedule_delay > 7:
                risk["risk_score"] = 0.6
                risk["details"] = f"Moderate schedule delay of {schedule_delay} days. Monitor closely."
            else:
                risk["risk_score"] = 0.4
                risk["details"] = f"Minor schedule delay of {schedule_delay} days. Within acceptable range."
                
        return risk
    
    def _evaluate_timeline_risk(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Evaluate risk based on project timeline and remaining time to completion.
        
        Args:
            start_date: Project start date
            end_date: Project end date
            
        Returns:
            Dictionary with risk assessment details
        """
        risk = {
            "risk_type": "timeline",
            "risk_identified": False,
            "risk_score": 0.0,
            "details": ""
        }
        
        today = datetime.now().date()
        total_days = (end_date - start_date).days
        elapsed_days = (today - start_date).days
        
        if total_days <= 0:
            return risk
        
        progress_percentage = (elapsed_days / total_days) * 100
        days_remaining = (end_date - today).days
        
        if days_remaining < 0:
            risk["risk_identified"] = True
            risk["risk_score"] = 1.0
            risk["details"] = f"Project has exceeded end date by {abs(days_remaining)} days."
        elif progress_percentage > 80 and days_remaining < 7:
            risk["risk_identified"] = True
            risk["risk_score"] = 0.7
            risk["details"] = f"Project nearing completion with only {days_remaining} days remaining. Review completion status."
            
        return risk
    
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
    
    def _log_risk(self, project_id: UUID, risk: Dict[str, Any]) -> None:
        """
        Log identified risk to the database.
        
        Args:
            project_id: UUID of the project
            risk: Dictionary containing risk details
        """
        try:
            risk_log = RiskLog(
                project_id=project_id,
                risk_type=risk["risk_type"],
                risk_score=risk["risk_score"],
                details=risk["details"],
                timestamp=datetime.now()
            )
            
            self.db.add(risk_log)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error logging risk: {str(e)}")
            self.db.rollback()
    
    def _create_alert(self, project_id: UUID, risks: List[Dict[str, Any]], risk_level: str) -> None:
        """
        Create an alert for high-risk projects.
        
        Args:
            project_id: UUID of the project
            risks: List of identified risks
            risk_level: Overall risk level
        """
        try:
            project = self.db.query(Project).filter(Project.project_id == project_id).first()
            
            if not project:
                return
            
            message = f"ALERT: Project '{project.name}' has {risk_level} risk level.\n"
            message += "Identified issues:\n"
            
            for risk in risks:
                if risk["risk_identified"]:
                    message += f"- {risk['details']}\n"
            
            alert = Alert(
                project_id=project_id,
                alert_type=risk_level,
                message=message,
                is_acknowledged=False,
                created_at=datetime.now()
            )
            
            self.db.add(alert)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            self.db.rollback()