"""
Download sample road videos and optional GPS metadata for quick testing.

This script downloads small public-domain/sample videos suitable for demo purposes.
"""

import sys
import json
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

SAMPLES = [
    {
        "name": "base_road_sample.mp4",
        "url": "https://samplelib.com/lib/preview/mp4/sample-5s.mp4"
    },
    {
        "name": "present_road_sample.mp4",
        "url": "https://samplelib.com/lib/preview/mp4/sample-10s.mp4"
    }
]

GPS_BASE = {
    "0": [12.9716, 77.5946],
    "30": [12.9717, 77.5947],
    "60": [12.9718, 77.5948]
}

GPS_PRESENT = {
    "0": [12.9716, 77.5946],
    "30": [12.9717, 77.59475],
    "60": [12.97185, 77.5949]
}


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(url) as r, open(dest, 'wb') as f:
            f.write(r.read())
        print(f"Downloaded: {dest}")
    except (URLError, HTTPError) as e:
        print(f"Failed to download {url}: {e}")


def main():
    project_root = Path(__file__).resolve().parents[1]
    uploads = project_root / "uploads" / "samples"
    uploads.mkdir(parents=True, exist_ok=True)

    for item in SAMPLES:
        dest = uploads / item["name"]
        if dest.exists() and dest.stat().st_size > 0:
            print(f"Already exists: {dest}")
            continue
        download(item["url"], dest)

    # Write example GPS metadata JSON files
    gps_dir = uploads
    (gps_dir / "base_gps.json").write_text(json.dumps(GPS_BASE, indent=2))
    (gps_dir / "present_gps.json").write_text(json.dumps(GPS_PRESENT, indent=2))
    print(f"Wrote GPS metadata: {gps_dir / 'base_gps.json'}")
    print(f"Wrote GPS metadata: {gps_dir / 'present_gps.json'}")

    print("\nDone. Sample videos are in uploads/samples/")
    print("Use these with the uploader UI or via API:")
    print("- Base: uploads/samples/base_road_sample.mp4")
    print("- Present: uploads/samples/present_road_sample.mp4")
    print("- GPS: uploads/samples/base_gps.json and present_gps.json (optional)")


if __name__ == "__main__":
    main()
