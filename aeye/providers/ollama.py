# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 A-Eye contributors
"""Local provider backed by Ollama (the default; no API key, nothing leaves the machine)."""
from __future__ import annotations

import base64
import json
from collections.abc import Iterator
from pathlib import Path

import httpx

from .base import ChatMessage, Provider


class OllamaProvider(Provider):
    name = "ollama"

    def __init__(
        self,
        host: str = "http://localhost:11434",
        vision_model: str = "qwen2.5vl:7b",
        chat_model: str = "qwen2.5vl:7b",
        timeout: float = 600.0,
    ) -> None:
        self.host = host.rstrip("/")
        self.vision_model = vision_model
        self.chat_model = chat_model
        self.timeout = timeout

    def caption(self, image_path: Path, prompt: str) -> str:
        image_b64 = base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
        payload = {
            "model": self.vision_model,
            "messages": [{"role": "user", "content": prompt, "images": [image_b64]}],
            "stream": False,
        }
        resp = httpx.post(f"{self.host}/api/chat", json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        stream: bool = True,
        deep_reasoning: bool = False,
        web_search: bool = False,
    ) -> Iterator[str]:
        # Local Ollama can't do server-side web search; the capability is a no-op
        # here (the UI gates it — see docs/providers.md). deep_reasoning could later
        # map to a reasoning-tuned local model or larger num_predict.
        payload: dict = {"model": self.chat_model, "messages": messages, "stream": stream}
        if not stream:
            resp = httpx.post(f"{self.host}/api/chat", json=payload, timeout=self.timeout)
            resp.raise_for_status()
            yield resp.json()["message"]["content"]
            return
        with httpx.stream(
            "POST", f"{self.host}/api/chat", json=payload, timeout=self.timeout
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                chunk = data.get("message", {}).get("content", "")
                if chunk:
                    yield chunk
                if data.get("done"):
                    break
