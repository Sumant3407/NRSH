# Road Safety Infrastructure Analysis System
## National Road Safety Hackathon 2025

An AI-powered system for comparative analysis of road infrastructure elements using computer vision and deep learning.

## 🎯 Features

- **AI-Based Video Analysis**: Compare base vs present road videos to detect deterioration
- **Multi-Element Detection**: Identify pavement condition, road markings, road studs, signs, roadside furniture, and VRU paths
- **Geospatial Visualization**: Map-based dashboard with GPS-tagged detections
- **Automated Reporting**: Generate PDF reports with before-after comparisons
- **Real-time Processing**: Fast API backend for video processing and inference
- **Interactive Dashboard**: Web interface for playback, analysis, and validation

## 🏗️ System Architecture

```
┌─────────────────┐
│  Input Videos   │ (Base + Present)
│  + Metadata     │ (GPS, Timestamps)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Pipeline  │ (Frame Extraction, Alignment)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Processing  │ (YOLOv8, Change Detection)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Aggregation    │ (GPS Segmentation, Scoring)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Visualization  │ (Dashboard, Maps, Reports)
└─────────────────┘
```

## 📁 Project Structure

```
RSH/
├── backend/              # FastAPI backend
│   ├── api/             # API routes
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   └── main.py          # FastAPI app entry
├── ai_models/           # AI model scripts
│   ├── detection/       # Object detection models
│   ├── change_detection/ # Change detection logic
│   └── training/        # Model training scripts
├── data_processing/     # Video processing pipeline
│   ├── frame_extraction.py
│   ├── alignment.py
│   └── preprocessing.py
├── frontend/            # React/Next.js dashboard
│   ├── components/
│   ├── pages/
│   └── public/
├── config/              # Configuration files
├── requirements.txt     # Python dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- CUDA-capable GPU (optional, for faster inference)

### Installation

1. **Clone and setup Python environment:**
```bash
cd RSH
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Setup frontend:**
```bash
cd frontend
npm install
```

3. **Download AI models:**
```bash
python scripts/download_models.py
```

### Running the Application

1. **Start backend server:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

2. **Start frontend:**
```bash
cd frontend
npm run dev
```

3. **Access dashboard:**
Open http://localhost:3000 in your browser

## 🔧 Configuration

Edit `config/config.yaml` to customize:
- Model paths
- Detection thresholds
- GPS coordinate systems
- Report templates

## 📊 Usage

### Upload Videos

1. Upload base (reference) video
2. Upload present (current) video
3. Provide GPS metadata (optional, can be extracted from video)

### Run Analysis

1. Select road segments to analyze
2. Click "Run Analysis"
3. View results in dashboard:
   - Map visualization with detected issues
   - Before-and-after comparison frames
   - Severity scores and trends

### Generate Reports

1. Select analysis results
2. Click "Generate Report"
3. Download PDF with:
   - Summary statistics
   - Issue heatmaps
   - Detailed findings

## 🎓 Technical Details

### AI Models

- **Object Detection**: YOLOv8 (custom trained on road infrastructure)
- **Segmentation**: DeepLabV3+ for pixel-level analysis
- **Change Detection**: Siamese network for temporal comparison

### Detection Elements

1. **Pavement Condition**: Cracks, potholes, surface degradation
2. **Road Markings**: Faded lines, missing markings
3. **Road Studs**: Missing or damaged reflectors
4. **Signs**: Damaged, missing, or obscured signs
5. **Roadside Furniture**: Barriers, guardrails, lighting
6. **VRU Paths**: Pedestrian crossings, bike lanes

### Evaluation Metrics

- **Detection Accuracy**: mAP@0.5 for object detection
- **Classification Accuracy**: F1-score for deterioration classification
- **Geospatial Precision**: GPS alignment accuracy
- **Processing Speed**: FPS for video analysis

## 🏆 Innovation Highlights

1. **Temporal Comparison**: AI-driven before-after analysis
2. **Geospatial Intelligence**: GPS-tagged detections with map visualization
3. **Automated Scoring**: Severity-based issue prioritization
4. **Auditor Feedback Loop**: Validation mechanism for continuous improvement
5. **Real-time Processing**: Optimized pipeline for quick insights

## 📝 API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

This is a hackathon project. For improvements:
1. Fork the repository
2. Create a feature branch
3. Submit pull request

## 📄 License

MIT License - Hackathon Project

## 👥 Team

National Road Safety Hackathon 2025 Team:<br>

Team Name: CHIKKUZ<br>

Members:<br>
1. Ananya Rai
2. Sumant Kumar Giri
