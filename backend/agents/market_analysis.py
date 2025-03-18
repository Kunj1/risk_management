from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key="YOUR_GEMINI_API_KEY")

market_analysis_agent = Agent(
    role="Market Risk Analyst",
    goal="Analyze financial news and external market risks.",
    backstory="A financial expert tracking global markets.",
    llm=llm
)