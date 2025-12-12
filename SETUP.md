# Setup Guide

## Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- pip (Python package manager)
- npm or yarn (Node package manager)

## Backend Setup

1. **Create virtual environment:**
```bash
python -m venv venv
```

2. **Activate virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Download AI models:**
```bash
python scripts/download_models.py
```

5. **Create necessary directories:**
```bash
mkdir -p uploads processed cache reports models
```

6. **Start backend server:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

## Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Create environment file (optional):**
```bash
cp ../.env.example .env.local
# Edit .env.local if needed

```

4. **Start development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Single-media detection (optional)

- In the web UI uploader, enable “Single-media detection” to run detection on one image or video without needing a base/present pair. Results appear in the dashboard under a generated analysis ID.

## Running the Full Application

1. Start the backend server (in one terminal):
```bash
cd backend
uvicorn main:app --reload --port 8000
```

2. Start the frontend server (in another terminal):
```bash
cd frontend
npm run dev
```

3. Open your browser and navigate to `http://localhost:3000`

## Project Structure

```
RSH/
├── backend/              # FastAPI backend
│   ├── api/             # API routes
│   ├── services/        # Business logic
│   └── main.py          # FastAPI app entry
├── ai_models/           # AI model scripts
│   ├── detection/       # Object detection
│   └── change_detection/ # Change detection
├── data_processing/     # Video processing
│   ├── frame_extraction.py
│   └── alignment.py
├── frontend/            # Next.js frontend
│   ├── components/      # React components
│   ├── pages/           # Next.js pages
│   └── styles/          # CSS files
├── config/              # Configuration files
├── scripts/             # Utility scripts
└── requirements.txt     # Python dependencies
```

## Troubleshooting

### Backend Issues

- **Import errors**: Make sure you're running from the project root or backend directory
- **Model not found**: Run `python scripts/download_models.py` to download models
- **Port already in use**: Change port in `backend/main.py` or kill the process using port 8000

### Frontend Issues

- **Module not found**: Run `npm install` again
- **API connection error**: Ensure backend is running on port 8000
- **Leaflet map not showing**: Check browser console for CORS or API errors

## Development Notes

- The backend uses FastAPI with automatic API documentation at `/docs`
- The frontend uses Next.js with React
- Videos are stored in `uploads/` directory
- Analysis results are stored in `processed/` directory
- Reports are generated in `reports/` directory

## Next Steps

1. Train custom YOLOv8 model on road infrastructure dataset
2. Implement database for persistent storage
3. Add user authentication
4. Deploy to cloud platform (AWS, GCP, Azure)
5. Add more visualization features
