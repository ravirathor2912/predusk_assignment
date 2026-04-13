import argparse
from pathlib import Path

from jd_tracker.io import ensure_local_source


def parse_args():
    p = argparse.ArgumentParser(description="Download a public video URL to a local file using yt-dlp")
    p.add_argument("--url", required=True)
    p.add_argument("--out-dir", default="outputs/download")
    return p.parse_args()


def main():
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    local = ensure_local_source(args.url, out_dir)
    print(local)


if __name__ == "__main__":
    main()
