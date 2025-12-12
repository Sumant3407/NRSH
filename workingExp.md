# Working Experience - Road Safety Infrastructure Analysis System

## Project Overview

The **Road Safety Infrastructure Analysis System** is an AI-powered platform designed for comparative analysis of road infrastructure elements using computer vision and deep learning. The system compares base (reference) and present (current) road videos to detect deterioration, damage, and changes in road infrastructure.

## System Architecture

### 1. **Backend Architecture (FastAPI)**

The backend is built using FastAPI and follows a modular service-oriented architecture:

#### Core Components:

- **API Routes** (`backend/api/routes/`):
  - `video.py`: Handles video upload, retrieval, and management
  - `analysis.py`: Manages analysis job creation and status tracking
  - `reports.py`: Generates PDF reports from analysis results
  - `dashboard.py`: Provides dashboard data and visualizations

- **Services** (`backend/services/`):
  - `video_service.py`: Manages video storage and metadata
  - `analysis_service.py`: Orchestrates the AI analysis pipeline
  - `report_service.py`: Generates comprehensive PDF reports
  - `dashboard_service.py`: Aggregates data for dashboard visualization
  - `config_manager.py`: Centralized configuration management

#### Main Application (`backend/main.py`):

- FastAPI application with CORS middleware
- Modular router inclusion for clean API structure
- Health check endpoints
- Configuration-based initialization

### 2. **AI/ML Pipeline**

#### Detection System (`ai_models/detection/detector.py`):

- **YOLOv8 Model**: Uses Ultralytics YOLOv8 for object detection
- **Detection Elements**:
  - Pavement cracks and potholes
  - Faded road markings
  - Missing road studs
  - Damaged signs
  - Roadside furniture damage
  - VRU (Vulnerable Road User) path obstructions
- **Severity Classification**: Heuristic-based classification (minor, moderate, severe)
- **Confidence Thresholding**: Configurable confidence and IoU thresholds

#### Change Detection (`ai_models/change_detection/change_detector.py`):

- Compares detections between base and present videos
- Identifies temporal changes and deterioration
- Calculates severity scores for detected issues

### 3. **Data Processing Pipeline**

#### Frame Extraction (`data_processing/frame_extraction.py`):

- Extracts frames from video at configurable FPS
- Handles multiple video formats (MP4, AVI, MOV, MKV)
- Optimizes frame extraction for processing efficiency

#### Frame Alignment (`data_processing/alignment.py`):

- Aligns frames from base and present videos
- GPS-based alignment using metadata
- Temporal alignment for synchronized comparison
- Handles coordinate system transformations

#### Preprocessing (`data_processing/preprocessing.py`):

- Frame resizing and normalization
- Video stabilization
- Quality enhancement for better detection accuracy

### 4. **Analysis Workflow**

The analysis process follows these steps:

1. **Video Upload**:
   - User uploads base (reference) and present (current) videos
   - Optional GPS metadata can be attached
   - Videos are stored with unique IDs

2. **Frame Extraction** (10% progress):
   - Frames extracted from both videos at configured FPS
   - Maximum frame limit to prevent excessive processing

3. **Frame Alignment** (30% progress):
   - Frames aligned using GPS coordinates and timestamps
   - Creates matched pairs for comparison

4. **Object Detection** (50% progress):
   - YOLOv8 model processes each frame
   - Detects road infrastructure elements
   - Classifies severity of detected issues

5. **Change Detection** (50-80% progress):
   - Compares detections between base and present frames
   - Identifies new issues, deterioration, or improvements
   - Calculates change scores

6. **Result Aggregation** (80% progress):
   - Groups detections by road segments
   - Aggregates by element type and severity
   - Generates summary statistics

7. **Result Storage** (100% progress):
   - Saves results as JSON files
   - Updates status tracking
   - Makes results available for visualization

### 5. **Frontend Architecture (Next.js/React)**

#### Components:

- `VideoUpload.js`: Drag-and-drop video upload interface
- `AnalysisDashboard.js`: Real-time analysis status and results display
- `MapVisualization.js`: Interactive map with GPS-tagged detections

#### Features:

- Real-time progress tracking
- Interactive map visualization
- Before-after frame comparison
- Heatmap visualization of issues
- Report generation interface

### 6. **Geospatial Features**

- **GPS Tagging**: All detections are tagged with GPS coordinates
- **Map Visualization**: Interactive maps showing issue locations
- **Heatmap Generation**: Visual representation of issue density
- **Road Segment Analysis**: Aggregation by geographic segments
- **Coordinate System Support**: WGS84 (EPSG:4326) with configurable systems

### 7. **Reporting System**

- **PDF Report Generation**: Comprehensive reports with:
  - Summary statistics
  - Issue heatmaps
  - Before-after comparisons
  - Detailed findings per element type
  - Severity breakdowns
- **Configurable Templates**: Customizable report formats
- **Export Options**: Multiple output formats

## Technical Implementation Details

### Configuration Management

The system uses YAML-based configuration (`config/config.yaml`):
- Model parameters (confidence thresholds, input sizes)
- Detection class definitions with severity weights
- Video processing settings (FPS, frame limits)
- Geospatial settings (coordinate systems, map providers)
- API settings (CORS, upload limits)
- Storage paths

### Data Storage

- *Current Implementation** (File-based):
- Videos stored in `uploads/` directory
- Metadata stored in JSON files
- Analysis results in `processed/` directory
- Status tracking via JSON files

- *Supabase Integration** (New):
- Structured database for videos, analyses, and results
- Real-time subscriptions for status updates
- Efficient querying and filtering
- Scalable storage solution

### API Endpoints

#### Video Management:

- `POST /api/v1/video/upload`: Upload video files
- `GET /api/v1/video/{video_id}`: Get video information
- `GET /api/v1/video/list`: List all videos
- `DELETE /api/v1/video/{video_id}`: Delete video

#### Analysis:

- `POST /api/v1/analysis/run`: Start analysis job
- `GET /api/v1/analysis/{analysis_id}/status`: Get analysis status
- `GET /api/v1/analysis/{analysis_id}/results`: Get analysis results
- `GET /api/v1/analysis/{analysis_id}/detections`: Get all detections
- `GET /api/v1/analysis/{analysis_id}/heatmap`: Get heatmap data

#### Dashboard:

- `GET /api/v1/dashboard/summary`: Get dashboard summary
- `GET /api/v1/dashboard/stats`: Get statistics

#### Reports:

- `POST /api/v1/reports/generate`: Generate PDF report
- `GET /api/v1/reports/{report_id}`: Download report

## Key Features & Innovations

### 1. **Temporal Comparison**

- AI-driven before-after analysis
- Identifies deterioration over time
- Quantifies changes with severity scores

### 2. **Multi-Element Detection**

- Simultaneous detection of 6+ infrastructure elements
- Custom-trained or adapted models for road infrastructure
- Configurable detection thresholds

### 3. **Geospatial Intelligence**

- GPS-tagged detections
- Map-based visualization
- Road segment-based aggregation
- Spatial querying capabilities

### 4. **Automated Scoring**

- Severity-based issue prioritization
- Weighted scoring system
- Configurable severity thresholds

### 5. **Real-time Processing**

- Background task processing
- Progress tracking via status updates
- Asynchronous API design
- Optimized for performance

### 6. **Scalable Architecture**

- Modular service design
- Easy to extend with new detection types
- Configurable processing parameters
- Database-backed for production scale

### 7. **Single-Media Detection**

- Optional mode to run detection on a single image or video (no comparison); enable via the uploader toggle in the UI. Results are returned under a generated analysis ID and surfaced in the dashboard.

## Performance Optimizations

- **Batch Processing**: Configurable batch sizes for model inference
- **GPU Support**: CUDA acceleration for faster processing
- **Frame Sampling**: Configurable FPS to balance accuracy and speed
- **Caching**: Intermediate results cached for faster retrieval
- **Async Operations**: Non-blocking I/O for better throughput

## Technology Stack

### Backend:

- **FastAPI**: Modern, fast web framework
- **Python 3.9+**: Core language
- **YOLOv8 (Ultralytics)**: Object detection
- **OpenCV**: Computer vision operations
- **PyTorch**: Deep learning framework

### Frontend:

- **Next.js**: React framework
- **React**: UI library
- **Tailwind CSS**: Styling
- **Map Libraries**: Geospatial visualization

### Database:

- **Supabase**: PostgreSQL database with real-time capabilities
- **SQLAlchemy**: ORM for database operations

### Infrastructure:

- **Docker** (optional): Containerization
- **Cloud Storage**: Scalable file storage
- **CDN**: Content delivery for static assets

## Development Workflow

1. **Setup**:
   - Install Python dependencies
   - Setup Supabase project
   - Configure environment variables
   - Download AI models

2. **Development**:
   - Backend: `uvicorn backend.main:app --reload`
   - Frontend: `npm run dev`
   - Database migrations: `alembic upgrade head`

3. **Testing**:
   - Unit tests for services
   - Integration tests for API endpoints
   - Model validation tests

4. **Deployment**:
   - Environment configuration
   - Database migration
   - Model deployment
   - Static asset optimization

## Future Enhancements

1. **Custom Model Training**: Train YOLOv8 on road infrastructure dataset
2. **Real-time Video Streaming**: Process live video feeds
3. **Mobile App**: Native mobile application for field data collection
4. **Advanced Analytics**: Trend analysis, predictive maintenance
5. **Integration**: Connect with road maintenance management systems
6. **Multi-user Support**: User authentication and role-based access
7. **Audit Trail**: Complete history of analyses and changes

## Challenges & Solutions

### Challenge 1: Frame Alignment

- *Problem**: Aligning frames from different videos with varying GPS data
- *Solution**: Multi-criteria alignment using GPS coordinates, timestamps, and visual features

### Challenge 2: Processing Speed

- *Problem**: Large video files require significant processing time
- *Solution**: Frame sampling, batch processing, GPU acceleration, and background tasks

### Challenge 3: Detection Accuracy

- *Problem**: General-purpose models may not detect road-specific elements accurately
- *Solution**: Custom class mapping, fine-tuning, and severity classification heuristics

### Challenge 4: Scalability

- *Problem**: File-based storage doesn't scale well
- *Solution**: Supabase integration for structured, scalable data storage

## Conclusion

The Road Safety Infrastructure Analysis System demonstrates a comprehensive approach to automated road infrastructure monitoring. By combining computer vision, deep learning, and geospatial analysis, the system provides actionable insights for road maintenance and safety improvements. The modular architecture ensures maintainability and extensibility for future enhancements.

- --

- *Team**: CHIKKUZ
- *Members**: Ananya Rai, Sumant Kumar Giri
- *Project**: National Road Safety Hackathon 2025
