# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 A-Eye contributors
"""FFmpeg discovery + small helpers.

Prefers a system ``ffmpeg`` on PATH; otherwise falls back to the static binary
bundled by ``imageio-ffmpeg`` — so users don't have to install FFmpeg by hand.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

_DURATION = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")


@lru_cache(maxsize=1)
def ffmpeg_exe() -> str:
    """Path to an ffmpeg binary: system PATH first, then the pip-bundled one."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # imageio-ffmpeg not installed and none on PATH
        raise RuntimeError(
            "FFmpeg not found. Install the media extra (`pip install \"aeye[media]\"`, "
            "which bundles one) or a system FFmpeg (e.g. `winget install Gyan.FFmpeg`)."
        ) from exc


def run_ffmpeg(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run ffmpeg with the given args; output is captured (no console window)."""
    return subprocess.run(
        [ffmpeg_exe(), *args], capture_output=True, text=True, encoding="utf-8", errors="replace"
    )


def probe_duration(path: Path) -> float | None:
    """Seconds of media in ``path``, parsed from ffmpeg's banner (no ffprobe needed)."""
    proc = run_ffmpeg(["-i", str(path)])  # no output file → ffmpeg prints info, exits non-zero
    match = _DURATION.search(proc.stderr or "")
    if not match:
        return None
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
