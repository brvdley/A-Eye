# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 A-Eye contributors
"""Ingest stage: resolve a local file or a URL into a local ``VideoSource``.

URLs (YouTube, Vimeo, 1000+ sites) are downloaded locally with yt-dlp, along with
platform captions/metadata when available. Downloading is the user's responsibility
under each platform's ToS; A-Eye does not bypass DRM. See docs/architecture.md.
"""
from __future__ import annotations

from pathlib import Path

from .config import Settings, get_settings
from .models import VideoSource

_VIDEO_EXTS = {".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v"}


def _is_url(source: str) -> bool:
    return source.startswith(("http://", "https://"))


def ingest(source: str, settings: Settings | None = None) -> VideoSource:
    """Return a local, analyzable video for ``source`` (a file path or a URL)."""
    settings = settings or get_settings()
    settings.ensure_dirs()

    if not _is_url(source):
        path = Path(source).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"No such file: {path}")
        if not path.is_file():
            raise ValueError(f"Not a file: {path}")
        return VideoSource(path=path, title=path.stem)

    return _download(source, settings)


def _download(url: str, settings: Settings) -> VideoSource:
    from yt_dlp import YoutubeDL  # lazy import — keeps the rest of the package light

    opts = {
        "outtmpl": str(settings.videos_dir / "%(id)s.%(ext)s"),
        # "best" prefers a single progressive stream (no ffmpeg needed to merge).
        # With ffmpeg installed, "bv*+ba" yields higher quality.
        "format": "best/bv*+ba",
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en.*"],
        "noplaylist": True,
        "quiet": True,
        "noprogress": True,
    }
    # Some sites (notably YouTube) gate anonymous access behind anti-bot checks;
    # pulling cookies from a logged-in browser is the usual fix. Opt-in via config.
    if settings.cookies_from_browser:
        opts["cookiesfrombrowser"] = (settings.cookies_from_browser,)
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = Path(ydl.prepare_filename(info))
    except Exception as exc:  # DRM, geo/age gating, network, unsupported site
        raise RuntimeError(
            f"Could not download {url!r}: {exc}. The link may be DRM-protected, "
            "private, or region/age-restricted."
        ) from exc

    # The merged/remuxed output can land at a different extension than predicted.
    if not path.exists():
        candidates = sorted(settings.videos_dir.glob(f"{info['id']}.*"))
        path = next((c for c in candidates if c.suffix.lower() in _VIDEO_EXTS), path)

    return VideoSource(
        path=path,
        source_url=url,
        title=info.get("title"),
        description=info.get("description"),
        duration=info.get("duration"),
        extra={"id": info.get("id"), "uploader": info.get("uploader")},
    )
