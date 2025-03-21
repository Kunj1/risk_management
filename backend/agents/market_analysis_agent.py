# market_analysis_agent.py
from crewai import Agent, Task
from backend.utils.gemini_client import get_gemini_client
from backend.data.database import get_db_client

class MarketAnalysisAgent:
    def __init__(self):
        self.gemini = get_gemini_client()
        self.db_client = get_db_client()
        
    def get_agent(self):
        """Return the CrewAI agent for market analysis"""
        return Agent(
            role="Market Analysis Expert",
            goal="Analyze market trends and economic indicators relevant to the project",
            backstory="""You are an expert in market analysis with years of experience 
                      in predicting how market trends affect IT projects. You can identify
                      economic indicators that might impact project success.""",
            verbose=True,
            allow_delegation=True,
            tools=[self.fetch_market_data, self.analyze_news]
        )
    
    def create_analysis_task(self, project_id):
        """Create a task for analyzing market conditions for a project"""
        project = self.db_client.from_("projects").select("*").eq("id", project_id).single().execute().data
        
        return Task(
            description=f"""Analyze current market conditions that might affect project {project['name']}.
                        Industry: {project['industry']}
                        Technology stack: {project['technology']}
                        Expected duration: {project['duration']} months
                        
                        Provide a detailed analysis of market risks including:
                        1. Economic indicators affecting this industry
                        2. Supply chain risks for the technology stack
                        3. Market competition and potential disruptions
                        4. Regulatory changes that might impact the project
                        """,
            expected_output="A JSON object containing market risks categorized by severity (high/medium/low)",
            agent=self.get_agent()
        )
    
    def fetch_market_data(self, industry, technology):
        """Tool to fetch market data relevant to an industry and technology"""
        # In a real implementation, this would call external APIs or databases
        # For this example, we'll simulate data
        
        # Simulated market data response
        response = self.gemini.generate_content(
            f"""Generate realistic current market data for the {industry} industry 
            and {technology} technology stack. Include:
            1. Growth trends
            2. Major players
            3. Supply chain issues
            4. Economic indicators
            
            Format the response as a structured JSON object.
            """
        )
        
        # Parse and return the JSON data
        return response.text
    
    def analyze_news(self, industry, technology, timeframe="last 3 months"):
        """Tool to analyze recent news relevant to an industry and technology"""
        # In a real implementation, this would call news APIs
        # For this example, we'll simulate news analysis
        
        response = self.gemini.generate_content(
            f"""Generate a realistic news analysis summary for the {industry} industry 
            and {technology} technology stack from the {timeframe}. Include:
            1. Major events
            2. Emerging trends
            3. Regulatory changes
            4. Potential disruptions
            
            Format the response as a structured JSON object.
            """
        )
        
        return response.text