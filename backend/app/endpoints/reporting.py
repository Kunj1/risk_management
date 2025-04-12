from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional
import uuid
from datetime import datetime, date

from ..db.database import get_db
from ..models import User, Project, Alert, RiskLog
from ..schemas import AlertCreate, AlertOut, AlertUpdate, ReportRequest, ReportResponse
from ..utils.security import get_current_user
from ..agents.reporting_agent import generate_risk_report

router = APIRouter()

# --- Reports Endpoints ---

@router.post("/generate", response_model=ReportResponse)
async def create_report(
    report_request: ReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Generate a risk report based on the request parameters.
    """
    # Validate project IDs if provided
    if report_request.project_ids:
        for project_id in report_request.project_ids:
            project = db.query(Project).filter(
                Project.project_id == project_id,
                Project.manager_id == current_user.user_id
            ).first()
            
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with ID {project_id} not found or not authorized"
                )
    
    # Generate report using the reporting agent
    try:
        report = await generate_risk_report(
            db=db,
            user_id=current_user.user_id,
            project_ids=report_request.project_ids,
            report_type=report_request.report_type,
            start_date=report_request.start_date,
            end_date=report_request.end_date
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )

# --- Alerts Endpoints ---

@router.get("/alerts", response_model=List[AlertOut])
def read_alerts(
    project_id: Optional[uuid.UUID] = None,
    alert_type: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get all alerts with optional filtering.
    """
    # Base query - all alerts for projects managed by the user
    query = db.query(Alert).join(Project).filter(Project.manager_id == current_user.user_id)
    
    # Apply filters
    if project_id:
        query = query.filter(Alert.project_id == project_id)
    
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    
    if acknowledged is not None:
        query = query.filter(Alert.is_acknowledged == acknowledged)
    
    # Get results
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    
    return alerts

@router.post("/alerts", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert_in: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new alert for a project.
    """
    # Verify project exists and belongs to user
    project = db.query(Project).filter(
        Project.project_id == alert_in.project_id,
        Project.manager_id == current_user.user_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or not authorized"
        )
    
    # Create alert
    alert = Alert(**alert_in.dict())
    
    # Add to database
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    return alert

@router.put("/alerts/{alert_id}", response_model=AlertOut)
def update_alert(
    alert_id: uuid.UUID,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update an alert (e.g., mark as acknowledged).
    """
    # Find the alert and ensure it belongs to a project managed by the user
    alert = db.query(Alert).join(Project).filter(
        Alert.alert_id == alert_id,
        Project.manager_id == current_user.user_id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found or not authorized"
        )
    
    # Update alert attributes
    for field, value in alert_update.dict(exclude_unset=True).items():
        setattr(alert, field, value)
    
    db.commit()
    db.refresh(alert)
    
    return alert