"""
Script to download AI models
"""

from pathlib import Path
from ultralytics import YOLO
import sys


def download_yolo_model(model_name: str = "yolov8n.pt"):
    """Download YOLOv8 model"""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    model_path = models_dir / model_name
    
    if model_path.exists():
        print(f"Model {model_name} already exists at {model_path}")
        return model_path
    
    print(f"Downloading {model_name}...")
    try:
        model = YOLO(model_name)
        # Save to models directory
        model.save(str(model_path))
        print(f"Model downloaded successfully to {model_path}")
        return model_path
    except Exception as e:
        print(f"Error downloading model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download AI models")
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt",
        help="Model name to download (default: yolov8n.pt)"
    )
    
    args = parser.parse_args()
    download_yolo_model(args.model)
