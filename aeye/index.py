# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 A-Eye contributors
"""Index stage: merge the stage outputs into one timestamped document.

``build_index`` assembles the ``IndexedVideo``; ``render_context`` flattens it
into the compact, timestamped text the chat stage reasons over. See
docs/architecture.md.
"""
from __future__ import annotations

from pathlib import Path

from .models import Caption, Extraction, IndexedVideo, TranscriptSegment, VideoSource


def _ts(seconds: float) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def build_index(
    source: VideoSource,
    extraction: Extraction,
    transcript: list[TranscriptSegment],
    captions: list[Caption],
) -> IndexedVideo:
    return IndexedVideo(
        source=source,
        transcript=transcript,
        keyframes=extraction.keyframes,
        captions=captions,
        subtitles=extraction.subtitles,
    )


def render_context(index: IndexedVideo) -> str:
    """Flatten the index into a timestamped text document for the chat prompt."""
    src = index.source
    lines: list[str] = []

    if src.title:
        lines.append(f"TITLE: {src.title}")
    if src.duration:
        lines.append(f"DURATION: {_ts(src.duration)}")
    if src.source_url:
        lines.append(f"SOURCE: {src.source_url}")

    if index.captions:
        lines.append("\nVISUAL (what is on screen, by timestamp):")
        for cap in index.captions:
            lines.append(f"[{_ts(cap.timestamp)}] {cap.description}")

    spoken = index.transcript or index.subtitles
    if spoken:
        label = "TRANSCRIPT" if index.transcript else "SUBTITLES"
        lines.append(f"\n{label} (spoken/caption text, by timestamp):")
        for seg in spoken:
            lines.append(f"[{_ts(seg.start)}] {seg.text}")

    if not index.captions and not spoken:
        lines.append("\n(No visual captions or transcript were produced for this video.)")

    return "\n".join(lines)


def save_index(index: IndexedVideo, path: Path) -> None:
    path.write_text(index.model_dump_json(indent=2), encoding="utf-8")


def load_index(path: Path) -> IndexedVideo:
    return IndexedVideo.model_validate_json(path.read_text(encoding="utf-8"))
