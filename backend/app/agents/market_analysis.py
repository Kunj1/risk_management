import logging
import aiohttp
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import os
import json

from app.schemas import MarketAnalysisResponse, MarketIndicator
from app.config import settings
from app.utils.logger import LoggerMixin

from crewai import Agent, Task, Crew
from crewai.tools import SerperDevTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chat_models import ChatOpenAI

logger = logging.getLogger(__name__)

class MarketAnalysisAgent(LoggerMixin):
    """
    Agent responsible for analyzing market trends and economic indicators.
    """
    
    def __init__(self):
        self.alpha_vantage_api_key = settings.ALPHA_VANTAGE_API_KEY
        self.financial_modeling_prep_api_key = settings.FINANCIAL_MODELING_PREP_API_KEY
        
    async def fetch_market_data(self) -> Dict[str, Any]:
        """
        Fetch market data from external APIs.
        """
        self.logger.info("Fetching market data from external sources")
        
        market_data = {
            "stock_market": {},
            "forex": {},
            "commodities": {},
            "economic_indicators": {}
        }
        
        try:
            # Fetch stock market data
            if self.alpha_vantage_api_key:
                async with aiohttp.ClientSession() as session:
                    # Get S&P 500 data
                    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&apikey={self.alpha_vantage_api_key}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            if "Global Quote" in data:
                                market_data["stock_market"]["sp500"] = data["Global Quote"]
                    
                    # Get NASDAQ data
                    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=QQQ&apikey={self.alpha_vantage_api_key}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            if "Global Quote" in data:
                                market_data["stock_market"]["nasdaq"] = data["Global Quote"]
            
            # Fetch economic indicators
            if self.financial_modeling_prep_api_key:
                async with aiohttp.ClientSession() as session:
                    # Get economic indicators
                    url = f"https://financialmodelingprep.com/api/v3/economic-calendar?apikey={self.financial_modeling_prep_api_key}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            market_data["economic_indicators"]["calendar"] = data[:10]  # Just get the latest 10 events
            
            # If no API keys are available, use mock data for development/testing
            if not self.alpha_vantage_api_key and not self.financial_modeling_prep_api_key:
                self.logger.warning("No API keys available, using mock market data")
                market_data = self._get_mock_market_data()
                
        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            # Use mock data as fallback
            market_data = self._get_mock_market_data()
            
        return market_data
            
    def _get_mock_market_data(self) -> Dict[str, Any]:
        """
        Generate mock market data for development/testing.
        """
        return {
            "stock_market": {
                "sp500": {"price": "4750.12", "change_percent": "0.75%"},
                "nasdaq": {"price": "16120.45", "change_percent": "0.92%"}
            },
            "forex": {
                "eur_usd": {"rate": "1.0842", "change_percent": "-0.12%"},
                "gbp_usd": {"rate": "1.2651", "change_percent": "0.05%"}
            },
            "commodities": {
                "gold": {"price": "2342.10", "change_percent": "0.33%"},
                "oil": {"price": "78.65", "change_percent": "-1.25%"}
            },
            "economic_indicators": {
                "unemployment": "3.8%",
                "inflation": "2.9%",
                "gdp_growth": "2.1%",
                "interest_rate": "5.5%"
            }
        }
    
    async def analyze_market_impact(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to analyze the market data and determine impact on projects.
        """
        self.logger.info("Analyzing market data impact with AI")
        
        # Set up CrewAI for market analysis
        try:
            # Select LLM based on available API keys
            if settings.GEMINI_API_KEY:
                llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=settings.GEMINI_API_KEY)
            elif settings.OPENAI_API_KEY:
                llm = ChatOpenAI(model="gpt-4", api_key=settings.OPENAI_API_KEY)
            else:
                self.logger.error("No LLM API key available for market analysis")
                return self._get_mock_analysis_results()
            
            # Create the market analyst agent
            market_analyst = Agent(
                role="Market Risk Analyst",
                goal="Analyze market trends and their impact on IT projects",
                backstory="""You are an expert in analyzing financial markets and economic indicators
                to determine how they might impact IT projects. You look for trends, warning signs,
                and opportunities that could affect project success.""",
                verbose=True,
                llm=llm,
                tools=[SerperDevTool()]
            )
            
            # Format market data for analysis
            market_data_json = json.dumps(market_data, indent=2)
            
            # Create the analysis task
            analysis_task = Task(
                description=f"""
                Analyze the following market data and determine how it might impact IT projects:
                
                {market_data_json}
                
                Consider factors like:
                - Overall market sentiment
                - Economic stability
                - Industry-specific trends for IT and technology
                - Potential impact on client budgets and project funding
                - Supply chain impacts for hardware or other resources
                
                Return your analysis in JSON format with these fields:
                - indicators: A list of key market indicators with name, value, impact_level (high/medium/low), and trend (positive/negative/neutral)
                - overall_market_sentiment: A brief assessment of overall market conditions
                - potential_impact_on_projects: Specific ways these conditions might affect IT projects
                """
                ,
                agent=market_analyst
            )
            
            # Execute the analysis
            crew = Crew(
                agents=[market_analyst],
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
                    return self._get_mock_analysis_results()
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse JSON from AI response, using mock data")
                return self._get_mock_analysis_results()
                
        except Exception as e:
            self.logger.error(f"Error during market impact analysis: {str(e)}")
            return self._get_mock_analysis_results()
    
    def _get_mock_analysis_results(self) -> Dict[str, Any]:
        """
        Generate mock analysis results when AI analysis fails.
        """
        return {
            "indicators": [
                {
                    "name": "S&P 500",
                    "value": 4750.12,
                    "impact_level": "medium",
                    "trend": "positive"
                },
                {
                    "name": "Inflation Rate",
                    "value": 2.9,
                    "impact_level": "high",
                    "trend": "negative"
                },
                {
                    "name": "Tech Sector Growth",
                    "value": 3.5,
                    "impact_level": "high",
                    "trend": "positive"
                },
                {
                    "name": "Interest Rates",
                    "value": 5.5,
                    "impact_level": "medium",
                    "trend": "neutral"
                }
            ],
            "overall_market_sentiment": "Cautiously optimistic with some headwinds from inflation",
            "potential_impact_on_projects": "Rising costs may affect budgets, but strong tech sector growth suggests continued investment in IT projects. Monitor client financial health closely."
        }


async def analyze_market_trends() -> MarketAnalysisResponse:
    """
    Analyze market trends and return formatted data.
    This is the main function to be called by the API endpoint.
    """
    agent = MarketAnalysisAgent()
    
    # Fetch market data
    market_data = await agent.fetch_market_data()
    
    # Analyze the impact
    analysis_results = await agent.analyze_market_impact(market_data)
    
    # Format the response according to schema
    indicators = [
        MarketIndicator(
            name=indicator["name"],
            value=float(indicator["value"]) if isinstance(indicator["value"], (int, float)) else 0.0,
            impact_level=indicator["impact_level"],
            trend=indicator["trend"]
        )
        for indicator in analysis_results.get("indicators", [])
    ]
    
    return MarketAnalysisResponse(
        timestamp=datetime.now(),
        indicators=indicators,
        overall_market_sentiment=analysis_results.get("overall_market_sentiment", ""),
        potential_impact_on_projects=analysis_results.get("potential_impact_on_projects", "")
    )