import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.config_manager import ConfigManager
from backend.services.report_service import ReportService

router = APIRouter()


# Function: get_report_service
def get_report_service():
    """Get report service instance"""
    project_root = Path(__file__).parent.parent.parent.parent
    config_path = project_root / "config" / "config.yaml"
    config = ConfigManager(config_path)
    return ReportService(config)


# Class: ReportRequest
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
        report_service = get_report_service()
        report_path = await report_service.generate_report(
            analysis_id=request.analysis_id,
            report_type=request.report_type,
            include_confidence_scores=request.include_confidence_scores,
            include_heatmaps=request.include_heatmaps,
        )

        if request.report_type == "pdf":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"NRSH_Report_{request.analysis_id}_{timestamp}.pdf"

            return FileResponse(
                report_path,
                media_type="application/pdf",
                filename=filename,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                },
            )
        else:
            import json

            with open(report_path, "r") as f:
                report_data = json.load(f)
            return JSONResponse(content=report_data)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis '{request.analysis_id}' not found. Please ensure the analysis has completed successfully.",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid request parameters: {str(e)}"
        )
    except Exception as e:
        import logging

        logging.error(
            f"Report generation failed for analysis {request.analysis_id}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}. Please try again or contact support if the issue persists.",
        )


@router.get("/list/{analysis_id}")
async def list_reports(analysis_id: str):
    """List all generated reports for an analysis"""
    try:
        report_service = get_report_service()
        reports = await report_service.list_reports(analysis_id)
        return JSONResponse(content={"reports": reports})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
