# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 A-Eye contributors
"""The shared data model: the timestamped structured document A-Eye builds per video.

Stages add to this incrementally — ingest sets ``source``; extract adds ``keyframes``
and ``subtitles``; transcribe adds ``transcript``; see (vision) adds ``captions``.
"""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class VideoSource(BaseModel):
    """A local, analyzable video — the output of the ingest stage."""

    path: Path  # local file on disk (always set after ingest)
    source_url: str | None = None  # original URL, if ingested from a link
    title: str | None = None
    description: str | None = None
    duration: float | None = None  # seconds, if known
    extra: dict = Field(default_factory=dict)


class TranscriptSegment(BaseModel):
    start: float  # seconds
    end: float
    text: str


class Keyframe(BaseModel):
    index: int
    timestamp: float  # seconds into the video
    image_path: Path


class Caption(BaseModel):
    timestamp: float
    description: str  # what the vision model sees at this keyframe
    ocr_text: str | None = None  # on-screen text, if any


class Extraction(BaseModel):
    """Artifacts produced by the extract stage (audio + keyframes + sidecar subs)."""

    workdir: Path
    audio_path: Path
    duration: float | None = None
    keyframes: list[Keyframe] = Field(default_factory=list)
    subtitles: list[TranscriptSegment] = Field(default_factory=list)


class IndexedVideo(BaseModel):
    """The cached, timestamped understanding the chat stage answers over."""

    source: VideoSource
    transcript: list[TranscriptSegment] = Field(default_factory=list)
    keyframes: list[Keyframe] = Field(default_factory=list)
    captions: list[Caption] = Field(default_factory=list)
    subtitles: list[TranscriptSegment] = Field(default_factory=list)  # embedded/platform subs
