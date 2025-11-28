"""
Analysis service for running AI inference and processing
"""

import os
import json
import sys
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import asyncio

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.config_manager import ConfigManager
from backend.services.video_service import VideoService
from backend.services.database_service import get_database_service
from backend.models.database import AnalysisStatus, ElementType, Severity
from data_processing.frame_extraction import FrameExtractor
from data_processing.alignment import FrameAligner
from ai_models.detection.detector import ObjectDetector
from ai_models.change_detection.change_detector import ChangeDetector
import uuid


class AnalysisService:
    """Service for running video analysis"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.video_service = VideoService(config)
        self.results_dir = Path(config.get("storage.processed_dir", "processed"))
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.db_service = get_database_service()
        
        # Initialize AI models
        self.detector = ObjectDetector(config)
        self.change_detector = ChangeDetector(config)
        
        # Initialize processing components
        self.frame_extractor = FrameExtractor(config)
        self.frame_aligner = FrameAligner(config)
    
    async def run_analysis(
        self,
        analysis_id: str,
        base_video_id: str,
        present_video_id: str,
        road_segments: Optional[List[Dict]] = None,
        detection_elements: Optional[List[str]] = None
    ):
        """Run analysis comparing base and present videos"""
        # Create analysis directory
        analysis_dir = self.results_dir / analysis_id
        analysis_dir.mkdir(exist_ok=True)
        
        # Create analysis record in database if available
        if self.db_service:
            try:
                await self.db_service.create_analysis(
                    analysis_id=analysis_id,
                    base_video_id=base_video_id,
                    present_video_id=present_video_id
                )
            except Exception as e:
                print(f"Warning: Could not create analysis in database: {e}")
        
        # Update status
        await self._update_status(analysis_id, "processing", 0)
        
        try:
            # Get video info
            base_info = await self.video_service.get_video_info(base_video_id)
            present_info = await self.video_service.get_video_info(present_video_id)
            
            base_path = Path(base_info["file_path"])
            present_path = Path(present_info["file_path"])
            
            # Step 1: Extract frames
            await self._update_status(analysis_id, "processing", 10)
            base_frames = await self.frame_extractor.extract_frames(base_path)
            present_frames = await self.frame_extractor.extract_frames(present_path)
            
            # Step 2: Align frames
            await self._update_status(analysis_id, "processing", 30)
            aligned_pairs = await self.frame_aligner.align_frames(
                base_frames, present_frames,
                base_info.get("gps_data"), present_info.get("gps_data")
            )
            
            # Step 3: Run object detection
            await self._update_status(analysis_id, "processing", 50)
            detections = []
            for base_frame, present_frame, metadata in aligned_pairs:
                base_detections = await self.detector.detect(base_frame)
                present_detections = await self.detector.detect(present_frame)
                
                # Step 4: Detect changes
                changes = await self.change_detector.detect_changes(
                    base_detections, present_detections
                )
                
                detections.extend(changes)
            
            # Step 5: Aggregate results
            await self._update_status(analysis_id, "processing", 80)
            aggregated_results = await self._aggregate_results(
                detections, road_segments
            )
            
            # Step 6: Save detections to database if available
            if self.db_service and detections:
                try:
                    detection_records = []
                    for det in detections:
                        try:
                            element_type = ElementType(det.get("element_type", "pavement_crack"))
                            severity = Severity(det.get("severity", "minor"))
                            
                            detection_records.append({
                                "id": str(uuid.uuid4()),
                                "analysis_id": analysis_id,
                                "element_type": element_type.value,
                                "bbox": det.get("bbox", [0, 0, 0, 0]),
                                "confidence": det.get("confidence", 0.5),
                                "severity": severity.value,
                                "severity_score": det.get("severity_score", 0.0),
                                "gps_coords": det.get("gps_coords"),
                                "frame_number": det.get("frame_number"),
                                "created_at": datetime.now().isoformat()
                            })
                        except Exception as e:
                            print(f"Warning: Could not process detection: {e}")
                            continue
                    
                    if detection_records:
                        await self.db_service.bulk_create_detections(detection_records)
                except Exception as e:
                    print(f"Warning: Could not save detections to database: {e}")
            
            # Step 7: Save results
            summary = self._generate_summary(aggregated_results)
            results = {
                "analysis_id": analysis_id,
                "base_video_id": base_video_id,
                "present_video_id": present_video_id,
                "detections": detections,
                "aggregated_results": aggregated_results,
                "summary": summary,
                "created_at": datetime.now().isoformat(),
                "status": "completed"
            }
            
            results_file = analysis_dir / "results.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Update database with summary
            if self.db_service:
                try:
                    await self.db_service.update_analysis_status(
                        analysis_id=analysis_id,
                        status=AnalysisStatus.COMPLETED,
                        progress=100,
                        summary=summary
                    )
                except Exception as e:
                    print(f"Warning: Could not update analysis in database: {e}")
            
            await self._update_status(analysis_id, "completed", 100)
        
        except Exception as e:
            await self._update_status(analysis_id, "failed", 0, str(e))
            raise
    
    async def _update_status(
        self,
        analysis_id: str,
        status: str,
        progress: int,
        error: Optional[str] = None
    ):
        """Update analysis status"""
        # Update database if available
        if self.db_service:
            try:
                status_enum = AnalysisStatus(status)
                await self.db_service.update_analysis_status(
                    analysis_id=analysis_id,
                    status=status_enum,
                    progress=progress,
                    error=error
                )
            except Exception as e:
                print(f"Warning: Could not update status in database: {e}")
        
        # Fallback to file-based storage
        status_file = self.results_dir / analysis_id / "status.json"
        status_file.parent.mkdir(parents=True, exist_ok=True)
        
        status_data = {
            "analysis_id": analysis_id,
            "status": status,
            "progress": progress,
            "updated_at": datetime.now().isoformat()
        }
        
        if error:
            status_data["error"] = error
        
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
    
    async def get_analysis_status(self, analysis_id: str) -> Dict:
        """Get current analysis status"""
        # Try database first
        if self.db_service:
            try:
                analysis = await self.db_service.get_analysis(analysis_id)
                if analysis:
                    return {
                        "analysis_id": analysis.id,
                        "status": analysis.status,
                        "progress": analysis.progress,
                        "error": analysis.error,
                        "updated_at": analysis.updated_at.isoformat() if analysis.updated_at else None
                    }
            except Exception as e:
                print(f"Warning: Could not fetch from database: {e}. Using file-based storage.")
        
        # Fallback to file-based storage
        status_file = self.results_dir / analysis_id / "status.json"
        
        if not status_file.exists():
            raise FileNotFoundError(f"Analysis {analysis_id} not found")
        
        with open(status_file, 'r') as f:
            return json.load(f)
    
    async def get_analysis_results(self, analysis_id: str) -> Dict:
        """Get analysis results"""
        results_file = self.results_dir / analysis_id / "results.json"
        
        if not results_file.exists():
            raise FileNotFoundError(f"Analysis {analysis_id} results not found")
        
        with open(results_file, 'r') as f:
            return json.load(f)
    
    async def get_detections(self, analysis_id: str) -> List[Dict]:
        """Get all detections for an analysis"""
        # Try database first
        if self.db_service:
            try:
                detections = await self.db_service.get_detections(analysis_id)
                return [{
                    "id": d.id,
                    "analysis_id": d.analysis_id,
                    "element_type": d.element_type,
                    "bbox": d.bbox,
                    "confidence": d.confidence,
                    "severity": d.severity,
                    "severity_score": d.severity_score,
                    "gps_coords": d.gps_coords,
                    "frame_number": d.frame_number
                } for d in detections]
            except Exception as e:
                print(f"Warning: Could not fetch detections from database: {e}. Using file-based storage.")
        
        # Fallback to file-based storage
        results = await self.get_analysis_results(analysis_id)
        return results.get("detections", [])
    
    async def get_heatmap_data(self, analysis_id: str) -> Dict:
        """Get heatmap data for visualization"""
        detections = await self.get_detections(analysis_id)
        
        # Group by GPS location
        heatmap_points = []
        for detection in detections:
            if "gps_coords" in detection:
                heatmap_points.append({
                    "lat": detection["gps_coords"][0],
                    "lon": detection["gps_coords"][1],
                    "intensity": detection.get("severity_score", 1.0),
                    "type": detection.get("element_type", "unknown")
                })
        
        return {
            "points": heatmap_points,
            "bounds": self._calculate_bounds(heatmap_points)
        }
    
    async def _aggregate_results(
        self,
        detections: List[Dict],
        road_segments: Optional[List[Dict]] = None
    ) -> Dict:
        """Aggregate detections by road segment"""
        # Simple aggregation by element type and severity
        aggregation = {}
        
        for detection in detections:
            element_type = detection.get("element_type", "unknown")
            severity = detection.get("severity", "minor")
            
            if element_type not in aggregation:
                aggregation[element_type] = {
                    "total": 0,
                    "by_severity": {"minor": 0, "moderate": 0, "severe": 0}
                }
            
            aggregation[element_type]["total"] += 1
            aggregation[element_type]["by_severity"][severity] += 1
        
        return aggregation
    
    def _generate_summary(self, aggregated_results: Dict) -> Dict:
        """Generate summary statistics"""
        total_issues = sum(
            agg["total"] for agg in aggregated_results.values()
        )
        
        severe_issues = sum(
            agg["by_severity"]["severe"] for agg in aggregated_results.values()
        )
        
        return {
            "total_issues": total_issues,
            "severe_issues": severe_issues,
            "element_types": len(aggregated_results),
            "aggregated_results": aggregated_results
        }
    
    def _calculate_bounds(self, points: List[Dict]) -> Optional[Dict]:
        """Calculate bounding box for heatmap points"""
        if not points:
            return None
        
        lats = [p["lat"] for p in points]
        lons = [p["lon"] for p in points]
        
        return {
            "north": max(lats),
            "south": min(lats),
            "east": max(lons),
            "west": min(lons)
        }

