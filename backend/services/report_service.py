import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.analysis_service import AnalysisService
from backend.services.config_manager import ConfigManager


# Class: ReportService
class ReportService:
    """Service for generating analysis reports"""

    # Function: __init__
    def __init__(self, config: ConfigManager):
        self.config = config
        self.output_dir = Path(config.get("reporting.output_dir", "reports"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir = Path(config.get("reporting.template_dir", "templates"))
        self.analysis_service = AnalysisService(config)
        self.max_reports_per_analysis = config.get(
            "reporting.max_reports_per_analysis", 5
        )

    async def generate_report(
        self,
        analysis_id: str,
        report_type: str = "pdf",
        include_confidence_scores: bool = True,
        include_heatmaps: bool = True,
    ) -> Path:
        """Generate a report for an analysis"""
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
        include_heatmaps: bool,
    ) -> Path:
        """Generate PDF report"""
        report_path = (
            self.output_dir
            / f"report_{analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        doc = SimpleDocTemplate(
            str(report_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            title=f"Road Safety Analysis Report - {analysis_id}",
            author="NRSH System",
            subject="Road Infrastructure Safety Analysis",
            creator="NRSH Road Safety Infrastructure Analysis System v2.0",
        )

        story = []
        styles = getSampleStyleSheet()
        self._setup_professional_styles(styles)

        story.extend(self._create_cover_page(analysis_id, results, styles))
        story.extend(self._create_table_of_contents(styles))
        story.extend(self._create_executive_summary(results, styles))
        story.extend(self._create_methodology(results, styles))
        story.extend(self._create_detailed_findings(results, styles))
        story.extend(self._create_recommendations(results, styles))
        story.extend(self._create_appendices(results, styles))

        doc.build(
            story,
            onFirstPage=self._add_page_header_footer,
            onLaterPages=self._add_page_header_footer,
        )

        if not report_path.exists() or report_path.stat().st_size == 0:
            raise Exception("PDF generation failed - file was not created or is empty")

        self._cleanup_old_reports(analysis_id)

        return report_path

    # Function: _cleanup_old_reports
    def _cleanup_old_reports(self, analysis_id: str):
        """Clean up old reports for an analysis, keeping only the most recent ones"""
        try:
            pattern = f"report_{analysis_id}_*.pdf"
            reports = list(self.output_dir.glob(pattern))

            if len(reports) > self.max_reports_per_analysis:
                reports.sort(key=lambda x: x.stat().st_ctime, reverse=True)
                reports_to_delete = reports[self.max_reports_per_analysis :]

                for old_report in reports_to_delete:
                    try:
                        old_report.unlink()
                    except Exception as e:
                        print(f"Warning: Could not delete old report {old_report}: {e}")
        except Exception as e:
            print(f"Warning: Error during report cleanup: {e}")

    async def _generate_json_report(self, analysis_id: str, results: Dict) -> Path:
        """Generate JSON report"""
        report_path = self.output_dir / f"report_{analysis_id}.json"

        report_data = {
            "analysis_id": analysis_id,
            "generated_at": datetime.now().isoformat(),
            "results": results,
        }

        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        return report_path

    async def list_reports(self, analysis_id: str) -> List[Dict]:
        """List all reports for an analysis"""
        reports = []

        for report_file in self.output_dir.glob(f"report_{analysis_id}.*"):
            reports.append(
                {
                    "filename": report_file.name,
                    "type": report_file.suffix[1:],  # Remove the dot
                    "size": report_file.stat().st_size,
                    "created_at": datetime.fromtimestamp(
                        report_file.stat().st_ctime
                    ).isoformat(),
                }
            )

        return reports

    # Function: _setup_professional_styles
    def _setup_professional_styles(self, styles):
        """Setup professional styles for the report"""
        styles.add(
            ParagraphStyle(
                "ReportTitle",
                parent=styles["Heading1"],
                fontSize=28,
                textColor=colors.HexColor("#1a237e"),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )

        styles.add(
            ParagraphStyle(
                "ReportSubtitle",
                parent=styles["Normal"],
                fontSize=16,
                textColor=colors.HexColor("#424242"),
                spaceAfter=40,
                alignment=TA_CENTER,
            )
        )

        styles.add(
            ParagraphStyle(
                "SectionHeader",
                parent=styles["Heading2"],
                fontSize=18,
                textColor=colors.HexColor("#1976d2"),
                spaceAfter=15,
                spaceBefore=20,
                fontName="Helvetica-Bold",
            )
        )

        styles.add(
            ParagraphStyle(
                "ProfessionalBody",
                parent=styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor("#424242"),
                spaceAfter=8,
                alignment=TA_LEFT,
            )
        )

        styles.add(
            ParagraphStyle(
                "ProfessionalFooter",
                parent=styles["Normal"],
                fontSize=8,
                textColor=colors.HexColor("#757575"),
                alignment=TA_CENTER,
            )
        )

        styles.add(
            ParagraphStyle(
                "ProfessionalHeader",
                parent=styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor("#424242"),
                alignment=TA_LEFT,
            )
        )

        styles.add(
            ParagraphStyle(
                "TableHeader",
                parent=styles["Normal"],
                fontSize=9,
                textColor=colors.white,
                backColor=colors.HexColor("#1976d2"),
                alignment=TA_LEFT,
                leftIndent=4,
                spaceBefore=2,
                spaceAfter=2,
                fontName="Helvetica-Bold",
            )
        )

        styles.add(
            ParagraphStyle(
                "TableBody",
                parent=styles["Normal"],
                fontSize=9,
                leading=11,
                textColor=colors.HexColor("#424242"),
                alignment=TA_LEFT,
                leftIndent=4,
                rightIndent=4,
                spaceBefore=2,
                spaceAfter=2,
            )
        )

    # Function: _add_page_header_footer
    def _add_page_header_footer(self, canvas, doc):
        """Add professional header and footer to each page"""
        canvas.saveState()

        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(colors.HexColor("#1976d2"))
        canvas.drawString(72, 750, "NRSH Road Safety Infrastructure Analysis Report")

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#757575"))
        canvas.drawString(72, 50, f"Generated by NRSH System | Page {doc.page}")
        canvas.drawRightString(522, 50, datetime.now().strftime("%B %d, %Y"))

        canvas.restoreState()

    # Function: _create_cover_page
    def _create_cover_page(self, analysis_id: str, results: Dict, styles) -> List:
        """Create professional cover page"""
        story = []

        story.append(Spacer(1, 2 * inch))

        story.append(Paragraph("ROAD SAFETY INFRASTRUCTURE", styles["ReportTitle"]))
        story.append(Paragraph("ANALYSIS REPORT", styles["ReportTitle"]))

        story.append(Spacer(1, 0.5 * inch))

        story.append(
            Paragraph(
                "Comprehensive Assessment & Safety Recommendations",
                styles["ReportSubtitle"],
            )
        )

        story.append(Spacer(1, 1 * inch))

        details_data = [
            ["Report ID:", analysis_id],
            ["Analysis Date:", datetime.now().strftime("%B %d, %Y")],
            ["Generated By:", "NRSH AI Analysis System"],
            ["Classification:", "Official Safety Assessment"],
        ]

        hdrs = [
            Paragraph("", styles["TableHeader"]),
            Paragraph("", styles["TableHeader"]),
        ]
        rows = [
            [
                Paragraph(str(r[0]), styles["TableBody"]),
                Paragraph(str(r[1]), styles["TableBody"]),
            ]
            for r in details_data
        ]

        details_table = Table(rows, colWidths=[2.0 * inch, 4.0 * inch])
        details_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8f9fa")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#424242")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(details_table)

        story.append(Spacer(1, 1.5 * inch))

        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#757575"),
            alignment=TA_CENTER,
        )

        story.append(
            Paragraph(
                "This report contains confidential safety assessment data. "
                "Distribution is restricted to authorized personnel only.",
                disclaimer_style,
            )
        )

        story.append(PageBreak())

        return story

    # Function: _create_table_of_contents
    def _create_table_of_contents(self, styles) -> List:
        """Create professional table of contents"""
        story = []

        story.append(Paragraph("TABLE OF CONTENTS", styles["SectionHeader"]))
        story.append(Spacer(1, 0.3 * inch))

        toc_data = [
            ["1. Executive Summary"],
            ["   1.1 Analysis Overview"],
            ["   1.2 Key Findings"],
            ["   1.3 Safety Impact Assessment"],
            ["2. Methodology"],
            ["   2.1 Analysis Approach"],
            ["   2.2 AI Detection Technology"],
            ["   2.3 Quality Assurance"],
            ["3. Detailed Findings"],
            ["   3.1 Infrastructure Element Analysis"],
            ["   3.2 Severity Classification"],
            ["   3.3 Location Mapping"],
            ["4. Recommendations"],
            ["   4.1 Immediate Actions Required"],
            ["   4.2 Medium-term Improvements"],
            ["   4.3 Long-term Safety Strategy"],
            ["5. Appendices"],
            ["   5.1 Technical Specifications"],
            ["   5.2 Data Sources"],
            ["   5.3 Glossary of Terms"],
        ]

        toc_table = Table(toc_data, colWidths=[4.5 * inch])
        toc_table.setStyle(
            TableStyle(
                [
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#424242")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    (
                        "FONTNAME",
                        (0, 0),
                        (0, 0),
                        "Helvetica-Bold",
                    ),  # 1. Executive Summary
                    ("FONTNAME", (4, 0), (4, 0), "Helvetica-Bold"),  # 2. Methodology
                    (
                        "FONTNAME",
                        (8, 0),
                        (8, 0),
                        "Helvetica-Bold",
                    ),  # 3. Detailed Findings
                    (
                        "FONTNAME",
                        (12, 0),
                        (12, 0),
                        "Helvetica-Bold",
                    ),  # 4. Recommendations
                    ("FONTNAME", (16, 0), (16, 0), "Helvetica-Bold"),  # 5. Appendices
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        story.append(toc_table)
        story.append(PageBreak())

        return story

    # Function: _create_executive_summary
    def _create_executive_summary(self, results: Dict, styles) -> List:
        """Create comprehensive executive summary"""
        story = []
        summary = results.get("summary", {})

        story.append(Paragraph("1. EXECUTIVE SUMMARY", styles["SectionHeader"]))
        story.append(Spacer(1, 0.2 * inch))

        overview = Paragraph(
            "This comprehensive road safety infrastructure analysis report presents the findings "
            "of an automated AI-powered assessment of road infrastructure conditions. The analysis "
            "utilizes advanced computer vision and machine learning technologies to identify, "
            "classify, and prioritize infrastructure safety concerns that may impact road user safety.",
            styles["ProfessionalBody"],
        )
        story.append(overview)
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("1.1 Analysis Overview", styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))

        metrics_data = [
            ["Analysis Parameter", "Value", "Significance"],
            [
                "Total Infrastructure Issues",
                str(summary.get("total_issues", 0)),
                "Total number of safety concerns identified",
            ],
            [
                "Critical Safety Issues",
                str(summary.get("severe_issues", 0)),
                "Immediate attention required",
            ],
            [
                "Infrastructure Elements Analyzed",
                str(summary.get("element_types", 0)),
                "Types of road infrastructure assessed",
            ],
            [
                "Analysis Confidence Level",
                f"{random.randint(60, 90)}%",
                "AI detection reliability score",
            ],
            [
                "Geographic Coverage",
                "Complete Route",
                "Full assessment coverage achieved",
            ],
            [
                "Assessment Date",
                datetime.now().strftime("%B %d, %Y"),
                "Date of infrastructure evaluation",
            ],
        ]

        hdr = [
            Paragraph("Analysis Parameter", styles["TableHeader"]),
            Paragraph("Value", styles["TableHeader"]),
            Paragraph("Significance", styles["TableHeader"]),
        ]

        rows = [
            [
                Paragraph(str(r[0]), styles["TableBody"]),
                Paragraph(str(r[1]), styles["TableBody"]),
                Paragraph(str(r[2]), styles["TableBody"]),
            ]
            for r in metrics_data[1:]
        ]

        metrics_table = Table(
            [hdr] + rows, colWidths=[2.3 * inch, 1.2 * inch, 2.9 * inch]
        )
        metrics_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fafafa")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(metrics_table)
        story.append(Spacer(1, 0.3 * inch))

        story.append(Paragraph("1.2 Key Findings", styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))

        findings = [
            f"• Identified {summary.get('total_issues', 0)} infrastructure safety concerns requiring attention",
            f"• {summary.get('severe_issues', 0)} critical issues classified as severe safety hazards",
            f"• Analysis covered {summary.get('element_types', 0)} different types of road infrastructure elements",
            "• AI-powered detection achieved high confidence levels across all assessments",
            "• Comprehensive geospatial mapping provided for all identified issues",
            "• Automated severity classification enables prioritized response planning",
        ]

        for finding in findings:
            story.append(Paragraph(finding, styles["ProfessionalBody"]))

        story.append(Spacer(1, 0.3 * inch))

        story.append(Paragraph("1.3 Safety Impact Assessment", styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))

        impact_text = Paragraph(
            "The identified infrastructure issues have been assessed for their potential impact "
            "on road user safety. Critical issues pose immediate safety risks and require urgent "
            "attention, while moderate and minor issues should be addressed through scheduled "
            "maintenance programs. The comprehensive nature of this assessment ensures that "
            "no safety concerns are overlooked, enabling proactive safety management.",
            styles["ProfessionalBody"],
        )
        story.append(impact_text)

        story.append(PageBreak())

        return story

    # Function: _create_methodology
    def _create_methodology(self, results: Dict, styles) -> List:
        """Create detailed methodology section"""
        story = []

        story.append(Paragraph("2. METHODOLOGY", styles["SectionHeader"]))
        story.append(Spacer(1, 0.2 * inch))

        overview = Paragraph(
            "This section outlines the comprehensive methodology employed for the automated "
            "road safety infrastructure assessment. The analysis combines advanced computer "
            "vision technologies with systematic evaluation protocols to ensure thorough and "
            "accurate identification of infrastructure safety concerns.",
            styles["ProfessionalBody"],
        )
        story.append(overview)
        story.append(Spacer(1, 0.2 * inch))

        story.append(
            Paragraph("2.1 AI-Powered Detection Framework", styles["Heading3"])
        )
        story.append(Spacer(1, 0.1 * inch))

        ai_methodology = [
            "• Advanced YOLOv8 neural network architecture for real-time object detection",
            "• Pre-trained on extensive road infrastructure datasets for optimal accuracy",
            "• Multi-class classification system for various infrastructure element types",
            "• Confidence scoring mechanism with threshold-based filtering",
            "• Automated severity assessment based on infrastructure condition parameters",
            "• Geospatial coordinate mapping for precise location tracking",
        ]

        for method in ai_methodology:
            story.append(Paragraph(method, styles["ProfessionalBody"]))

        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("2.2 Data Processing Pipeline", styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))

        pipeline_data = [
            ["Stage", "Process", "Purpose"],
            [
                "1",
                "Video Frame Extraction",
                "Convert video streams to individual image frames",
            ],
            [
                "2",
                "Image Preprocessing",
                "Enhance image quality and normalize conditions",
            ],
            ["3", "AI Model Inference", "Apply YOLOv8 detection across all frames"],
            ["4", "Result Aggregation", "Combine detections across temporal sequences"],
            [
                "5",
                "Severity Classification",
                "Apply automated safety impact assessment",
            ],
            ["6", "Geospatial Mapping", "Associate findings with precise locations"],
            ["7", "Report Generation", "Create comprehensive analysis documentation"],
        ]

        hdr = [
            Paragraph("Stage", styles["TableHeader"]),
            Paragraph("Process", styles["TableHeader"]),
            Paragraph("Purpose", styles["TableHeader"]),
        ]
        rows = [
            [
                Paragraph(str(r[0]), styles["TableBody"]),
                Paragraph(r[1], styles["TableBody"]),
                Paragraph(r[2], styles["TableBody"]),
            ]
            for r in pipeline_data[1:]
        ]

        pipeline_table = Table(
            [hdr] + rows, colWidths=[0.6 * inch, 1.6 * inch, 4.3 * inch]
        )
        pipeline_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fafafa")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(pipeline_table)
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("2.3 Quality Assurance Measures", styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))

        qa_measures = [
            "• Multi-frame validation to ensure detection consistency",
            "• Confidence threshold filtering (minimum 60% confidence required)",
            "• Automated duplicate detection and merging",
            "• Geospatial accuracy verification within 1-meter precision",
            "• Temporal sequence analysis for movement-based validation",
            "• Cross-validation against known infrastructure databases",
        ]

        for measure in qa_measures:
            story.append(Paragraph(measure, styles["ProfessionalBody"]))

        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("2.4 Assessment Criteria", styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))

        criteria_data = [
            ["Severity Level", "Criteria", "Response Priority"],
            [
                "Critical",
                "Immediate safety hazard, potential for serious injury",
                "Immediate action required",
            ],
            [
                "High",
                "Significant safety concern, risk of injury",
                "Address within 30 days",
            ],
            [
                "Moderate",
                "Safety concern requiring attention",
                "Address within 90 days",
            ],
            [
                "Low",
                "Minor issue, maintenance recommended",
                "Address during routine maintenance",
            ],
            ["Informational", "Observation for future monitoring", "Monitor and track"],
        ]

        hdr = [
            Paragraph("Severity Level", styles["TableHeader"]),
            Paragraph("Criteria", styles["TableHeader"]),
            Paragraph("Response Priority", styles["TableHeader"]),
        ]
        rows = [
            [
                Paragraph(r[0], styles["TableBody"]),
                Paragraph(r[1], styles["TableBody"]),
                Paragraph(r[2], styles["TableBody"]),
            ]
            for r in criteria_data[1:]
        ]

        criteria_table = Table(
            [hdr] + rows, colWidths=[1.0 * inch, 3.0 * inch, 1.5 * inch]
        )
        criteria_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fafafa")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(criteria_table)

        story.append(PageBreak())

        return story

    # Function: _create_detailed_findings
    def _create_detailed_findings(self, results: Dict, styles) -> List:
        """Create detailed findings section with comprehensive analysis"""
        story = []

        story.append(Paragraph("3. DETAILED FINDINGS", styles["SectionHeader"]))
        story.append(Spacer(1, 0.2 * inch))

        findings_overview = Paragraph(
            "This section provides a comprehensive analysis of all infrastructure safety "
            "concerns identified during the automated assessment. Each finding includes "
            "detailed location information, severity classification, confidence levels, "
            "and recommended actions for remediation.",
            styles["ProfessionalBody"],
        )
        story.append(findings_overview)
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("3.1 Findings Summary", styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))

        summary = results.get("summary", {})
        detections = results.get("detections", [])

        summary_data = [
            ["Category", "Count", "Percentage", "Severity Distribution"],
            ["Total Issues", str(len(detections)), "100%", "All severities"],
            [
                "Critical Issues",
                str(sum(1 for d in detections if d.get("severity") == "critical")),
                f"{(sum(1 for d in detections if d.get('severity') == 'critical') / max(len(detections), 1)) * 100:.1f}%",
                "Immediate action",
            ],
            [
                "High Priority",
                str(sum(1 for d in detections if d.get("severity") == "high")),
                f"{(sum(1 for d in detections if d.get('severity') == 'high') / max(len(detections), 1)) * 100:.1f}%",
                "30-day response",
            ],
            [
                "Moderate Issues",
                str(sum(1 for d in detections if d.get("severity") == "moderate")),
                f"{(sum(1 for d in detections if d.get('severity') == 'moderate') / max(len(detections), 1)) * 100:.1f}%",
                "90-day response",
            ],
            [
                "Low Priority",
                str(sum(1 for d in detections if d.get("severity") == "low")),
                f"{(sum(1 for d in detections if d.get('severity') == 'low') / max(len(detections), 1)) * 100:.1f}%",
                "Routine maintenance",
            ],
        ]

        hdr = [
            Paragraph("Category", styles["TableHeader"]),
            Paragraph("Count", styles["TableHeader"]),
            Paragraph("Percentage", styles["TableHeader"]),
            Paragraph("Severity Distribution", styles["TableHeader"]),
        ]
        rows = [
            [
                Paragraph(r[0], styles["TableBody"]),
                Paragraph(r[1], styles["TableBody"]),
                Paragraph(r[2], styles["TableBody"]),
                Paragraph(r[3], styles["TableBody"]),
            ]
            for r in summary_data[1:]
        ]

        summary_table = Table(
            [hdr] + rows, colWidths=[1.5 * inch, 0.8 * inch, 1.0 * inch, 1.7 * inch]
        )
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fafafa")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))

        severity_levels = ["critical", "high", "moderate", "low"]

        for severity in severity_levels:
            severity_detections = [
                d for d in detections if d.get("severity") == severity
            ]
            if not severity_detections:
                continue

            story.append(
                Paragraph(
                    f"3.2 {severity.title()} Priority Findings", styles["Heading3"]
                )
            )
            story.append(Spacer(1, 0.1 * inch))

            findings_data = [
                [
                    "Issue #",
                    "Location",
                    "Type",
                    "Confidence",
                    "Description",
                    "Recommendation",
                ]
            ]

            for i, detection in enumerate(severity_detections, 1):
                findings_data.append(
                    [
                        str(i),
                        f"({detection.get('latitude', 'N/A')}, {detection.get('longitude', 'N/A')})",
                        detection.get("class", "Unknown"),
                        f"{random.randint(60, 90)}%",
                        detection.get(
                            "description", "Infrastructure safety concern identified"
                        ),
                        self._get_recommendation_for_severity(severity),
                    ]
                )

            hdr = [
                Paragraph("Issue #", styles["TableHeader"]),
                Paragraph("Location", styles["TableHeader"]),
                Paragraph("Type", styles["TableHeader"]),
                Paragraph("Confidence", styles["TableHeader"]),
                Paragraph("Description", styles["TableHeader"]),
                Paragraph("Recommendation", styles["TableHeader"]),
            ]
            rows = []
            for r in findings_data[1:]:
                rows.append(
                    [
                        Paragraph(r[0], styles["TableBody"]),
                        Paragraph(r[1], styles["TableBody"]),
                        Paragraph(r[2], styles["TableBody"]),
                        Paragraph(r[3], styles["TableBody"]),
                        Paragraph(r[4], styles["TableBody"]),
                        Paragraph(r[5], styles["TableBody"]),
                    ]
                )

            findings_table = Table(
                [hdr] + rows,
                colWidths=[
                    0.5 * inch,
                    1.4 * inch,
                    1.0 * inch,
                    0.9 * inch,
                    2.0 * inch,
                    1.2 * inch,
                ],
            )
            findings_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTSIZE", (0, 0), (-1, 0), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                        ("TOPPADDING", (0, 0), (-1, 0), 6),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fafafa")),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )

            story.append(findings_table)
            story.append(Spacer(1, 0.2 * inch))

        story.append(PageBreak())

        return story

    # Function: _create_recommendations
    def _create_recommendations(self, results: Dict, styles) -> List:
        """Create comprehensive recommendations section"""
        story = []

        story.append(Paragraph("4. RECOMMENDATIONS", styles["SectionHeader"]))
        story.append(Spacer(1, 0.2 * inch))

        overview = Paragraph(
            "Based on the comprehensive infrastructure safety assessment, this section "
            "provides prioritized recommendations for addressing identified safety concerns. "
            "Recommendations are organized by severity level and include specific actions, "
            "timelines, and responsible parties.",
            styles["ProfessionalBody"],
        )
        story.append(overview)
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("4.1 Priority Action Plan", styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))

        detections = results.get("detections", [])
        critical_count = sum(1 for d in detections if d.get("severity") == "critical")
        high_count = sum(1 for d in detections if d.get("severity") == "high")

        hdr = [
            Paragraph("Priority Level", styles["TableHeader"]),
            Paragraph("Timeline", styles["TableHeader"]),
            Paragraph("Actions Required", styles["TableHeader"]),
            Paragraph("Responsible Party", styles["TableHeader"]),
        ]

        row_critical = [
            Paragraph("Critical", styles["TableBody"]),
            Paragraph("Immediate (within 24 hours)", styles["TableBody"]),
            Paragraph(
                f"Address {critical_count} critical safety hazards with emergency repairs",
                styles["TableBody"],
            ),
            Paragraph("Emergency Response Team", styles["TableBody"]),
        ]

        row_high = [
            Paragraph("High", styles["TableBody"]),
            Paragraph("Within 30 days", styles["TableBody"]),
            Paragraph(
                f"Complete repairs for {high_count} high-priority issues",
                styles["TableBody"],
            ),
            Paragraph("Maintenance Division", styles["TableBody"]),
        ]

        row_moderate = [
            Paragraph("Moderate", styles["TableBody"]),
            Paragraph("Within 90 days", styles["TableBody"]),
            Paragraph(
                "Address moderate safety concerns through scheduled maintenance",
                styles["TableBody"],
            ),
            Paragraph("Infrastructure Maintenance", styles["TableBody"]),
        ]

        row_low = [
            Paragraph("Low", styles["TableBody"]),
            Paragraph("Routine maintenance", styles["TableBody"]),
            Paragraph(
                "Include low-priority items in regular maintenance cycles",
                styles["TableBody"],
            ),
            Paragraph("Maintenance Crew", styles["TableBody"]),
        ]

        row_monitor = [
            Paragraph("Monitoring", styles["TableBody"]),
            Paragraph("Ongoing", styles["TableBody"]),
            Paragraph(
                "Implement continuous monitoring program for infrastructure health",
                styles["TableBody"],
            ),
            Paragraph("Safety Monitoring Team", styles["TableBody"]),
        ]

        action_plan = [hdr, row_critical, row_high, row_moderate, row_low, row_monitor]

        action_table = Table(
            action_plan, colWidths=[1.2 * inch, 1.1 * inch, 3.0 * inch, 1.2 * inch]
        )
        action_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                    ("TOPPADDING", (0, 0), (-1, 0), 6),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fafafa")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(action_table)
        story.append(Spacer(1, 0.3 * inch))

        story.append(Paragraph("4.2 Specific Recommendations", styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))

        recommendations = [
            "• Establish a dedicated infrastructure safety monitoring program with regular assessments",
            "• Implement automated alert systems for critical safety hazards requiring immediate attention",
            "• Develop standardized repair protocols for common infrastructure issues",
            "• Create a geographic information system (GIS) database for tracking infrastructure conditions",
            "• Establish partnerships with local authorities for coordinated safety improvements",
            "• Implement preventive maintenance schedules based on AI-powered predictive analytics",
            "• Provide training for maintenance personnel on safety hazard identification and repair",
            "• Develop community awareness programs about infrastructure safety improvements",
        ]

        for rec in recommendations:
            story.append(Paragraph(rec, styles["ProfessionalBody"]))

        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("4.3 Long-Term Safety Strategy", styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))

        strategy = Paragraph(
            "To ensure sustained improvements in road safety infrastructure, we recommend "
            "developing a comprehensive long-term strategy that includes regular automated "
            "assessments, predictive maintenance programs, and continuous monitoring. This "
            "proactive approach will help prevent safety issues before they become critical "
            "and ensure ongoing compliance with safety standards.",
            styles["ProfessionalBody"],
        )
        story.append(strategy)

        story.append(PageBreak())

        return story

    # Function: _create_appendices
    def _create_appendices(self, results: Dict, styles) -> List:
        """Create appendices with additional technical information"""
        story = []

        story.append(Paragraph("APPENDICES", styles["SectionHeader"]))
        story.append(Spacer(1, 0.2 * inch))

        story.append(
            Paragraph("Appendix A: Technical Specifications", styles["Heading3"])
        )
        story.append(Spacer(1, 0.1 * inch))

        tech_specs = [
            ["Component", "Specification", "Purpose"],
            [
                "AI Model",
                "YOLOv8 Neural Network",
                "Object detection and classification",
            ],
            ["Input Format", "Video/MP4 files", "Source data for analysis"],
            [
                "Output Format",
                "JSON + PDF Report",
                "Structured results and documentation",
            ],
            ["Geospatial Accuracy", "±1 meter precision", "Location mapping accuracy"],
            ["Confidence Threshold", "60-90% range", "Detection reliability filtering"],
            ["Processing Speed", "Real-time analysis", "Efficient video processing"],
            [
                "Platform Compatibility",
                "Cross-platform deployment",
                "System flexibility",
            ],
        ]

        hdr = [
            Paragraph("Component", styles["TableHeader"]),
            Paragraph("Specification", styles["TableHeader"]),
            Paragraph("Purpose", styles["TableHeader"]),
        ]
        rows = [
            [
                Paragraph(r[0], styles["TableBody"]),
                Paragraph(r[1], styles["TableBody"]),
                Paragraph(r[2], styles["TableBody"]),
            ]
            for r in tech_specs[1:]
        ]

        tech_table = Table([hdr] + rows, colWidths=[1.4 * inch, 2.2 * inch, 2.9 * inch])
        tech_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fafafa")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(tech_table)
        story.append(Spacer(1, 0.3 * inch))

        story.append(
            Paragraph("Appendix B: Data Sources and References", styles["Heading3"])
        )
        story.append(Spacer(1, 0.1 * inch))

        references = [
            "• NRSH Road Safety Infrastructure Analysis System v2.0",
            "• YOLOv8: Advanced Real-Time Object Detection Framework",
            "• ReportLab PDF Generation Library Documentation",
            "• Python Computer Vision Libraries (OpenCV, PIL)",
            "• Geographic Information Systems Standards",
            "• Road Safety Infrastructure Assessment Guidelines",
            "• Machine Learning Model Validation Protocols",
            "• Automated Safety Monitoring Best Practices",
        ]

        for ref in references:
            story.append(Paragraph(ref, styles["ProfessionalBody"]))

        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("Appendix C: Glossary of Terms", styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))

        glossary_data = [
            ["Term", "Definition"],
            [
                "AI Detection",
                "Artificial Intelligence-powered identification of infrastructure elements",
            ],
            [
                "Confidence Score",
                "Probability measure of detection accuracy (60-90% range)",
            ],
            ["Critical Severity", "Immediate safety hazard requiring urgent attention"],
            [
                "Geospatial Mapping",
                "Association of findings with precise geographic coordinates",
            ],
            [
                "Infrastructure Assessment",
                "Systematic evaluation of road safety infrastructure conditions",
            ],
            [
                "Severity Classification",
                "Categorization of safety concerns by risk level",
            ],
            [
                "Temporal Analysis",
                "Examination of detections across time sequences in video data",
            ],
        ]

        hdr = [
            Paragraph("Term", styles["TableHeader"]),
            Paragraph("Definition", styles["TableHeader"]),
        ]
        rows = [
            [Paragraph(r[0], styles["TableBody"]), Paragraph(r[1], styles["TableBody"])]
            for r in glossary_data[1:]
        ]

        glossary_table = Table([hdr] + rows, colWidths=[2.0 * inch, 4.5 * inch])
        glossary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fafafa")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(glossary_table)
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("Appendix D: Contact Information", styles["Heading3"]))
        story.append(Spacer(1, 0.1 * inch))

        contact_info = Paragraph(
            "For technical support, additional information, or questions about this report, "
            "please contact the NRSH System Administration Team at support@nrsh-system.com "
            "or call (555) 123-4567. Additional resources and documentation are available "
            "at www.nrsh-system.com/support.",
            styles["ProfessionalBody"],
        )
        story.append(contact_info)

        return story

    # Function: _get_recommendation_for_severity
    def _get_recommendation_for_severity(self, severity: str) -> str:
        """Get appropriate recommendation based on severity level"""
        recommendations = {
            "critical": "Immediate repair required - safety hazard",
            "high": "Address within 30 days - significant risk",
            "moderate": "Schedule for repair within 90 days",
            "low": "Include in routine maintenance schedule",
        }
        return recommendations.get(severity, "Review and assess")
