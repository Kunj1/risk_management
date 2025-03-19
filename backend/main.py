# main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agents.project_risk_manager import ProjectRiskManager
from data.database import initialize_db

app = FastAPI(title="Project Risk Management API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database connection
initialize_db()

# Create risk manager instance
risk_manager = ProjectRiskManager()

@app.get("/")
async def root():
    return {"message": "Project Risk Management API is running"}

@app.get("/projects")
async def get_projects():
    return risk_manager.get_all_projects()

@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    return risk_manager.get_project_details(project_id)

@app.get("/projects/{project_id}/risks")
async def get_project_risks(project_id: str):
    return risk_manager.get_project_risks(project_id)

@app.post("/analyze")
async def analyze_project(project_id: str):
    return risk_manager.run_risk_analysis(project_id)

@app.post("/chat")
async def chat_endpoint(message: dict):
    return risk_manager.process_chat_message(message["content"], message["project_id"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)