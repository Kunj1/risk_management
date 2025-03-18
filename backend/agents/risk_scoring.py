from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key="YOUR_GEMINI_API_KEY")

risk_scoring_agent = Agent(
    role="Risk Assessor",
    goal="Score financial transactions and assess investment risks.",
    backstory="A risk analyst evaluating market volatility.",
    llm=llm
)