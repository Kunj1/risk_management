from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .db.database import engine, Base
from .endpoints import auth, projects, risks, market, reporting, chat
from .utils.logger import setup_logging

# Initialize the FastAPI application
app = FastAPI(
    title="Project Risk Management API",
    description="API for monitoring project risks and generating reports",
    version="1.0.0"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(risks.router, prefix="/risks", tags=["Risks"])
app.include_router(market.router, prefix="/market", tags=["Market Analysis"])
app.include_router(reporting.router, prefix="/reports", tags=["Reporting"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the API server")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the API server")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)