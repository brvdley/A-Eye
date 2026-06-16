# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 A-Eye contributors
"""Runtime configuration, loaded from the environment (``AEYE_*``) with sane defaults.

Cloud API keys are read from the standard provider env vars (``ANTHROPIC_API_KEY`` /
``OPENAI_API_KEY``) and are never written to disk by A-Eye. See docs/providers.md.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AEYE_", env_file=".env", extra="ignore")

    # Where A-Eye stores downloaded videos, frames/thumbnails, and cached indexes.
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".aeye")

    # Local model serving (Ollama) — the default provider.
    ollama_host: str = "http://localhost:11434"
    vision_model: str = "qwen2.5vl:7b"
    chat_model: str = "qwen2.5vl:7b"

    # Transcription (faster-whisper).
    whisper_model: str = "large-v3-turbo"

    # Extract stage: keyframe sampling. Scene cuts drive keyframes; when few/none
    # are found, fall back to one frame every ``keyframe_interval`` seconds.
    keyframe_interval: float = 5.0
    max_keyframes: int = 80

    # Provider selection per role: "ollama" (local) | "anthropic" | "openai".
    vision_provider: str = "ollama"
    chat_provider: str = "ollama"

    # Cloud keys (BYOK) — read from the standard env vars, not the AEYE_ prefix.
    anthropic_api_key: str | None = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")

    # Optional: pull cookies from a browser for sites that gate anonymous access
    # (e.g. YouTube anti-bot). One of: chrome, edge, firefox, brave, ... (see yt-dlp).
    cookies_from_browser: str | None = None

    @property
    def videos_dir(self) -> Path:
        return self.data_dir / "videos"

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / "cache"

    def ensure_dirs(self) -> None:
        for d in (self.data_dir, self.videos_dir, self.cache_dir):
            d.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
