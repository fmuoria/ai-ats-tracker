from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from .models import init_db
from .api import candidates_router, job_descriptions_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI ATS Tracker API",
    description="AI-Powered Applicant Tracking System with comprehensive candidate evaluation and job matching",
    version="2.0.0"
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(candidates_router)
app.include_router(job_descriptions_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("Database initialized successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI ATS Tracker API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
