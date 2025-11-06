# Quick Start Guide - How to Run the Project

## Prerequisites Check

First, verify you have the required tools:

```powershell
# Check Python version (need 3.9+)
python --version

# Check Node.js version (need 16+)
node --version

# Check npm
npm --version
```

## Step-by-Step Setup

### Step 1: Create Python Virtual Environment

Open PowerShell in the project directory (`C:\Users\suman\Documents\RSH`):

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run this first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should see `(venv)` at the start of your command prompt.

### Step 2: Install Python Dependencies

```powershell
# Make sure venv is activated (you should see (venv))
pip install -r requirements.txt
```

This will install all required packages (FastAPI, PyTorch, YOLOv8, etc.)

### Step 3: Create Required Directories

```powershell
# Create directories for uploads, results, etc.
New-Item -ItemType Directory -Force -Path uploads, processed, cache, reports, models
```

### Step 4: Download AI Models

```powershell
# Download YOLOv8 model (this may take a few minutes)
python scripts/download_models.py
```

### Step 5: Install Frontend Dependencies

Open a **new PowerShell window** (keep the backend one open):

```powershell
# Navigate to project directory
cd C:\Users\suman\Documents\RSH

# Navigate to frontend
cd frontend

# Install Node.js dependencies
npm install
```

This may take a few minutes.

## Running the Application

You need **two terminals** running simultaneously:

### Terminal 1: Backend Server

```powershell
# Navigate to project root
cd C:\Users\suman\Documents\RSH

# Activate virtual environment (if not already activated)
.\venv\Scripts\Activate.ps1

# Run backend server (from project root)
uvicorn backend.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Backend API is now running at:** http://localhost:8000
**API Documentation:** http://localhost:8000/docs

### Terminal 2: Frontend Server

```powershell
# Navigate to frontend directory
cd C:\Users\suman\Documents\RSH\frontend

# Run frontend development server
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

**Frontend is now running at:** http://localhost:3000

## Access the Application

1. Open your web browser
2. Navigate to: **http://localhost:3000**
3. You should see the Road Safety Infrastructure Analysis dashboard

## Alternative: Run Backend from Backend Directory

If you prefer to run from the backend directory:

```powershell
cd backend
python main.py
```

This also works because we fixed the import paths!

## Testing the API

You can test the API directly:

1. **Open API Docs:** http://localhost:8000/docs
2. **Test Health Endpoint:** http://localhost:8000/health
3. **Root Endpoint:** http://localhost:8000/

## Troubleshooting

### Backend Issues

**Problem: ModuleNotFoundError**
```powershell
# Make sure you're in the project root and venv is activated
cd C:\Users\suman\Documents\RSH
.\venv\Scripts\Activate.ps1
```

**Problem: Port 8000 already in use**
```powershell
# Find and kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Or change the port in backend/main.py
```

**Problem: Config file not found**
- Make sure `config/config.yaml` exists
- Check you're running from project root

### Frontend Issues

**Problem: npm install fails**
```powershell
# Clear npm cache and try again
npm cache clean --force
npm install
```

**Problem: Cannot connect to API**
- Make sure backend is running on port 8000
- Check `frontend/next.config.js` has correct API URL
- Check browser console for CORS errors

**Problem: Execution Policy Error (PowerShell)**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Quick Commands Reference

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run backend (from project root)
uvicorn backend.main:app --reload --port 8000

# Run backend (from backend directory)
cd backend
python main.py

# Run frontend
cd frontend
npm run dev

# Deactivate virtual environment (when done)
deactivate
```

## Next Steps

1. ✅ Backend and frontend are running
2. Open http://localhost:3000 in your browser
3. Upload test videos (base and present)
4. Run analysis
5. View results in the dashboard

## Full Command Sequence (Copy-Paste)

```powershell
# Terminal 1: Backend
cd C:\Users\suman\Documents\RSH
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/download_models.py
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend (in new PowerShell window)
cd C:\Users\suman\Documents\RSH\frontend
npm install
npm run dev
```

Then open http://localhost:3000 in your browser!

## Download sample videos (optional)

```powershell
# From project root
python scripts/download_sample_videos.py
```

This creates sample files in `uploads/samples/`:
- `base_road_sample.mp4`
- `present_road_sample.mp4`
- `base_gps.json` and `present_gps.json` (optional)

Use these via the web uploader as Base and Present to test the pipeline.

