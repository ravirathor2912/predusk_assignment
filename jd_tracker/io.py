from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse


def _is_url(source: str) -> bool:
    try:
        u = urlparse(source)
        return u.scheme in {"http", "https"} and bool(u.netloc)
    except Exception:
        return False


def ensure_local_source(source: str, outputs_dir: Path) -> Path:
    """Return a local file path for the video source.

    This project expects a **local video file** path.
    If you have a public video link, download it first and pass the local file.
    """

    src_path = Path(source)
    if src_path.exists():
        return src_path

    if _is_url(source):
        raise RuntimeError(
            "Source is a URL. Download the video locally first and pass the local file path to --source."
        )

    raise FileNotFoundError(f"Source not found: {source}")
