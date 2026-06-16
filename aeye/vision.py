# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 A-Eye contributors
"""See stage: caption each keyframe and read its on-screen text, via a provider.

Local by default (Ollama + a vision model); the same provider interface lets a
cloud model (Claude/GPT) serve this stage when configured. See docs/providers.md.
"""
from __future__ import annotations

from .config import Settings, get_settings
from .models import Caption, Keyframe
from .providers import Provider, build_provider

CAPTION_PROMPT = (
    "You are analyzing a single frame from a video. In 1-2 sentences, describe "
    "what is shown. Then, if there is any on-screen text (UI, slides, captions, "
    "signs), transcribe it verbatim after 'TEXT:'. If there is none, omit TEXT."
)


def see(
    keyframes: list[Keyframe],
    settings: Settings | None = None,
    provider: Provider | None = None,
) -> list[Caption]:
    """Caption every keyframe; returns one Caption per frame, in order."""
    settings = settings or get_settings()
    provider = provider or build_provider(settings.vision_provider, settings)

    captions: list[Caption] = []
    for frame in keyframes:
        description = provider.caption(frame.image_path, CAPTION_PROMPT).strip()
        captions.append(Caption(timestamp=frame.timestamp, description=description))
    return captions
