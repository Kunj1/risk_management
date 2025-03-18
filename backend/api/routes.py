from fastapi import FastAPI, Depends
from backend.database.db import SessionLocal, ProjectRisk
from backend.agents.reporting import reporting_agent

app = FastAPI()

# Get Project Risks
@app.get("/project-risks")
def get_project_risks():
    db = SessionLocal()
    risks = db.query(ProjectRisk).all()
    return {"project_risks": risks}

# Get Risk Report
@app.get("/risk-report")
def get_risk_report():
    report = reporting_agent.run("Analyze project risks and generate mitigation strategies.")
    return {"risk_report": report}