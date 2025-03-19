# risk_scoring_agent.py
from crewai import Agent, Task
from ..utils.gemini_client import get_gemini_client
from ..data.database import get_db_client

class RiskScoringAgent:
    def __init__(self):
        self.gemini = get_gemini_client()
        self.db_client = get_db_client()
        
    def get_agent(self):
        """Return the CrewAI agent for risk scoring"""
        return Agent(
            role="Risk Assessment Specialist",
            goal="Accurately assess and score all identified project risks",
            backstory="""You are a risk assessment specialist with a background in
                      quantitative analysis. You can evaluate the probability and impact
                      of identified risks and assign appropriate scores and prioritization.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.calculate_risk_score, self.generate_risk_matrix]
        )
    
    def create_scoring_task(self, project_id):
        """Create a task for scoring project risks"""
        project = self.db_client.from_("projects").select("*").eq("id", project_id).single().execute().data
        
        return Task(
            description=f"""Evaluate all identified risks for project {project['name']}.
                        Using the market analysis and project status data:
                        1. Assign probability scores (1-5) to each risk
                        2. Assign impact scores (1-5) to each risk
                        3. Calculate overall risk scores (probability × impact)
                        4. Categorize risks by severity
                        5. Prioritize risks for mitigation
                        
                        Consider both external market risks and internal project risks.
                        """,
            expected_output="A comprehensive risk assessment with scores, categories, and priorities",
            agent=self.get_agent()
        )
    
    def calculate_risk_score(self, risks_data):
        """Tool to calculate risk scores based on probability and impact"""
        # In a real implementation, this would apply a risk model
        # For this example, we'll use Gemini to simulate risk scoring
        
        response = self.gemini.generate_content(
            f"""Given the following identified risks:
            {risks_data}
            
            Calculate for each risk:
            1. Probability score (1-5)
            2. Impact score (1-5)
            3. Overall risk score (probability × impact)
            4. Risk category (High: 15-25, Medium: 8-14, Low: 1-7)
            
            Format the response as a structured JSON object with all risks and their scores.
            """
        )
        
        return response.text
    
    def generate_risk_matrix(self, scored_risks):
        """Tool to generate a risk matrix visualization data"""
        # This would generate data for visualizing risks in a matrix
        
        response = self.gemini.generate_content(
            f"""Given the following scored risks:
            {scored_risks}
            
            Generate data for a 5x5 risk matrix visualization where:
            - X-axis represents Impact (1-5)
            - Y-axis represents Probability (1-5)
            - Each risk is positioned according to its scores
            - Include risk IDs and brief descriptions at each position
            
            Format the response as a structured JSON object suitable for visualization.
            """
        )
        
        return response.text