# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 A-Eye contributors
"""The provider interface shared by local and cloud backends."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path
from typing import TypedDict


class ChatMessage(TypedDict):
    role: str  # "system" | "user" | "assistant"
    content: str


class Provider(ABC):
    """A backend for the See (vision) and Chat (reasoning) stages.

    Capabilities (``deep_reasoning``, ``web_search``) are accepted by every
    provider; a backend that can't honor one ignores it (e.g. local web search
    isn't wired yet). See docs/providers.md and docs/ui-spec.md (mode chips).
    """

    name: str

    @abstractmethod
    def caption(self, image_path: Path, prompt: str) -> str:
        """See stage: describe a keyframe and read any on-screen text (OCR)."""

    @abstractmethod
    def chat(
        self,
        messages: list[ChatMessage],
        *,
        stream: bool = True,
        deep_reasoning: bool = False,
        web_search: bool = False,
    ) -> Iterator[str]:
        """Chat stage: yield the answer as text chunks (streamed when ``stream``)."""
