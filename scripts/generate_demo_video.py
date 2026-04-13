import argparse
from pathlib import Path

import cv2
import numpy as np


def _try_load_ultralytics_sample() -> np.ndarray | None:
    """Best-effort load of a sample image that contains people.

    This is used only for generating an offline-ish demo video for verification.
    """
    try:
        from ultralytics.utils.files import ROOT  # type: ignore

        candidate = Path(str(ROOT)) / "assets" / "zidane.jpg"
        if candidate.exists():
            img = cv2.imread(str(candidate))
            return img
    except Exception:
        pass

    return None


def parse_args():
    p = argparse.ArgumentParser(description="Generate a demo video (panning over an image) for verification")
    p.add_argument("--out", required=True, help="Output video path")
    p.add_argument("--seconds", type=int, default=6)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--w", type=int, default=960)
    p.add_argument("--h", type=int, default=540)
    return p.parse_args()


def main():
    args = parse_args()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    base = _try_load_ultralytics_sample()
    if base is None:
        # fallback: simple textured image
        base = np.zeros((1080, 1920, 3), dtype=np.uint8)
        base[:] = (40, 40, 40)
        for y in range(0, base.shape[0], 40):
            cv2.line(base, (0, y), (base.shape[1], y), (60, 60, 60), 1)
        cv2.putText(base, "fallback demo (no people)", (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (200, 200, 200), 3)

    base_h, base_w = base.shape[:2]
    out_w, out_h = args.w, args.h

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, args.fps, (out_w, out_h))
    if not writer.isOpened():
        raise RuntimeError("Could not create output writer")

    n_frames = args.seconds * args.fps
    for t in range(n_frames):
        # horizontal pan
        if base_w <= out_w:
            x = 0
        else:
            x = int((base_w - out_w) * (t / max(1, n_frames - 1)))
        if base_h <= out_h:
            y = 0
        else:
            y = int((base_h - out_h) * (0.2 + 0.6 * (np.sin(t / 10) * 0.5 + 0.5)))

        crop = base[y : y + out_h, x : x + out_w]
        if crop.shape[0] != out_h or crop.shape[1] != out_w:
            crop = cv2.resize(crop, (out_w, out_h), interpolation=cv2.INTER_LINEAR)

        cv2.putText(crop, f"demo frame {t}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        writer.write(crop)

    writer.release()
    print(f"Wrote demo video: {out_path}")


if __name__ == "__main__":
    main()
