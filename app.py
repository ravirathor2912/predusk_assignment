from __future__ import annotations

import tempfile
from pathlib import Path
from uuid import uuid4

import streamlit as st

from jd_tracker.pipeline import run_tracking


st.set_page_config(page_title="Detection + Tracking", layout="centered")

st.title("Multi-Object Detection + Persistent ID Tracking")

st.write("Upload a video (or provide a public URL), then run detection + tracking and download the annotated result.")

source_mode = st.radio("Input", ["Upload video", "Public URL"], horizontal=True)

uploaded = None
url = ""

if source_mode == "Upload video":
    uploaded = st.file_uploader("Video file", type=["mp4", "mov", "mkv", "avi"])
else:
    url = st.text_input("Public video URL", placeholder="https://...")

with st.expander("Settings", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        model = st.text_input("Model", value="yolov8n.pt")
        tracker = st.selectbox("Tracker", ["botsort", "bytetrack"], index=0)
        imgsz = st.number_input("Image size (imgsz)", min_value=320, max_value=1280, value=640, step=32)
    with col2:
        conf = st.slider("Confidence", min_value=0.0, max_value=1.0, value=0.25, step=0.05)
        iou = st.slider("IOU", min_value=0.0, max_value=1.0, value=0.50, step=0.05)
        max_frames = st.number_input("Max frames (optional)", min_value=0, value=0, step=30, help="0 = process full video")

    classes_str = st.text_input("Classes (optional)", value="0", help="Space-separated class IDs. Default 0 = person")
    save_screenshots = st.number_input("Screenshots", min_value=0, max_value=20, value=5, step=1)

run_btn = st.button("Run tracking", type="primary")


def _parse_classes(s: str) -> list[int] | None:
    s = (s or "").strip()
    if not s:
        return None
    parts = s.split()
    out: list[int] = []
    for p in parts:
        try:
            out.append(int(p))
        except ValueError:
            pass
    return out or None


if run_btn:
    if source_mode == "Upload video" and uploaded is None:
        st.error("Please upload a video file.")
        st.stop()
    if source_mode == "Public URL" and not url.strip():
        st.error("Please paste a public URL.")
        st.stop()

    run_id = uuid4().hex[:8]
    out_dir = Path("outputs") / f"web_{run_id}"

    with st.spinner("Running detection + tracking (this can take a while)..."):
        with tempfile.TemporaryDirectory() as td:
            if source_mode == "Upload video":
                in_path = Path(td) / uploaded.name
                in_path.write_bytes(uploaded.getbuffer())
                source = str(in_path)
            else:
                source = url.strip()

            outputs = run_tracking(
                source=source,
                outputs_dir=out_dir,
                model=model,
                tracker=tracker,
                imgsz=int(imgsz),
                conf=float(conf),
                iou=float(iou),
                classes=_parse_classes(classes_str),
                max_frames=(int(max_frames) if int(max_frames) > 0 else None),
                save_screenshots=int(save_screenshots),
            )

    st.success("Done")

    st.subheader("Outputs")
    st.write(f"Saved to: `{out_dir}`")

    if outputs.annotated_path.exists():
        st.video(outputs.annotated_path.read_bytes())
        st.download_button(
            "Download annotated video",
            data=outputs.annotated_path.read_bytes(),
            file_name="annotated.mp4",
            mime="video/mp4",
        )

    if outputs.tracks_csv.exists():
        st.download_button(
            "Download tracks CSV",
            data=outputs.tracks_csv.read_bytes(),
            file_name="tracks.csv",
            mime="text/csv",
        )

    if outputs.screenshots_dir.exists():
        shots = sorted(outputs.screenshots_dir.glob("*.jpg"))
        if shots:
            st.subheader("Screenshots")
            for p in shots[:6]:
                st.image(str(p), caption=p.name, use_container_width=True)
