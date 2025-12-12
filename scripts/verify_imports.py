import importlib
import sys
from pathlib import Path
from types import ModuleType
from typing import List, Optional, Tuple


# Function: add_project_root_to_path
def add_project_root_to_path():
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
    return project_root


# Function: test_import
def test_import(module_path: str, attr: Optional[str] = None) -> Tuple[bool, str]:
    """Attempt to import module and optionally verify a class exists.

    Returns a tuple (ok: bool, message: str).
    """
    try:
        module = importlib.import_module(module_path)
    except Exception as exc:  # ImportError, ModuleNotFoundError, etc.
        return False, f"IMPORT FAILED: {module_path} -> {exc!r}"

    if attr:
        try:
            if not hasattr(module, attr):
                return False, f"MISSING ATTR: {module_path}.{attr}"
        except Exception as exc:
            return False, f"ATTR CHECK FAILED: {module_path}.{attr} -> {exc!r}"

    return True, f"OK: {module_path}{'.' + attr if attr else ''}"


# Function: print_summary
def print_summary(results: List[Tuple[str, bool, str]]):
    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = total - passed

    print("\nImport Verification Summary")
    print("---------------------------")
    for label, ok, msg in results:
        mark = "[OK]" if ok else "[FAIL]"
        print(f"{mark} {label}: {msg}")

    print("\nTotals:")
    print(f"  Tested:  {total}")
    print(f"  Passed:  {passed}")
    print(f"  Failed:  {failed}")


# Function: main
def main():
    project_root = add_project_root_to_path()
    print(f"Project root: {project_root}")

    tests: List[Tuple[str, Optional[str]]] = [
        ("backend.main", "app"),
        ("backend.api.routes.video", None),
        ("backend.api.routes.analysis", None),
        ("backend.api.routes.reports", None),
        ("backend.api.routes.dashboard", None),
        ("backend.services.config_manager", None),
        ("backend.services.video_service", None),
        ("backend.services.analysis_service", None),
        ("backend.services.database_service", None),
        ("backend.services.report_service", None),
        ("backend.services.dashboard_service", None),
        ("backend.models.database", None),
        ("ai_models.detection.detector", "ObjectDetector"),
        ("ai_models.change_detection.change_detector", "ChangeDetector"),
        ("data_processing.frame_extraction", "FrameExtractor"),
        ("data_processing.alignment", "FrameAligner"),
        ("data_processing.preprocessing", "ImagePreprocessor"),
    ]

    results: List[Tuple[str, bool, str]] = []
    for module_path, attr in tests:
        ok, msg = test_import(module_path, attr)
        results.append((module_path + ("." + attr if attr else ""), ok, msg))

    cross_checks: List[Tuple[str, Optional[str]]] = [
        ("ai_models.detection.detector", "ObjectDetector"),
        ("data_processing.frame_extraction", "FrameExtractor"),
        ("backend.services.analysis_service", None),
    ]

    for module_path, attr in cross_checks:
        ok, msg = test_import(module_path, attr)
        results.append((f"cross:{module_path}{'.' + attr if attr else ''}", ok, msg))

    print_summary(results)

    all_ok = all(ok for _, ok, _ in results)
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
