"""
FastAPI Backend for Road Safety Infrastructure Analysis
"""

import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import yaml

from backend.api.routes import video, analysis, reports, dashboard
from backend.services.config_manager import ConfigManager

# Load configuration
config_path = project_root / "config" / "config.yaml"
config_manager = ConfigManager(config_path)

app = FastAPI(
    title="Road Safety Infrastructure Analysis API",
    description="AI-powered road infrastructure analysis system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config_manager.get("api.cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(video.router, prefix="/api/v1/video", tags=["Video"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Road Safety Infrastructure Analysis API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "road-safety-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config_manager.get("api.host", "0.0.0.0"),
        port=config_manager.get("api.port", 8000),
        reload=True
    )

