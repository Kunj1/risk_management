# project_status_agent.py
from crewai import Agent, Task
from backend.utils.gemini_client import get_gemini_client
from backend.data.database import get_db_client

class ProjectStatusAgent:
    def __init__(self):
        self.gemini = get_gemini_client()
        self.db_client = get_db_client()
        
    def get_agent(self):
        """Return the CrewAI agent for project status tracking"""
        return Agent(
            role="Project Status Tracker",
            goal="Monitor project progress and identify internal risks",
            backstory="""You are an experienced project manager with a keen eye for
                      spotting potential issues before they become problems. You can
                      analyze project metrics and identify resource constraints, schedule
                      delays, and other internal factors that might put a project at risk.""",
            verbose=True,
            allow_delegation=True,
            tools=[self.analyze_project_metrics, self.check_resource_availability]
        )
    
    def create_status_task(self, project_id):
        """Create a task for tracking project status"""
        project = self.db_client.from_("projects").select("*").eq("id", project_id).single().execute().data
        
        return Task(
            description=f"""Analyze the current status of project {project['name']}.
                        Review the following project parameters:
                        1. Resource allocation and availability
                        2. Schedule adherence and milestone completion
                        3. Budget utilization and financial health
                        4. Team performance and productivity metrics
                        5. Quality metrics and deliverable status
                        
                        Identify any internal risks that could impact project success.
                        """,
            expected_output="A JSON object containing internal project risks categorized by type and severity",
            agent=self.get_agent()
        )
    
    def analyze_project_metrics(self, project_id):
        """Tool to analyze project metrics"""
        # In a real implementation, this would pull from project management tools
        # For this example, we'll simulate project metrics
        
        project = self.db_client.from_("projects").select("*").eq("id", project_id).single().execute().data
        
        response = self.gemini.generate_content(
            f"""Generate realistic project metrics for an IT project named {project['name']} in the 
            {project['industry']} industry using {project['technology']} technology. Include:
            1. Schedule metrics (planned vs. actual)
            2. Budget metrics (planned vs. actual)
            3. Resource utilization
            4. Quality metrics (defects, issues)
            5. Team productivity indicators
            
            Format the response as a structured JSON object.
            """
        )
        
        return response.text
    
    def check_resource_availability(self, project_id):
        """Tool to check resource availability for a project"""
        # In a real implementation, this would pull from resource management systems
        # For this example, we'll simulate resource data
        
        project = self.db_client.from_("projects").select("*").eq("id", project_id).single().execute().data
        
        response = self.gemini.generate_content(
            f"""Generate realistic resource availability data for an IT project named {project['name']} 
            using {project['technology']} technology. Include:
            1. Team member allocation and availability
            2. Skills coverage and gaps
            3. Potential resource conflicts
            4. Upcoming vacation or time off
            5. Critical resource dependencies
            
            Format the response as a structured JSON object.
            """
        )
        
        return response.text