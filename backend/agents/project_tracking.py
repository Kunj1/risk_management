from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key="YOUR_GEMINI_API_KEY")

project_tracking_agent = Agent(
    role="Project Status Tracker",
    goal="Track project progress, resource availability, and delays.",
    backstory="An AI project manager ensuring project success.",
    llm=llm
)