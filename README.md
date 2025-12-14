# Road Safety Infrastructure Analysis System

## National Road Safety Hackathon 2025

An AI-powered system for comparative analysis of road infrastructure elements using computer vision and deep learning.

## Features

- **AI-Based Video Analysis**: Compare base vs present road videos to detect deterioration
- **Single-Media Detection**: Run detection on a single image or video (no comparison) via UI toggle
- **Multi-Element Detection**: Identify pavement condition, road markings, road studs, signs, roadside furniture, and VRU paths
- **Geospatial Visualization**: Map-based dashboard with GPS-tagged detections
- **Automated Reporting**: Generate PDF reports with before-after comparisons
- **Real-time Processing**: Fast API backend for video processing and inference
- **Interactive Dashboard**: Web interface for playback, analysis, and validation
- **Database Integration**: Supabase PostgreSQL database for scalable data storage

## System Architecture

```text
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

## Project Structure

```
NRSH/
├── backend/              # FastAPI backend
│   ├── api/             # API routes
│   ├── models/          # Database models (Supabase)
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
├── database/            # Database schema and setup
│   ├── schema.sql       # Supabase database schema
│   └── README.md        # Database setup guide
├── frontend/            # React/Next.js dashboard
│   ├── components/
│   ├── pages/
│   └── public/
├── config/              # Configuration files
├── requirements.txt     # Python dependencies
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- CUDA-capable GPU (optional, for faster inference)

### Installation

1. **Clone and setup Python environment:**

```bash
cd NRSH
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

4. **Setup Supabase Database (Optional but Recommended):**

```bash
# Create .env file with Supabase credentials

# See SUPABASE_SETUP.md for detailed instructions

# Run database schema

# Copy contents of database/schema.sql to Supabase SQL Editor

```

### Import System and Module Structure

The project uses a lightweight import pattern where modules add the project root to `sys.path` so cross-package imports work when running scripts directly. This is implemented by computing the project root via `Path(__file__).resolve().parent.parent` (or additional `.parent` calls depending on file depth) and inserting it into `sys.path`.

Key points:

- Backend routes depend on `backend.services`.
- Backend services depend on `ai_models`, `data_processing`, and `backend.models`.
- `ai_models` and `data_processing` import configuration (ConfigManager) from `backend.services.config_manager`.

Verifying imports

We provide a helper script to verify imports across the codebase:

```bash
python scripts/verify_imports.py
```

If any imports fail, ensure you are running the command from the project root and that all third-party dependencies are installed:

```bash
pip install -r requirements.txt
```

Troubleshooting

- `ModuleNotFoundError`: Run the verification script from the project root and confirm dependencies are installed.
- `ImportError` for third-party packages: install `requirements.txt`.
- Circular import errors: review the dependency map in `IMPORT_VERIFICATION_REPORT.md` and consider moving runtime imports into functions or installing the package in editable mode.

See `IMPORT_VERIFICATION_REPORT.md` for a detailed dependency map, identified issues, and recommended fixes.

## SoftwareDocumentCode directory

The repository contains an archival snapshot in `SoftwareDocumentCode/`. This
directory is a copy of the project tree intended for documentation, review,
and submission packages. It is not the canonical working tree — active
development and CI should target the root-level directories such as
`backend/`, `frontend/`, and `ai_models/`.

For full details about the snapshot contents and guidance on removal, see:

- `SoftwareDocumentCode/README.md`

Contributors should prefer modifying files under the project root (for
example, `backend/`, `frontend/`) rather than inside `SoftwareDocumentCode/`.

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
Open [http://localhost:3000](http://localhost:3000) in your browser

## Configuration

Edit `config/config.yaml` to customize:
- Model paths
- Detection thresholds
- GPS coordinate systems
- Report templates

### Environment Variables

Runtime configuration is also controlled via environment variables. A
centralized list and guidance are provided in `.env.example` at the
repository root. Common variables include `SUPABASE_URL`, `SUPABASE_KEY`,
`NEXT_PUBLIC_API_URL`, and frontend timeouts/polling variables.
Copy `.env.example` to `.env` for local development and modify values as
needed.

## Development & Formatting

We use common formatting tools to keep code consistent across the repository.

Python (backend, AI, data processing)

```bash
# install formatter tools (once)
python -m pip install --upgrade pip
python -m pip install black==23.12.0 isort==5.12.0

# sort imports then format
python -m isort backend ai_models data_processing scripts --profile black
python -m black backend ai_models data_processing scripts --line-length 88 --target-version py39
```

Frontend (React/Next.js)

```bash
cd frontend
npm install
# format all frontend files using Prettier (format script added to package.json)
npm run format
# run ESLint
npm run lint
```

We recommend adding these to a pre-commit hook (for example using `pre-commit`) to enforce formatting on commit.


## Usage

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

## Technical Details

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

## Innovation Highlights

1. **Temporal Comparison**: AI-driven before-after analysis
2. **Geospatial Intelligence**: GPS-tagged detections with map visualization
3. **Automated Scoring**: Severity-based issue prioritization
4. **Auditor Feedback Loop**: Validation mechanism for continuous improvement
5. **Real-time Processing**: Optimized pipeline for quick insights

## Software & Technologies Utilized

### Programming Languages

- **Python 3.9+**: Backend development, AI/ML processing, data analysis
- **JavaScript (ES6+)**: Frontend development, React components
- **SQL**: Database schema and queries (PostgreSQL)

### Backend Framework & Libraries

- **FastAPI 0.104.1**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **Pydantic**: Data validation and settings management
- **Python-multipart**: File upload handling

### AI/ML & Computer Vision

- **PyTorch 2.1.0**: Deep learning framework
- **Torchvision 0.16.0**: Computer vision utilities
- **Ultralytics YOLOv8 8.1.0**: Object detection model
- **OpenCV 4.8.1**: Computer vision and image processing
- **NumPy 1.24.3**: Numerical computing
- **Pillow 10.1.0**: Image processing
- **scikit-learn 1.3.2**: Machine learning utilities

### Data Processing & Analysis

- **Pandas 2.1.3**: Data manipulation and analysis
- **SciPy 1.11.4**: Scientific computing
- **imageio 2.31.6**: Image I/O operations
- **imageio-ffmpeg 0.4.9**: Video processing

### Geospatial Libraries

- **geopy 2.4.1**: Geocoding and distance calculations
- **folium 0.15.1**: Interactive map generation
- **geopandas 0.14.1**: Geospatial data operations
- **shapely 2.0.2**: Geometric operations

### Visualization

- **Matplotlib 3.8.2**: Static plotting
- **Seaborn 0.13.0**: Statistical data visualization
- **Plotly 5.18.0**: Interactive visualizations

### Report Generation

- **ReportLab 4.0.7**: PDF generation
- **FPDF2 2.7.6**: PDF creation library
- **Jinja2 3.1.2**: Template engine

### Database & ORM

- **Supabase 2.3.0**: PostgreSQL database with real-time capabilities
- **PostgREST 0.13.0**: REST API for PostgreSQL
- **SQLAlchemy 2.0.23**: SQL toolkit and ORM
- **Alembic 1.12.1**: Database migration tool

### Frontend Framework & Libraries

- **Next.js 14.2.33**: React framework for production
- **React 18.2.0**: UI library
- **React DOM 18.2.0**: React rendering
- **Axios 1.13.2**: HTTP client for API calls

### Frontend UI & Visualization

- **Leaflet 1.9.4**: Interactive maps
- **React-Leaflet 4.2.1**: React components for Leaflet
- **Recharts 2.10.3**: Chart library for React
- **Lucide React 0.294.0**: Icon library
- **Tailwind CSS 3.3.6**: Utility-first CSS framework

### Frontend Development Tools

- **TypeScript 5.3.3**: Type checking (dev dependency)
- **ESLint 8.56.0**: Code linting
- **PostCSS 8.4.32**: CSS processing
- **Autoprefixer 10.4.16**: CSS vendor prefixing

### Utilities & Configuration

- **python-dotenv 1.0.0**: Environment variable management
- **PyYAML 6.0.1**: YAML file parsing
- **aiofiles 23.2.1**: Async file operations
- **python-jose**: JWT token handling

### Testing

- **pytest 7.4.3**: Python testing framework
- **pytest-asyncio 0.21.1**: Async testing support

### Development Tools & Platforms

- **Git**: Version control
- **Node.js 16+**: JavaScript runtime
- **npm**: Node package manager
- **pip**: Python package manager
- **Virtual Environment (venv)**: Python environment isolation
- **Supabase Cloud**: Database hosting and management
- **CUDA** (Optional): GPU acceleration for AI inference

### IDEs & Editors

- **VS Code / Cursor**: Code editor
- **PowerShell**: Command-line interface (Windows)

### API Documentation

- **Swagger UI**: Interactive API documentation (auto-generated by FastAPI)
- **ReDoc**: Alternative API documentation

## 🗄️ Database Setup (Supabase)

The system uses Supabase (PostgreSQL) for data storage. Setup is optional - the system will fall back to file-based storage if Supabase is not configured.

- *Quick Setup:**

1. Create a Supabase project at [https://supabase.com](https://supabase.com)
2. Get your `SUPABASE_URL` and `SUPABASE_KEY` from project settings
3. Create `.env` file with credentials
4. Run `database/schema.sql` in Supabase SQL Editor
5. Test connection: `python scripts/test_database.py`

For detailed instructions, see [SUPABASE_SETUP.md](SUPABASE_SETUP.md) and [database/README.md](database/README.md).

## 📝 API Documentation

Once the server is running, visit:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🤝 Contributing

This is a hackathon project. For improvements:

1. Fork the repository
2. Create a feature branch
3. Submit pull request

## 📄 License

MIT License - Hackathon Project

## 👥 Team

National Road Safety Hackathon 2025 — Team: CHIKKUZ

Members:
1. Ananya Rai
2. Sumant Kumar Giri