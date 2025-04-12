import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import json

from ..models import Project, RiskLog
from ..schemas import ProjectRiskScoreResponse, RiskFactorScore
from ..config import settings
from ..utils.logger import LoggerMixin

from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

class RiskScoringAgent(LoggerMixin):
    """
    Agent responsible for calculating risk scores for projects.
    """
    
    def __init__(self):
        pass
    
    def calculate_internal_risk_score(self, project: Project) -> Dict[str, Any]:
        """
        Calculate risk score based on internal project factors.
        """
        self.logger.info(f"Calculating internal risk score for project {project.name}")
        
        risk_factors = {}
        
        # Resource availability risk
        if project.resource_availability <= 30:
            resource_risk = {"score": 0.9, "weight": 0.4, "description": "Critical resource shortage"}
        elif project.resource_availability <= 50:
            resource_risk = {"score": 0.7, "weight": 0.4, "description": "Significant resource shortage"}
        elif project.resource_availability <= 70:
            resource_risk = {"score": 0.4, "weight": 0.4, "description": "Moderate resource constraints"}
        else:
            resource_risk = {"score": 0.1, "weight": 0.4, "description": "Good resource availability"}
        
        risk_factors["resource_availability"] = resource_risk
        
        # Payment risk
        payment_risk = {"score": 0.8, "weight": 0.3, "description": "Payment not received"} if not project.customer_payment_received else {"score": 0.1, "weight": 0.3, "description": "Payment received"}
        risk_factors["payment"] = payment_risk
        
        # Schedule risk
        if project.schedule_delay > 30:
            schedule_risk = {"score": 0.9, "weight": 0.3, "description": "Critical schedule delay"}
        elif project.schedule_delay > 14:
            schedule_risk = {"score": 0.6, "weight": 0.3, "description": "Significant schedule delay"}
        elif project.schedule_delay > 7:
            schedule_risk = {"score": 0.4, "weight": 0.3, "description": "Moderate schedule delay"}
        else:
            schedule_risk = {"score": 0.1, "weight": 0.3, "description": "On schedule or minor delay"}
        
        risk_factors["schedule"] = schedule_risk
        
        # Calculate overall internal risk score (weighted average)
        overall_score = sum(factor["score"] * factor["weight"] for factor in risk_factors.values())
        
        return {
            "overall_score": overall_score,
            "factors": [
                {"factor_name": name, "score": details["score"], "weight": details["weight"], "description": details["description"]}
                for name, details in risk_factors.items()
            ]
        }
    
    async def analyze_project_risk(self, project: Project, internal_risk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to analyze project risk and provide recommendations.
        """
        self.logger.info(f"Analyzing project risk with AI for project {project.name}")
        
        try:
            # Select LLM based on available API keys
            if settings.GEMINI_API_KEY:
                llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=settings.GEMINI_API_KEY)
            else:
                self.logger.error("No LLM API key available for risk analysis")
                return self._get_mock_analysis_results(project, internal_risk)
            
            # Create the risk analyst agent
            risk_analyst = Agent(
                role="Project Risk Analyst",
                goal="Analyze project risks and provide mitigation recommendations",
                backstory="""You are an expert in analyzing project risks in IT organizations.
                You understand both technical and business aspects of software development projects
                and can identify potential issues before they become critical.""",
                verbose=True,
                llm=llm
            )
            
            # Format project data for analysis
            project_data = {
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "end_date": project.end_date.isoformat() if project.end_date else None,
                "resource_availability": project.resource_availability,
                "customer_payment_received": project.customer_payment_received,
                "schedule_delay": project.schedule_delay
            }
            
            project_json = json.dumps(project_data, indent=2)
            risk_json = json.dumps(internal_risk, indent=2)
            
            # Create the analysis task
            analysis_task = Task(
                description=f"""
                Analyze the following project and its risk assessment:
                
                PROJECT DATA:
                {project_json}
                
                RISK ASSESSMENT:
                {risk_json}
                
                Consider:
                1. The primary risk factors and their severity
                2. Additional potential risks not captured in the assessment
                3. Practical mitigation strategies for each identified risk
                
                Return your analysis in JSON format with these fields:
                - additional_risk_factors: List of any additional risk factors you identify
                - recommendations: List of specific actions to mitigate the identified risks
                """
                ,
                agent=risk_analyst
            )
            
            # Execute the analysis
            crew = Crew(
                agents=[risk_analyst],
                tasks=[analysis_task],
                verbose=True
            )
            
            result = crew.kickoff()
            
            # Extract JSON from result
            try:
                # Try to find and parse JSON in the result
                start_idx = result.find('{')
                end_idx = result.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = result[start_idx:end_idx]
                    analysis_results = json.loads(json_str)
                    return analysis_results
                else:
                    self.logger.warning("Could not extract JSON from AI response, using mock data")
                    return self._get_mock_analysis_results(project, internal_risk)
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse JSON from AI response, using mock data")
                return self._get_mock_analysis_results(project, internal_risk)
                
        except Exception as e:
            self.logger.error(f"Error during project risk analysis: {str(e)}")
            return self._get_mock_analysis_results(project, internal_risk)
    
    def _get_mock_analysis_results(self, project: Project, internal_risk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate mock analysis results when AI analysis fails.
        """
        overall_score = internal_risk["overall_score"]
        
        # Generate recommendations based on risk level
        recommendations = []
        
        # Resource recommendations
        if project.resource_availability < 70:
            recommendations.append("Consider hiring temporary contractors to address resource constraints")
            recommendations.append("Reprioritize tasks to focus on critical path activities")
        
        # Payment recommendations
        if not project.customer_payment_received:
            recommendations.append("Escalate payment issue to account management")
            recommendations.append("Review contract terms for possible penalties or remediation")
        
        # Schedule recommendations
        if project.schedule_delay > 7:
            recommendations.append("Conduct schedule risk assessment meeting with team")
            recommendations.append("Identify tasks that can be compressed or executed in parallel")
        
        # General recommendations
        recommendations.append("Schedule weekly risk review meetings with stakeholders")
        
        return {
            "additional_risk_factors": [
                {
                    "factor_name": "Scope Creep",
                    "score": 0.6,
                    "weight": 0.2,
                    "description": "Project may face scope expansion without proper change control"
                },
                {
                    "factor_name": "Technical Complexity",
                    "score": 0.5,
                    "weight": 0.2,
                    "description": "Project may involve complex technical challenges"
                }
            ],
            "recommendations": recommendations[:3]  # Limit to 3 recommendations
        }


async def calculate_project_risk_score(project: Project, db: Session) -> ProjectRiskScoreResponse:
    """
    Calculate and return the risk score for a project.
    This is the main function to be called by the API endpoint.
    """
    agent = RiskScoringAgent()
    
    # Calculate internal risk factors
    internal_risk = agent.calculate_internal_risk_score(project)
    
    # Get AI analysis and recommendations
    analysis_results = await agent.analyze_project_risk(project, internal_risk)
    
    # Combine internal risk factors with additional factors from AI
    all_risk_factors = [
        RiskFactorScore(
            factor_name=factor["factor_name"],
            score=factor["score"],
            weight=factor["weight"],
            description=factor["description"]
        )
        for factor in internal_risk["factors"]
    ]
    
    # Add additional risk factors if available
    if "additional_risk_factors" in analysis_results:
        for factor in analysis_results["additional_risk_factors"]:
            all_risk_factors.append(
                RiskFactorScore(
                    factor_name=factor["factor_name"],
                    score=factor["score"],
                    weight=factor["weight"],
                    description=factor["description"]
                )
            )
    
    # Get recommendations
    recommendations = analysis_results.get("recommendations", [])
    
    # Create risk log entry
    risk_log = RiskLog(
        project_id=project.project_id,
        risk_type="aggregated",
        risk_score=internal_risk["overall_score"],
        details=f"Automated risk assessment: Overall score {internal_risk['overall_score']:.2f}"
    )
    
    db.add(risk_log)
    db.commit()
    
    return ProjectRiskScoreResponse(
        project_id=project.project_id,
        project_name=project.name,
        overall_risk_score=internal_risk["overall_score"],
        risk_factors=all_risk_factors,
        timestamp=datetime.now(),
        recommendations=recommendations
    )