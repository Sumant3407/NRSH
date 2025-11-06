"""
Report generation endpoints
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.report_service import ReportService
from backend.services.config_manager import ConfigManager

router = APIRouter()

# Initialize services
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
config_path = project_root / "config" / "config.yaml"
config = ConfigManager(config_path)
report_service = ReportService(config)


class ReportRequest(BaseModel):
    analysis_id: str
    report_type: str = "pdf"  # "pdf" or "json"
    include_confidence_scores: bool = True
    include_heatmaps: bool = True


@router.post("/generate")
async def generate_report(request: ReportRequest):
    """
    Generate a report for an analysis
    
    - **analysis_id**: ID of the analysis to report on
    - **report_type**: Type of report - "pdf" or "json"
    - **include_confidence_scores**: Include confidence scores in report
    - **include_heatmaps**: Include heatmap visualizations
    """
    try:
        report_path = await report_service.generate_report(
            analysis_id=request.analysis_id,
            report_type=request.report_type,
            include_confidence_scores=request.include_confidence_scores,
            include_heatmaps=request.include_heatmaps
        )
        
        if request.report_type == "pdf":
            return FileResponse(
                report_path,
                media_type="application/pdf",
                filename=f"report_{request.analysis_id}.pdf"
            )
        else:
            # Return JSON report
            import json
            with open(report_path, 'r') as f:
                report_data = json.load(f)
            return JSONResponse(content=report_data)
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{analysis_id}")
async def list_reports(analysis_id: str):
    """List all generated reports for an analysis"""
    try:
        reports = await report_service.list_reports(analysis_id)
        return JSONResponse(content={"reports": reports})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

