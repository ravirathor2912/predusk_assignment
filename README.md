# Multi-Object Detection + Persistent ID Tracking (Sports/Event Footage)

This project detects multiple moving subjects in a video and tracks them with **unique, persistent IDs**, producing an **annotated output video**.

## What you get
- Detection: **YOLOv8** (Ultralytics)
- Tracking: **BoT-SORT** (default) or ByteTrack via Ultralytics tracking
- Outputs:
  - annotated video (`outputs/<run>/annotated.mp4`)
  - tracking CSV (`outputs/<run>/tracks.csv`)
  - a few screenshots (`outputs/<run>/screenshots/*.jpg`)

## Live hosted URL (optional)
This repo includes a minimal Streamlit app (`app.py`). Deployment steps (to get a public URL) are in [DEPLOYMENT.md](DEPLOYMENT.md).

## Setup (Windows)
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Notes:
- First run will download YOLO weights (e.g. `yolov8n.pt`).
- If you use YouTube/streaming URLs, `yt-dlp` may need **ffmpeg** installed and on PATH.
- Tracking depends on `lap` (included in `requirements.txt`).

## Quick sanity test (no internet)
Runs an end-to-end smoke test that generates a small demo video and executes the tracker:
```bash
python scripts/smoke_test.py
```

If you just want a synthetic video generator:
```bash
python scripts/generate_synthetic_video.py --out outputs/synth.mp4
```

## Run on a real public video
### Option A: Local file
```bash
python track.py --source path\\to\\your_video.mp4 --run-name my_run
```

### Option B: Public URL
```bash
python track.py --source "https://..." --run-name my_run
```
You can also download first:
```bash
python scripts/download_video.py --url "https://..." --out-dir outputs/download
```
If URL download fails, download the video yourself (keeping the public link for the submission) and run using Option A.

## Common settings
- Track people only (COCO class 0):
```bash
python track.py --source ... --classes 0
```
- Higher confidence threshold:
```bash
python track.py --source ... --conf 0.35
```
- Use GPU (if available):
```bash
python track.py --source ... --device 0
```

## Deliverables checklist
- Annotated output video: `outputs/<run>/annotated.mp4`
- Source video link: add to [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md)
- Short report (1–2 pages): [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md)

## Troubleshooting
- If you see `ModuleNotFoundError`, confirm venv is active and `pip install -r requirements.txt` succeeded.
- If IDs flicker a lot, try `--tracker botsort` and increase `--imgsz` (e.g. 960) at a cost of speed.
