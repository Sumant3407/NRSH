# Samples

This folder documents sample assets for quick demos.

We do not commit video binaries. Use the download script to fetch small public sample videos.

## Download

From project root:

```bash
# Windows PowerShell

python scripts/download_sample_videos.py
```

This will create:
- `uploads/samples/base_road_sample.mp4`
- `uploads/samples/present_road_sample.mp4`
- `uploads/samples/base_gps.json`
- `uploads/samples/present_gps.json`

## Use in App

- Upload `base_road_sample.mp4` as Base
- Upload `present_road_sample.mp4` as Present
- Optionally paste the contents of `base_gps.json` / `present_gps.json` into the GPS field (if you extend the UI to accept it), or rely on temporal alignment.

### Single-media detection

- To test detection without comparison, upload a single image or video and check “Single-media detection” in the uploader. Results will appear in the dashboard under a generated analysis ID.
