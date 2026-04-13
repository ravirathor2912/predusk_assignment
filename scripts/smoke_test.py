import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)


def main() -> None:
    out_dir = Path("outputs") / "smoke"
    out_dir.mkdir(parents=True, exist_ok=True)

    demo_video = out_dir / "demo.mp4"
    run([sys.executable, "scripts/generate_demo_video.py", "--out", str(demo_video)])

    run_name = "smoke_run"
    run([sys.executable, "track.py", "--source", str(demo_video), "--run-name", run_name, "--max-frames", "120", "--save-screenshots", "3"])  # ~4 seconds

    annotated = Path("outputs") / run_name / "annotated.mp4"
    tracks = Path("outputs") / run_name / "tracks.csv"
    if not annotated.exists() or not tracks.exists():
        raise SystemExit("Smoke test failed: outputs not created")

    print("Smoke test OK")


if __name__ == "__main__":
    main()
