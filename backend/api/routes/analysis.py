import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.analysis_service import AnalysisService
from backend.services.config_manager import ConfigManager

router = APIRouter()


# Function: get_analysis_service
def get_analysis_service():
    """Get analysis service instance"""
    project_root = Path(__file__).parent.parent.parent.parent
    config_path = project_root / "config" / "config.yaml"
    config = ConfigManager(config_path)
    return AnalysisService(config)


# Class: AnalysisRequest
class AnalysisRequest(BaseModel):
    base_video_id: str
    present_video_id: str
    road_segments: Optional[List[Dict]] = None  # GPS segments to analyze
    detection_elements: Optional[List[str]] = None  # Specific elements to detect


# Class: AnalysisResponse
class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str


# Class: SingleDetectRequest
class SingleDetectRequest(BaseModel):
    video_id: str
    detection_elements: Optional[List[str]] = None


# Class: SingleDetectResponse
class SingleDetectResponse(BaseModel):
    analysis_id: str
    status: str
    message: str
    summary: Dict
    detections: List[Dict]


# Class: DetectionResult
class DetectionResult(BaseModel):
    element_type: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    severity: str  # "minor", "moderate", "severe"
    gps_coords: Optional[List[float]] = None  # [lat, lon]


@router.post("/start", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Start analysis comparing base and present videos

    This endpoint queues the analysis job and returns immediately.
    Use /status/{analysis_id} to check progress.
    """
    try:
        if request.detection_elements is not None:
            if not isinstance(request.detection_elements, list) or not all(
                isinstance(x, str) for x in request.detection_elements
            ):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "INVALID_DETECTION_ELEMENTS",
                        "message": "detection_elements must be a list of strings",
                    },
                )

        analysis_id = str(uuid.uuid4())

        analysis_service = get_analysis_service()

        background_tasks.add_task(
            analysis_service.run_analysis,
            analysis_id=analysis_id,
            base_video_id=request.base_video_id,
            present_video_id=request.present_video_id,
            road_segments=request.road_segments,
            detection_elements=request.detection_elements,
        )

        return AnalysisResponse(
            analysis_id=analysis_id,
            status="queued",
            message="Analysis started. Check status endpoint for progress.",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect", response_model=SingleDetectResponse)
async def detect_single_media(request: SingleDetectRequest):
    """
    Run detection on a single media file (image or video) previously uploaded.
    Returns detections and a summary without change detection.
    """
    try:
        if request.detection_elements is not None:
            if not isinstance(request.detection_elements, list) or not all(
                isinstance(x, str) for x in request.detection_elements
            ):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "INVALID_DETECTION_ELEMENTS",
                        "message": "detection_elements must be a list of strings",
                    },
                )

        analysis_id = str(uuid.uuid4())

        analysis_service = get_analysis_service()

        await analysis_service.run_single_detection(
            analysis_id=analysis_id,
            video_id=request.video_id,
            detection_elements=request.detection_elements,
        )

        results = await analysis_service.get_analysis_results(analysis_id)

        return SingleDetectResponse(
            analysis_id=analysis_id,
            status="completed",
            message="Single media detection completed.",
            summary=results.get("summary", {}),
            detections=results.get("detections", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get the status of an analysis job"""
    try:
        analysis_service = get_analysis_service()
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
        analysis_service = get_analysis_service()
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
        analysis_service = get_analysis_service()
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
        analysis_service = get_analysis_service()
        heatmap = await analysis_service.get_heatmap_data(analysis_id)
        return JSONResponse(content=heatmap)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
