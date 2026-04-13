# Short Technical Report (1–2 pages)

## Video source
- Public source link: <PASTE YOUR PUBLIC VIDEO LINK HERE>
- Video title/channel/event: <FILL>
- Why this video: Multiple moving subjects with occlusions and camera motion.

## Approach
### Detector
- Model: YOLOv8 (Ultralytics), default `yolov8n.pt` (configurable)
- Target classes: COCO class `0` (person) for players/officials
- Key settings used: `conf=0.25`, `imgsz=640`, `iou=0.5`

### Tracker
- Tracker: BoT-SORT (via Ultralytics tracking)
- Why this tracker: robust association under occlusions and camera motion; uses motion + appearance cues (depending on config)

## Pipeline design
1. Download the public video to a local file
2. Run `YOLO.track(...)` on the local video
3. For each frame:
   - extract boxes, confidences, classes, **track IDs**
   - draw bounding boxes + `ID:<n>` labels
   - write annotated frame to output video
   - append per-frame data to `tracks.csv`
4. Save a few screenshots for reporting

## How ID consistency is maintained
- The tracker keeps an internal state per object track (position/velocity prediction) and matches new detections to existing tracks each frame.
- When objects overlap/occlude, matching relies on predicted motion and (tracker-dependent) appearance association to reduce ID switches.

## Challenges encountered
- Occlusion/overlap causing ID switches
- Motion blur and small objects at distance
- Camera pan/zoom changing scale

## Observed failure cases
- Prolonged full occlusion (track may be dropped and later re-created with a new ID)
- Very similar uniforms/appearance when players cross
- Tiny objects (ball) can be missed depending on resolution

## Improvements
- Increase resolution (`--imgsz`) or use larger model (`yolov8s.pt`)
- Tune tracker parameters / ReID settings (if enabled)
- Add sport-specific fine-tuning or segmentation
- Optional evaluation: manually label a short segment and compute IDF1/MOTA

## Run command used (for reproducibility)
For long videos, process a short segment first (e.g., 600–1800 frames):

`python track.py --source "path\\to\\video.mp4" --run-name submission_run --classes 0 --tracker botsort --imgsz 640 --conf 0.25 --iou 0.5 --max-frames 900 --save-screenshots 5`
