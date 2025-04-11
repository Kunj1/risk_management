from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List

from app.db.database import get_db
from app.models import User
from app.schemas import MarketAnalysisResponse
from app.utils.security import get_current_user
from app.agents.market_analysis import analyze_market_trends

router = APIRouter()

@router.get("/analysis", response_model=MarketAnalysisResponse)
async def get_market_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get market analysis data and trends.
    """
    try:
        # Use the market analysis agent to get market trends and indicators
        market_analysis = await analyze_market_trends()
        return market_analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing market trends: {str(e)}"
        )