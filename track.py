import argparse
from pathlib import Path

from jd_tracker.pipeline import run_tracking


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Multi-object detection + persistent ID tracking")
    p.add_argument("--source", required=True, help="Path to a video file or a public URL")
    p.add_argument("--run-name", default="run", help="Output subfolder name under outputs/")
    p.add_argument("--model", default="yolov8n.pt", help="Ultralytics YOLO model weights")
    p.add_argument("--tracker", choices=["botsort", "bytetrack"], default="botsort")
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--iou", type=float, default=0.5)
    p.add_argument("--classes", type=int, nargs="*", default=None, help="Filter by class ids (COCO). Example: --classes 0")
    p.add_argument("--device", default=None, help="e.g. 'cpu', '0' for CUDA device 0")
    p.add_argument("--max-frames", type=int, default=None, help="Process only first N frames")
    p.add_argument("--save-screenshots", type=int, default=5, help="Number of screenshots to save")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    outputs_dir = Path("outputs") / args.run_name
    outputs = run_tracking(
        source=args.source,
        outputs_dir=outputs_dir,
        model=args.model,
        tracker=args.tracker,
        imgsz=args.imgsz,
        conf=args.conf,
        iou=args.iou,
        classes=args.classes,
        device=args.device,
        max_frames=args.max_frames,
        save_screenshots=args.save_screenshots,
    )

    print(f"Saved annotated video: {outputs.annotated_path}")
    print(f"Saved tracks CSV: {outputs.tracks_csv}")
    print(f"Saved screenshots: {outputs.screenshots_dir}")


if __name__ == "__main__":
    main()
