# Short Technical Report (1–2 pages)

## Video source
- Public source link: <PASTE LINK HERE>
- Video title/channel/event: <FILL>
- Why this video: <multi-subject motion, occlusions, camera movement, etc>

## Approach
### Detector
- Model: YOLOv8 (Ultralytics), default `yolov8n.pt` (configurable)
- Target classes: <e.g., person/players>
- Key settings: confidence threshold, image size

### Tracker
- Tracker: BoT-SORT (via Ultralytics tracking)
- Why this tracker: robust association under occlusions and camera motion; uses motion + appearance cues (depending on config)

## Pipeline design
1. (Optional) Download from URL using `yt-dlp`
2. Run `YOLO.track(...)` on the video
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
