# reporting_agent.py
from crewai import Agent, Task
from backend.utils.gemini_client import get_gemini_client
from backend.data.database import get_db_client

class ReportingAgent:
    def __init__(self):
        self.gemini = get_gemini_client()
        self.db_client = get_db_client()
        
    def get_agent(self):
        """Return the CrewAI agent for reporting"""
        return Agent(
            role="Risk Reporting Specialist",
            goal="Create comprehensive and actionable risk reports",
            backstory="""You are an expert in data visualization and reporting with
                      a specialty in risk management. You can translate complex risk
                      assessments into clear, actionable reports for decision-makers.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.generate_executive_summary, self.create_mitigation_recommendations]
        )
    
    def create_report_task(self, project_id):
        """Create a task for generating risk reports"""
        project = self.db_client.from_("projects").select("*").eq("id", project_id).single().execute().data
        
        return Task(
            description=f"""Create a comprehensive risk report for project {project['name']}.
                        Using the risk assessment data, generate:
                        1. An executive summary of key risks
                        2. Detailed risk analysis with visualizations
                        3. Mitigation recommendations for high-priority risks
                        4. Risk monitoring plan and KPIs
                        
                        The report should be actionable and provide clear guidance for decision-makers.
                        """,
            expected_output="A complete risk report with executive summary, analysis, and recommendations",
            agent=self.get_agent()
        )
    
    def generate_executive_summary(self, risk_assessment):
        """Tool to generate an executive summary of project risks"""
        
        response = self.gemini.generate_content(
            f"""Given the following risk assessment:
            {risk_assessment}
            
            Generate an executive summary that includes:
            1. Overall project risk level
            2. Top 3-5 most critical risks
            3. Key areas requiring immediate attention
            4. Main recommendations
            5. Risk trend (improving, stable, worsening)
            
            Keep the summary concise and actionable for executive stakeholders.
            Format the response as a structured JSON object.
            """
        )
        
        return response.text
    
    def create_mitigation_recommendations(self, risk_assessment):
        """Tool to create risk mitigation recommendations"""
        
        response = self.gemini.generate_content(
            f"""Given the following risk assessment:
            {risk_assessment}
            
            For each high and medium risk, provide:
            1. Detailed mitigation strategy
            2. Required actions and responsible roles
            3. Timeline for implementation
            4. Resources needed
            5. Success metrics for the mitigation
            
            Prioritize recommendations by risk severity and feasibility.
            Format the response as a structured JSON object.
            """
        )
        
        return response.text