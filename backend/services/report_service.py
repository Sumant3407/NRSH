"""
Report generation service
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.config_manager import ConfigManager
from backend.services.analysis_service import AnalysisService


class ReportService:
    """Service for generating analysis reports"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.output_dir = Path(config.get("reporting.output_dir", "reports"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir = Path(config.get("reporting.template_dir", "templates"))
        self.analysis_service = AnalysisService(config)
    
    async def generate_report(
        self,
        analysis_id: str,
        report_type: str = "pdf",
        include_confidence_scores: bool = True,
        include_heatmaps: bool = True
    ) -> Path:
        """Generate a report for an analysis"""
        # Get analysis results
        results = await self.analysis_service.get_analysis_results(analysis_id)
        
        if report_type == "pdf":
            return await self._generate_pdf_report(
                analysis_id, results, include_confidence_scores, include_heatmaps
            )
        else:
            return await self._generate_json_report(analysis_id, results)
    
    async def _generate_pdf_report(
        self,
        analysis_id: str,
        results: Dict,
        include_confidence_scores: bool,
        include_heatmaps: bool
    ) -> Path:
        """Generate PDF report"""
        report_path = self.output_dir / f"report_{analysis_id}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(report_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for the 'Flowable' objects
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph("Road Safety Infrastructure Analysis Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Analysis metadata
        story.append(Paragraph(f"Analysis ID: {analysis_id}", styles['Normal']))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary section
        summary = results.get("summary", {})
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        
        summary_data = [
            ["Metric", "Value"],
            ["Total Issues Detected", str(summary.get("total_issues", 0))],
            ["Severe Issues", str(summary.get("severe_issues", 0))],
            ["Element Types", str(summary.get("element_types", 0))]
        ]
        
        summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Detailed results
        story.append(Paragraph("Detailed Findings", styles['Heading2']))
        
        aggregated = summary.get("aggregated_results", {})
        if aggregated:
            detail_data = [["Element Type", "Total", "Minor", "Moderate", "Severe"]]
            
            for element_type, counts in aggregated.items():
                detail_data.append([
                    element_type.replace("_", " ").title(),
                    str(counts.get("total", 0)),
                    str(counts.get("by_severity", {}).get("minor", 0)),
                    str(counts.get("by_severity", {}).get("moderate", 0)),
                    str(counts.get("by_severity", {}).get("severe", 0))
                ])
            
            detail_table = Table(detail_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(detail_table)
        
        # Build PDF
        doc.build(story)
        return report_path
    
    async def _generate_json_report(self, analysis_id: str, results: Dict) -> Path:
        """Generate JSON report"""
        report_path = self.output_dir / f"report_{analysis_id}.json"
        
        report_data = {
            "analysis_id": analysis_id,
            "generated_at": datetime.now().isoformat(),
            "results": results
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return report_path
    
    async def list_reports(self, analysis_id: str) -> List[Dict]:
        """List all reports for an analysis"""
        reports = []
        
        # Find all report files for this analysis
        for report_file in self.output_dir.glob(f"report_{analysis_id}.*"):
            reports.append({
                "filename": report_file.name,
                "type": report_file.suffix[1:],  # Remove the dot
                "size": report_file.stat().st_size,
                "created_at": datetime.fromtimestamp(
                    report_file.stat().st_ctime
                ).isoformat()
            })
        
        return reports
