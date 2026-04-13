from __future__ import annotations

from typing import Tuple

import cv2


def color_for_id(track_id: int) -> Tuple[int, int, int]:
    """Deterministic bright-ish BGR color for a given track id."""
    if track_id is None or track_id < 0:
        return (0, 255, 255)

    # simple hash -> stable color
    r = (37 * track_id) % 255
    g = (17 * track_id + 99) % 255
    b = (29 * track_id + 199) % 255

    # bias to be more visible
    r = int(80 + (r * 175 / 255))
    g = int(80 + (g * 175 / 255))
    b = int(80 + (b * 175 / 255))
    return (b, g, r)


def draw_box(frame, xyxy, color=(0, 255, 0), label: str | None = None) -> None:
    x1, y1, x2, y2 = [int(v) for v in xyxy]
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    if label:
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        (tw, th), baseline = cv2.getTextSize(label, font, font_scale, thickness)
        th += baseline
        y_text = max(y1, th + 2)
        cv2.rectangle(frame, (x1, y_text - th), (x1 + tw + 6, y_text + 2), color, -1)
        cv2.putText(frame, label, (x1 + 3, y_text - 4), font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)
