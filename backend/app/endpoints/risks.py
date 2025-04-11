from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional
import uuid

from app.db.database import get_db
from app.models import User, Project, RiskLog
from app.schemas import RiskLogCreate, RiskLogOut, ProjectRiskScoreResponse
from app.utils.security import get_current_user
from app.agents.risk_scoring import calculate_project_risk_score

router = APIRouter()

@router.post("/logs", response_model=RiskLogOut, status_code=status.HTTP_201_CREATED)
def create_risk_log(
    risk_in: RiskLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new risk log for a project.
    """
    # Verify project exists and belongs to user
    project = db.query(Project).filter(
        Project.project_id == risk_in.project_id,
        Project.manager_id == current_user.user_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or not authorized"
        )
    
    # Create risk log
    risk_log = RiskLog(**risk_in.dict())
    
    # Add to database
    db.add(risk_log)
    db.commit()
    db.refresh(risk_log)
    
    return risk_log

@router.get("/logs", response_model=List[RiskLogOut])
def read_risk_logs(
    project_id: Optional[uuid.UUID] = None,
    risk_type: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get risk logs with optional filtering.
    """
    # Base query - all projects managed by the user
    query = db.query(RiskLog).join(Project).filter(Project.manager_id == current_user.user_id)
    
    # Apply filters
    if project_id:
        query = query.filter(RiskLog.project_id == project_id)
    
    if risk_type:
        query = query.filter(RiskLog.risk_type == risk_type)
    
    if min_score is not None:
        query = query.filter(RiskLog.risk_score >= min_score)
    
    if max_score is not None:
        query = query.filter(RiskLog.risk_score <= max_score)
    
    # Get results
    risk_logs = query.order_by(RiskLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return risk_logs

@router.get("/score/{project_id}", response_model=ProjectRiskScoreResponse)
async def get_project_risk_score(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Calculate and return the risk score for a project.
    """
    # Verify project exists and belongs to user
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.manager_id == current_user.user_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or not authorized"
        )
    
    # Calculate risk score using the risk scoring agent
    risk_score_response = await calculate_project_risk_score(project, db)
    
    return risk_score_response