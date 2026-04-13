from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from yt_dlp import YoutubeDL


def _is_url(source: str) -> bool:
    try:
        u = urlparse(source)
        return u.scheme in {"http", "https"} and bool(u.netloc)
    except Exception:
        return False


def ensure_local_source(source: str, outputs_dir: Path) -> Path:
    """Return a local file path for the video source.

    - If `source` is a local path, returns it.
    - If `source` is a URL, tries to download with yt-dlp into outputs_dir.

    Raises a RuntimeError if the download fails.
    """

    src_path = Path(source)
    if src_path.exists():
        return src_path

    if not _is_url(source):
        raise FileNotFoundError(f"Source not found: {source}")

    outputs_dir.mkdir(parents=True, exist_ok=True)
    outtmpl = str(outputs_dir / "source.%(ext)s")

    ydl_opts = {
        "outtmpl": outtmpl,
        "format": "mp4/best",
        "quiet": True,
        "noplaylist": True,
        "retries": 3,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(source, download=True)
            downloaded = ydl.prepare_filename(info)
            return Path(downloaded)
    except Exception as e:
        raise RuntimeError(
            "Failed to download video from URL. If this is a streaming site, install ffmpeg or download the video manually and pass a local file path."
        ) from e
