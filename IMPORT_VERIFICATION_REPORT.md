# Import Verification Report

This document summarizes the import patterns, dependency map, verification status, potential issues, and recommended next steps for the NRSH codebase.

1. Import Pattern Summary
-------------------------

- Pattern: Many modules add the project root to `sys.path` at runtime, typically via `Path(__file__).resolve().parent.parent` (or additional `.parent` calls depending on depth) and `sys.path.insert(0, str(project_root))`.
- Purpose: This enables cross-package imports when running modules directly from files or scripts without installing the package.
- Project root calculation examples:
  - Files in `scripts/` or top-level use `Path(__file__).parent.parent` to reach root.
  - Files two or three directories deep use additional `.parent` calls to reach the project root.

2. Import Dependency Map
------------------------

- `backend/main.py` → imports `backend.api.routes.*` and `backend.services.config_manager`
- `backend/api/routes/*.py` → import from `backend.services`
- `backend/services/analysis_service.py` → imports from `backend.services`, `backend.models.database`, `data_processing`, and `ai_models`
- `backend/services/video_service.py` → imports from `backend.services.config_manager`, `backend.services.database_service`, `backend.models.database`
- `backend/services/database_service.py` → imports from `backend.models.database`
- `backend/services/report_service.py` → imports from `backend.services.config_manager`, `backend.services.analysis_service`
- `backend/services/dashboard_service.py` → imports from `backend.services.config_manager`, `backend.services.analysis_service`, `backend.services.video_service`
- `ai_models/detection/detector.py` → imports from `backend.services.config_manager`
- `ai_models/change_detection/change_detector.py` → imports from `backend.services.config_manager`
- `data_processing/frame_extraction.py` → imports from `backend.services.config_manager`
- `data_processing/alignment.py` → imports from `backend.services.config_manager`, `data_processing.frame_extraction`

3. Verified Import Paths
------------------------

- Standard library imports: os, sys, json, pathlib, datetime, etc. — ✓ Available
- Third-party imports: fastapi, pydantic, cv2, numpy, ultralytics, supabase, etc. — ⚠ Requires environment setup per `requirements.txt`
- Internal package imports: Documented above (Dependency Map). These rely on the `sys.path` manipulation pattern.

4. Potential Issues Identified
----------------------------

Issue 1: Circular Import Risk
- Description: `backend.services.analysis_service` imports from `ai_models` and `data_processing`, both of which import `backend.services.config_manager`.
- Impact: Potential circular dependency chain `backend.services -> ai_models/data_processing -> backend.services`.
- Status: ⚠ Monitor at runtime; often safe if imports are simple constants or class definitions but can surface as ImportError in some execution orders.

Issue 2: `backend/models/__init__.py` Import Mismatch
- Description: The file attempted to import top-level names (`Video`, `Analysis`, etc.) but the actual model definitions in `backend/models/database.py` use `*Model` suffixes.
- Status: ❌ This would cause ImportError on `from backend.models import Video`.
- Resolution: Updated `backend/models/__init__.py` to export the correct names (`VideoModel`, `AnalysisModel`, `DetectionModel`, `ReportModel`, `RoadSegmentModel`).

Issue 3: Fragile `project_root` Calculation
- Description: Different files compute project root with varying `.parent` counts. File relocation or refactors can break imports.
- Status: ⚠ Fragile and error-prone.
- Recommendation: Prefer installing the package in editable mode (`pip install -e .`) or centralize path logic.

5. Import Testing Recommendations
--------------------------------

Run these checks from the project root (project root contains `scripts/`):

a) Test `backend.main` imports:

```
python -c "from backend.main import app; print('✓ backend.main imports successful')"
```

b) Test service imports:

```
python -c "from backend.services.analysis_service import AnalysisService; print('✓ AnalysisService imports successful')"
```

c) Test AI model imports:

```
python -c "from ai_models.detection.detector import ObjectDetector; print('✓ ObjectDetector imports successful')"
```

d) Test data processing imports:

```
python -c "from data_processing.frame_extraction import FrameExtractor; print('✓ FrameExtractor imports successful')"
```

e) Test database service imports:

```
python -c "from backend.services.database_service import DatabaseService; print('✓ DatabaseService imports successful')"
```

Notes: Some imports may succeed only when environment variables (e.g., Supabase credentials) or third-party packages are available. The import checks focus on Python-level import resolution and attribute presence.

6. Summary and Recommendations
------------------------------

- Files analyzed: 20+ (core modules across `backend`, `ai_models`, `data_processing`)
- Import pattern: Consistent `sys.path` manipulation across modules
- Critical issues: 1 (models __init__ import mismatch) — fixed in this change
- Warnings: circular import risk and fragile project_root calculation

Recommended actions:
1. Keep the fix for `backend/models/__init__.py` (done).
2. Run the provided `scripts/verify_imports.py` to validate imports in your environment.
3. Consider refactoring imports by installing the package in editable mode (`pip install -e .`) or centralizing path-handling logic.
4. Add import verification to CI to catch regressions early.

---

Generated on: (run-time)
