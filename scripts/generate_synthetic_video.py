import argparse
from pathlib import Path

import cv2
import numpy as np


def parse_args():
    p = argparse.ArgumentParser(description="Generate a synthetic video for pipeline sanity checks")
    p.add_argument("--out", required=True, help="Output video path, e.g. outputs/synth.mp4")
    p.add_argument("--seconds", type=int, default=8)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--w", type=int, default=960)
    p.add_argument("--h", type=int, default=540)
    p.add_argument("--objects", type=int, default=6)
    return p.parse_args()


def main():
    args = parse_args()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, args.fps, (args.w, args.h))
    if not writer.isOpened():
        raise RuntimeError("Could not create output writer")

    rng = np.random.default_rng(0)
    pos = rng.uniform([50, 50], [args.w - 100, args.h - 100], size=(args.objects, 2))
    vel = rng.uniform([-6, -4], [6, 4], size=(args.objects, 2))
    sizes = rng.uniform([40, 50], [90, 120], size=(args.objects, 2))

    n_frames = args.seconds * args.fps
    for t in range(n_frames):
        frame = np.zeros((args.h, args.w, 3), dtype=np.uint8)
        frame[:] = (20, 20, 20)

        # add some lines to mimic background texture
        for x in range(0, args.w, 60):
            cv2.line(frame, (x, 0), (x, args.h), (30, 30, 30), 1)

        for i in range(args.objects):
            pos[i] += vel[i]
            if pos[i, 0] < 0 or pos[i, 0] + sizes[i, 0] > args.w:
                vel[i, 0] *= -1
                pos[i, 0] = np.clip(pos[i, 0], 0, args.w - sizes[i, 0])
            if pos[i, 1] < 0 or pos[i, 1] + sizes[i, 1] > args.h:
                vel[i, 1] *= -1
                pos[i, 1] = np.clip(pos[i, 1], 0, args.h - sizes[i, 1])

            x1, y1 = pos[i].astype(int)
            x2, y2 = (pos[i] + sizes[i]).astype(int)

            # occasional occlusion: draw a black rectangle covering part of scene
            if 80 < t < 120 and i % 2 == 0:
                cv2.rectangle(frame, (args.w // 3, args.h // 3), (args.w // 3 + 200, args.h // 3 + 200), (0, 0, 0), -1)

            color = (int(80 + (i * 40) % 175), int(120 + (i * 70) % 135), int(150 + (i * 90) % 105))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
            cv2.putText(frame, f"obj{i}", (x1 + 5, y1 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, cv2.LINE_AA)

        cv2.putText(frame, f"synthetic frame {t}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (230, 230, 230), 2, cv2.LINE_AA)
        writer.write(frame)

    writer.release()
    print(f"Wrote synthetic video: {out_path}")


if __name__ == "__main__":
    main()
