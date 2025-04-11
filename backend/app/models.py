from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Text, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(100))
    role = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="manager")
    chat_logs = relationship("ChatLog", back_populates="user")


class Project(Base):
    __tablename__ = "projects"
    
    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), index=True)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(50))
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    resource_availability = Column(Integer)
    customer_payment_received = Column(Boolean, default=False)
    schedule_delay = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    manager = relationship("User", back_populates="projects")
    risk_logs = relationship("RiskLog", back_populates="project")
    alerts = relationship("Alert", back_populates="project")


class RiskLog(Base):
    __tablename__ = "risk_logs"
    
    risk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id"))
    risk_type = Column(String(50))
    risk_score = Column(Float)
    details = Column(Text)
    timestamp = Column(DateTime, server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="risk_logs")


class Alert(Base):
    __tablename__ = "alerts"
    
    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id"))
    alert_type = Column(String(50))
    message = Column(Text)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="alerts")


class ChatLog(Base):
    __tablename__ = "chat_logs"
    
    chat_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    message = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_logs")