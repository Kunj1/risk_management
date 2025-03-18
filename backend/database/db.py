from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from config.settings import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Define Project Risk Table
class ProjectRisk(Base):
    __tablename__ = "project_risks"
    
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, index=True)
    resource_availability = Column(Integer)
    schedule_delay = Column(Integer)
    customer_payment_received = Column(Boolean)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Create Tables
def init_db():
    Base.metadata.create_all(engine)
