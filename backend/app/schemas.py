from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: str = "project_manager"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None


class UserOut(UserBase):
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: str
    start_date: date
    end_date: date
    resource_availability: int = Field(..., ge=0, le=100)
    customer_payment_received: bool = False
    schedule_delay: int = 0


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    resource_availability: Optional[int] = None
    customer_payment_received: Optional[bool] = None
    schedule_delay: Optional[int] = None


class ProjectOut(ProjectBase):
    project_id: UUID
    status: str
    manager_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Risk log schemas
class RiskLogBase(BaseModel):
    project_id: UUID
    risk_type: str
    risk_score: float = Field(..., ge=0, le=1)
    details: str


class RiskLogCreate(RiskLogBase):
    pass


class RiskLogOut(RiskLogBase):
    risk_id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


# Alert schemas
class AlertBase(BaseModel):
    project_id: UUID
    alert_type: str
    message: str


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    is_acknowledged: bool = True


class AlertOut(AlertBase):
    alert_id: UUID
    is_acknowledged: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Chat schemas
class ChatMessageIn(BaseModel):
    message: str


class ChatMessageOut(BaseModel):
    chat_id: UUID
    user_id: UUID
    message: str
    response: str
    timestamp: datetime

    class Config:
        from_attributes = True


# Market analysis schemas
class MarketIndicator(BaseModel):
    name: str
    value: float
    impact_level: str
    trend: str


class MarketAnalysisResponse(BaseModel):
    timestamp: datetime
    indicators: List[MarketIndicator]
    overall_market_sentiment: str
    potential_impact_on_projects: str


# Risk scoring schemas
class RiskFactorScore(BaseModel):
    factor_name: str
    score: float
    weight: float
    description: str


class ProjectRiskScoreResponse(BaseModel):
    project_id: UUID
    project_name: str
    overall_risk_score: float
    risk_factors: List[RiskFactorScore]
    timestamp: datetime
    recommendations: List[str]


# Report schemas
class ReportRequest(BaseModel):
    project_ids: Optional[List[UUID]] = None  # None means all projects
    report_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ReportData(BaseModel):
    title: str
    summary: str
    risk_metrics: Dict[str, Any]
    charts_data: Optional[Dict[str, Any]] = None
    recommendations: List[str]


class ReportResponse(BaseModel):
    report_id: str
    generated_at: datetime
    report_type: str
    data: ReportData