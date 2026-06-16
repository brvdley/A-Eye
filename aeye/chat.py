# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 A-Eye contributors
"""Chat stage: answer a prompt over the indexed video, streaming the response.

Capabilities (``deep_reasoning``, ``web_search``) map to the mode chips in the UI
and are passed through to the provider. See docs/providers.md and docs/ui-spec.md.
"""
from __future__ import annotations

from collections.abc import Iterator

from .config import Settings, get_settings
from .index import render_context
from .models import IndexedVideo
from .providers import Provider, build_provider

SYSTEM_PROMPT = (
    "You are A-Eye, an assistant that has watched a video. You are given a "
    "timestamped context built from the video's visuals (keyframe descriptions + "
    "on-screen text) and its transcript. Answer the user's question using that "
    "context. Cite moments with timestamps in [mm:ss] form when relevant. If the "
    "answer isn't supported by the video, say so plainly rather than guessing."
)


def ask(
    index: IndexedVideo,
    question: str,
    settings: Settings | None = None,
    provider: Provider | None = None,
    *,
    deep_reasoning: bool = False,
    web_search: bool = False,
) -> Iterator[str]:
    """Stream the answer to ``question`` grounded in ``index``."""
    settings = settings or get_settings()
    provider = provider or build_provider(settings.chat_provider, settings)

    context = render_context(index)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"VIDEO CONTEXT:\n{context}\n\nQUESTION: {question}"},
    ]
    yield from provider.chat(
        messages, stream=True, deep_reasoning=deep_reasoning, web_search=web_search
    )
