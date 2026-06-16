# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 A-Eye contributors
"""Transcribe stage: audio.wav -> timestamped transcript via faster-whisper.

Prefers the GPU (float16); falls back to CPU (int8) when CUDA libraries aren't
available. The model is loaded once and cached. See docs/architecture.md.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from .config import Settings, get_settings
from .models import TranscriptSegment


# GPU first, then CPU. NOTE: ctranslate2 loads CUDA libraries lazily at inference
# time (not at construction), so the fallback has to wrap the actual transcription.
# GPU needs cuBLAS + cuDNN for CUDA 12 on PATH; without them we transcribe on CPU.
_DEVICES = (("cuda", "float16"), ("cpu", "int8"))


@lru_cache(maxsize=2)
def _load_model(name: str, device: str, compute_type: str):
    from faster_whisper import WhisperModel  # lazy — heavy import

    return WhisperModel(name, device=device, compute_type=compute_type)


def transcribe(audio_path: Path, settings: Settings | None = None) -> list[TranscriptSegment]:
    """Return timestamped transcript segments for a 16 kHz mono ``audio.wav``."""
    settings = settings or get_settings()
    last_error: Exception | None = None
    for device, compute_type in _DEVICES:
        try:
            model = _load_model(settings.whisper_model, device, compute_type)
            # Iterating the generator is where decode (and any CUDA load) happens,
            # so force evaluation inside the try to trigger the CPU fallback.
            segments, _info = model.transcribe(str(audio_path), vad_filter=True)
            return [
                TranscriptSegment(start=seg.start, end=seg.end, text=seg.text.strip())
                for seg in segments
                if seg.text.strip()
            ]
        except Exception as exc:  # missing CUDA libs, etc. → try the next device
            last_error = exc
    raise RuntimeError(f"Transcription failed on all devices: {last_error}")
