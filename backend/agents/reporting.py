from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key="YOUR_GEMINI_API_KEY")

reporting_agent = Agent(
    role="Risk Reporter",
    goal="Generate risk reports and provide mitigation strategies.",
    backstory="An AI-driven consultant providing risk insights.",
    llm=llm
)