# project_risk_manager.py
from crewai import Crew, Agent, Task
from .market_analysis_agent import MarketAnalysisAgent
from .project_status_agent import ProjectStatusAgent
from .risk_scoring_agent import RiskScoringAgent
from .reporting_agent import ReportingAgent
from ..data.database import get_db_client
from ..utils.gemini_client import get_gemini_client

class ProjectRiskManager:
    def __init__(self):
        self.db_client = get_db_client()
        self.gemini = get_gemini_client()
        
        # Initialize agents
        self.market_agent = MarketAnalysisAgent()
        self.project_status_agent = ProjectStatusAgent()
        self.risk_scoring_agent = RiskScoringAgent()
        self.reporting_agent = ReportingAgent()
        
    def get_all_projects(self):
        """Retrieve all projects from the database"""
        return self.db_client.from_("projects").select("*").execute().data
    
    def get_project_details(self, project_id):
        """Get detailed information about a specific project"""
        return self.db_client.from_("projects").select("*").eq("id", project_id).single().execute().data
    
    def get_project_risks(self, project_id):
        """Get risks associated with a specific project"""
        return self.db_client.from_("risks").select("*").eq("project_id", project_id).execute().data
    
    def run_risk_analysis(self, project_id):
        """Run a comprehensive risk analysis on a project"""
        # Create crew with all agents
        project_crew = Crew(
            agents=[
                self.market_agent.get_agent(),
                self.project_status_agent.get_agent(),
                self.risk_scoring_agent.get_agent(),
                self.reporting_agent.get_agent()
            ],
            tasks=[
                self.market_agent.create_analysis_task(project_id),
                self.project_status_agent.create_status_task(project_id),
                self.risk_scoring_agent.create_scoring_task(project_id),
                self.reporting_agent.create_report_task(project_id)
            ],
            verbose=True
        )
        
        # Run the crew
        result = project_crew.kickoff()
        
        # Save results to database
        self._save_analysis_results(project_id, result)
        
        return result
    
    def process_chat_message(self, message, project_id=None):
        """Process a chat message from the user"""
        context = {}
        
        if project_id:
            # Get project details and risks
            project = self.get_project_details(project_id)
            risks = self.get_project_risks(project_id)
            context = {
                "project": project,
                "risks": risks
            }
        
        # Use Gemini to process the chat message
        response = self.gemini.generate_content(
            f"""You are a Project Risk Management Assistant.
            Respond to the following query about project risks.
            
            Project Context: {context}
            
            User Query: {message}
            """
        )
        
        return {"response": response.text}
    
    def _save_analysis_results(self, project_id, results):
        """Save analysis results to the database"""
        # Parse results and save to appropriate tables
        # Implementation depends on the structure of results
        pass