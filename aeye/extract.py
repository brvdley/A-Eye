# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 A-Eye contributors
"""Extract stage: turn a local video into the raw material the AI stages need.

Produces, under ``<cache>/<key>/``:
  - ``audio.wav``       — 16 kHz mono, for faster-whisper (transcribe stage)
  - ``keyframes/*.jpg`` — scene-change frames (interval fallback when few/no cuts)
and parses any sidecar subtitles yt-dlp wrote (platform captions).

CPU only; uses FFmpeg (see media.py) and PySceneDetect. See docs/architecture.md.
"""
from __future__ import annotations

import re
from pathlib import Path

from .config import Settings, get_settings
from .media import probe_duration, run_ffmpeg
from .models import Extraction, Keyframe, TranscriptSegment, VideoSource


def extract(source: VideoSource, settings: Settings | None = None) -> Extraction:
    """Run the extract stage for an ingested video."""
    settings = settings or get_settings()
    settings.ensure_dirs()

    workdir = _workdir(source, settings)
    duration = source.duration or probe_duration(source.path)
    audio_path = _extract_audio(source.path, workdir)
    keyframes = _extract_keyframes(source.path, workdir, duration, settings)
    subtitles = _load_sidecar_subtitles(source)

    return Extraction(
        workdir=workdir,
        audio_path=audio_path,
        duration=duration,
        keyframes=keyframes,
        subtitles=subtitles,
    )


def _workdir(source: VideoSource, settings: Settings) -> Path:
    key = (source.extra or {}).get("id") or source.path.stem
    workdir = settings.cache_dir / str(key)
    (workdir / "keyframes").mkdir(parents=True, exist_ok=True)
    return workdir


def _extract_audio(video: Path, workdir: Path) -> Path:
    out = workdir / "audio.wav"
    proc = run_ffmpeg(["-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(out)])
    if proc.returncode != 0 or not out.exists():
        raise RuntimeError(f"Audio extraction failed:\n{(proc.stderr or '')[-600:]}")
    return out


def _keyframe_timestamps(video: Path, duration: float | None, settings: Settings) -> list[float]:
    """Scene-cut midpoints; fall back to an even interval grid when there are none."""
    times: list[float] = []
    try:
        from scenedetect import ContentDetector, detect

        scenes = detect(str(video), ContentDetector())
        times = [(start.get_seconds() + end.get_seconds()) / 2 for start, end in scenes]
    except Exception:
        times = []  # any backend hiccup → fall through to the interval grid

    if not times:
        if duration and duration > 0:
            iv = settings.keyframe_interval
            count = max(1, int(duration // iv))
            last = max(duration - 0.05, 0.0)
            times = [min(iv / 2 + k * iv, last) for k in range(count)]
        else:
            times = [0.0]

    times = sorted({round(t, 2) for t in times if t >= 0})
    if len(times) > settings.max_keyframes:
        step = len(times) / settings.max_keyframes
        times = [times[int(i * step)] for i in range(settings.max_keyframes)]
    return times


def _extract_keyframes(
    video: Path, workdir: Path, duration: float | None, settings: Settings
) -> list[Keyframe]:
    kdir = workdir / "keyframes"
    frames: list[Keyframe] = []
    for index, ts in enumerate(_keyframe_timestamps(video, duration, settings)):
        out = kdir / f"frame_{index:04d}.jpg"
        # -ss before -i is a fast keyframe-accurate seek.
        run_ffmpeg(["-y", "-ss", f"{ts:.3f}", "-i", str(video), "-frames:v", "1", "-q:v", "3", str(out)])
        if out.exists():
            frames.append(Keyframe(index=index, timestamp=ts, image_path=out))
    return frames


# --- sidecar subtitles (platform captions written by yt-dlp) ---------------

_CUE = re.compile(
    r"(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})"
)
_TAG = re.compile(r"<[^>]+>")


def _hms(stamp: str) -> float:
    hours, minutes, seconds = stamp.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def _parse_vtt(path: Path) -> list[TranscriptSegment]:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    segments: list[TranscriptSegment] = []
    i = 0
    while i < len(lines):
        cue = _CUE.search(lines[i])
        if not cue:
            i += 1
            continue
        start, end = _hms(cue.group(1)), _hms(cue.group(2))
        i += 1
        text_lines: list[str] = []
        while i < len(lines) and lines[i].strip():
            text_lines.append(_TAG.sub("", lines[i]).strip())
            i += 1
        text = " ".join(t for t in text_lines if t)
        if text:
            segments.append(TranscriptSegment(start=start, end=end, text=text))
    return segments


def _load_sidecar_subtitles(source: VideoSource) -> list[TranscriptSegment]:
    for vtt in sorted(source.path.parent.glob(f"{source.path.stem}*.vtt")):
        segments = _parse_vtt(vtt)
        if segments:
            return segments
    return []
