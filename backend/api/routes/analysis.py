"""
Analysis endpoints for video processing and AI inference
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
from pathlib import Path
import uuid

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.analysis_service import AnalysisService
from backend.services.config_manager import ConfigManager

router = APIRouter()

# Initialize services
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
config_path = project_root / "config" / "config.yaml"
config = ConfigManager(config_path)
analysis_service = AnalysisService(config)


class AnalysisRequest(BaseModel):
    base_video_id: str
    present_video_id: str
    road_segments: Optional[List[Dict]] = None  # GPS segments to analyze
    detection_elements: Optional[List[str]] = None  # Specific elements to detect


class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str


class DetectionResult(BaseModel):
    element_type: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    severity: str  # "minor", "moderate", "severe"
    gps_coords: Optional[List[float]] = None  # [lat, lon]


@router.post("/start", response_model=AnalysisResponse)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Start analysis comparing base and present videos
    
    This endpoint queues the analysis job and returns immediately.
    Use /status/{analysis_id} to check progress.
    """
    try:
        analysis_id = str(uuid.uuid4())
        
        # Add analysis task to background
        background_tasks.add_task(
            analysis_service.run_analysis,
            analysis_id=analysis_id,
            base_video_id=request.base_video_id,
            present_video_id=request.present_video_id,
            road_segments=request.road_segments,
            detection_elements=request.detection_elements
        )
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="queued",
            message="Analysis started. Check status endpoint for progress."
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get the status of an analysis job"""
    try:
        status = await analysis_service.get_analysis_status(analysis_id)
        return JSONResponse(content=status)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{analysis_id}")
async def get_analysis_results(analysis_id: str):
    """Get analysis results including detections and scores"""
    try:
        results = await analysis_service.get_analysis_results(analysis_id)
        return JSONResponse(content=results)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detections/{analysis_id}")
async def get_detections(analysis_id: str):
    """Get all detections for an analysis"""
    try:
        detections = await analysis_service.get_detections(analysis_id)
        return JSONResponse(content={"detections": detections})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heatmap/{analysis_id}")
async def get_heatmap_data(analysis_id: str):
    """Get heatmap data for visualization"""
    try:
        heatmap = await analysis_service.get_heatmap_data(analysis_id)
        return JSONResponse(content=heatmap)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

