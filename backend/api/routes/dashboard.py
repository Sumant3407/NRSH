"""
Dashboard data endpoints
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.dashboard_service import DashboardService
from backend.services.config_manager import ConfigManager

router = APIRouter()

# Initialize services
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
config_path = project_root / "config" / "config.yaml"
config = ConfigManager(config_path)
dashboard_service = DashboardService(config)


@router.get("/summary")
async def get_dashboard_summary():
    """Get overall dashboard summary statistics"""
    try:
        summary = await dashboard_service.get_summary()
        return JSONResponse(content=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/map-data/{analysis_id}")
async def get_map_data(analysis_id: str):
    """Get geospatial data for map visualization"""
    try:
        map_data = await dashboard_service.get_map_data(analysis_id)
        return JSONResponse(content=map_data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline/{analysis_id}")
async def get_timeline(analysis_id: str):
    """Get temporal analysis data for timeline visualization"""
    try:
        timeline = await dashboard_service.get_timeline(analysis_id)
        return JSONResponse(content=timeline)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison/{analysis_id}")
async def get_comparison_frames(analysis_id: str, frame_index: Optional[int] = None):
    """Get before-after comparison frames"""
    try:
        comparison = await dashboard_service.get_comparison_frames(
            analysis_id, frame_index
        )
        return JSONResponse(content=comparison)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

