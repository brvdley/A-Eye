# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 A-Eye contributors
"""Model providers for the See (vision) and Chat (reasoning) stages.

Local-first: ``OllamaProvider`` is the default and needs no key. Optional BYOK
cloud providers (Anthropic, OpenAI) plug in behind the same interface — they land
in Phase 3. See docs/providers.md.
"""
from __future__ import annotations

from ..config import Settings
from .base import ChatMessage, Provider
from .ollama import OllamaProvider

__all__ = ["ChatMessage", "Provider", "OllamaProvider", "build_provider"]


def build_provider(name: str, settings: Settings) -> Provider:
    """Construct the provider for a role ("ollama" | "anthropic" | "openai")."""
    if name == "ollama":
        return OllamaProvider(
            host=settings.ollama_host,
            vision_model=settings.vision_model,
            chat_model=settings.chat_model,
        )
    if name in ("anthropic", "openai"):
        raise NotImplementedError(
            f"The {name!r} cloud provider lands in Phase 3 — see docs/providers.md."
        )
    raise ValueError(f"Unknown provider: {name!r}")
