# Software Document Code

This folder contains copies of all code files used in the Road Safety Infrastructure Analysis System project.

## Contents

### Backend Code (`backend/`)
- **main.py**: FastAPI application entry point
- **api/routes/**: API endpoint definitions (video, analysis, dashboard, reports)
- **services/**: Business logic services (video, analysis, dashboard, report, database, config)
- **models/**: Database models and schemas (Supabase integration)

### AI/ML Models (`ai_models/`)
- **detection/**: Object detection using YOLOv8
- **change_detection/**: Change detection algorithms

### Data Processing (`data_processing/`)
- **frame_extraction.py**: Video frame extraction
- **alignment.py**: Frame alignment using GPS and temporal data
- **preprocessing.py**: Image preprocessing utilities

### Frontend Code (`frontend/`)
- **pages/**: Next.js pages
- **components/**: React components (VideoUpload, AnalysisDashboard, MapVisualization)
- **styles/**: CSS styles
- Configuration files (next.config.js, tailwind.config.js, etc.)

### Configuration Files
- **config/config.yaml**: Application configuration
- **database/schema.sql**: Supabase database schema
- **requirements.txt**: Python dependencies
- **frontend/package.json**: Node.js dependencies

### Scripts (`scripts/`)
- **download_models.py**: Download AI models
- **download_sample_videos.py**: Download sample videos
- **test_database.py**: Test Supabase connection

## Purpose

This folder serves as a code repository/documentation for:
- Code review and documentation
- Reference for development
- Submission requirements
- Backup of all source code

## Note

These are copies of the original code files. For the latest versions, refer to the main project directories.

## File Structure

```
SoftwareDocumentCode/
├── backend/
│   ├── main.py
│   ├── api/
│   ├── services/
│   └── models/
├── ai_models/
│   ├── detection/
│   └── change_detection/
├── data_processing/
├── frontend/
│   ├── pages/
│   ├── components/
│   └── styles/
├── config/
├── database/
└── scripts/
```

## Last Updated

All files copied on: 2025-11-29

