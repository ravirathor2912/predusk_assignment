from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm
from ultralytics import YOLO

from jd_tracker.io import ensure_local_source
from jd_tracker.viz import color_for_id, draw_box


@dataclass(frozen=True)
class TrackingOutputs:
    source_path: Path
    annotated_path: Path
    tracks_csv: Path
    screenshots_dir: Path


def _probe_video(path: Path) -> tuple[float, int, int, int | None]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames_raw = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    total_frames = int(total_frames_raw) if total_frames_raw and total_frames_raw > 0 else None
    cap.release()
    return float(fps), width, height, total_frames


def _pick_screenshot_indices(total_frames: int | None, count: int) -> set[int]:
    if count <= 0:
        return set()
    if count == 1:
        return {0 if not total_frames else max(0, total_frames // 2)}

    if total_frames and total_frames > 0:
        return {int(i * (total_frames - 1) / (count - 1)) for i in range(count)}

    return {0}


def run_tracking(
    *,
    source: str,
    outputs_dir: Path,
    model: str = "yolov8n.pt",
    tracker: str = "botsort",
    imgsz: int = 640,
    conf: float = 0.25,
    iou: float = 0.5,
    classes: list[int] | None = None,
    device: str | None = None,
    max_frames: int | None = None,
    save_screenshots: int = 5,
) -> TrackingOutputs:
    outputs_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir = outputs_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    source_path = ensure_local_source(source, outputs_dir)
    fps, width, height, total_frames = _probe_video(source_path)

    yolo = YOLO(model)
    tracker_cfg = "botsort.yaml" if tracker == "botsort" else "bytetrack.yaml"

    stream: Iterable = yolo.track(
        source=str(source_path),
        stream=True,
        persist=True,
        tracker=tracker_cfg,
        imgsz=imgsz,
        conf=conf,
        iou=iou,
        classes=classes,
        device=device,
        verbose=False,
    )

    annotated_path = outputs_dir / "annotated.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(annotated_path), fourcc, fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError("Could not create output video writer")

    effective_total = total_frames
    if max_frames is not None and max_frames > 0:
        effective_total = min(total_frames, max_frames) if total_frames else max_frames
    screenshot_indices = _pick_screenshot_indices(effective_total, int(save_screenshots))

    rows: list[dict] = []
    frame_idx = 0

    pbar_total = min(total_frames, max_frames) if (total_frames and max_frames) else (total_frames or max_frames)
    pbar = tqdm(total=pbar_total, desc="Tracking", unit="frame")

    for result in stream:
        frame = result.orig_img
        if frame is None:
            break

        boxes = result.boxes
        if boxes is not None and boxes.xyxy is not None and len(boxes) > 0:
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy() if boxes.conf is not None else np.zeros((len(xyxy),), dtype=float)
            clss = boxes.cls.cpu().numpy().astype(int) if boxes.cls is not None else np.zeros((len(xyxy),), dtype=int)
            ids = (
                boxes.id.cpu().numpy().astype(int)
                if getattr(boxes, "id", None) is not None
                else np.full((len(xyxy),), -1, dtype=int)
            )

            for (x1, y1, x2, y2), det_conf, cls, tid in zip(xyxy, confs, clss, ids):
                color = color_for_id(int(tid))
                label = f"ID:{int(tid)} conf:{det_conf:.2f} cls:{int(cls)}"
                draw_box(frame, (x1, y1, x2, y2), color=color, label=label)
                rows.append(
                    {
                        "frame": frame_idx,
                        "track_id": int(tid),
                        "cls": int(cls),
                        "conf": float(det_conf),
                        "x1": float(x1),
                        "y1": float(y1),
                        "x2": float(x2),
                        "y2": float(y2),
                    }
                )

        cv2.putText(
            frame,
            f"frame {frame_idx}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        writer.write(frame)

        if frame_idx in screenshot_indices:
            out_path = screenshots_dir / f"frame_{frame_idx:06d}.jpg"
            cv2.imwrite(str(out_path), frame)

        frame_idx += 1
        pbar.update(1)

        if max_frames is not None and frame_idx >= max_frames:
            break

    pbar.close()
    writer.release()

    tracks_csv = outputs_dir / "tracks.csv"
    if rows:
        pd.DataFrame(rows).to_csv(tracks_csv, index=False)
    else:
        pd.DataFrame(columns=["frame", "track_id", "cls", "conf", "x1", "y1", "x2", "y2"]).to_csv(tracks_csv, index=False)

    return TrackingOutputs(
        source_path=source_path,
        annotated_path=annotated_path,
        tracks_csv=tracks_csv,
        screenshots_dir=screenshots_dir,
    )
