# CLAUDE.md — A-Eye

Context for Claude Code sessions working on this repo. Read this first.

## What this project is

**A-Eye** ("AI" + the ability to watch) is a **fully-local** tool that analyzes a video
**visually, audibly, and via text/subtitles**, then lets the user chat with an AI about it
— for research, learning, accessibility, or reverse-engineering how something was built.

Differentiator vs. existing "chat with video" tools: A-Eye **watches the pixels** (on-screen
text, UI, slides, scenes), not just the transcript, and runs **100% locally**.

Full detail in [`docs/vision.md`](docs/vision.md). **Keep docs in sync with reality** as code lands.

## Hard constraints

- **Target GPU: ~10 GB VRAM** (dev machine: RTX 3080 10 GB / Ryzen 7 3700X 8c/16t / 32 GB RAM, Windows 11).
  Models **must not co-reside** — the pipeline loads/unloads stages sequentially. Don't propose
  designs that assume a big multi-model resident footprint.
- **Open source, Apache-2.0.** Never commit model weights or large media — they're gitignored
  (`models/`, `*.gguf`, `*.safetensors`, `cache/`, `data/`). Pull models at runtime via Ollama.
- **Cross-platform.** Dev is on Windows/PowerShell, but most users run Linux/Mac. Use `pathlib`,
  no hardcoded `\` paths, configurable Ollama host/model.

## Architecture (the pipeline)

`ingest → extract → transcribe → see → index → chat` — see [`docs/architecture.md`](docs/architecture.md).

- **ingest** — source resolver. Local file passthrough, or **`yt-dlp`** to download a pasted **URL** (YouTube/Vimeo/1000+ sites) locally, plus platform captions/metadata. ToS/copyright is the user's responsibility; never bypass DRM. Fail gracefully on gated links.
- **extract** — ffmpeg + PySceneDetect: keyframes, scrubber thumbnails (sprite + WebVTT), audio, subs.
- **transcribe** — faster-whisper (large-v3-turbo), timestamped.
- **see** — Qwen2.5-VL-7B (Apache-2.0): keyframe captions + OCR.
- **index** — assemble one timestamped structured doc (cached per video).
- **chat** — Q&A over the doc; answers cite timestamps. Qwen2.5-VL can be both "see" and "chat".

**Providers (local-first, cloud-optional).** See/Chat go through `aeye/providers/`: `OllamaProvider` (local, default) or, with a user key (**BYOK**), `AnthropicProvider` (Claude) / `OpenAIProvider` (GPT) — both multimodal. Default is 100% local; cloud is opt-in and sends frames+transcript to the provider. **Key rules: backend-only, never in the frontend, never committed (`.env*` gitignored), never logged.** Current Claude IDs: `claude-opus-4-8` (default cloud pick), `claude-sonnet-4-6`, `claude-haiku-4-5`, `claude-fable-5`. Full detail: [`docs/providers.md`](docs/providers.md). When writing Claude code, consult the claude-api skill (stream responses; pass frames as image blocks).

## Stack

- Backend: **Python 3.11+ / FastAPI**. Models via **Ollama**. Media via **FFmpeg + PySceneDetect**. URL ingest via **yt-dlp**.
- Frontend: **React + Vite + TailwindCSS + shadcn/ui**, Framer Motion, Lucide.
- Packaging: **local web app now** (FastAPI serves the React build at localhost) → Tauri/Electron later.

## UI essentials

Dark theme, **red accent** (`--accent: #E5392F`) tied to the scrub dial. Layout: collapsible
chat-history rail · resizable split (video ⇄ chat, horizontal/vertical) · global transport bar
(scrubber w/ thumbnail previews, red dial, transport + speed) · floating rounded prompt input.
**Signature interaction: bidirectional timestamp sync** — clickable citation chips ⇄ video seek.
Full spec: [`docs/ui-spec.md`](docs/ui-spec.md).

## Current status

**Pre-alpha / Phase 0.** Planning artifacts exist (license, docs, this file). No app code yet.
Build order is in [`docs/roadmap.md`](docs/roadmap.md) — **Phase 1 = the CLI pipeline, headless,
before any UI.** Don't jump to the frontend before the engine works.

## Working conventions

- Update the relevant `docs/*.md` and the roadmap checkboxes when you ship something.
- Apache-2.0 license header on new source files.
- Keep the README quickstart honest about what actually runs.
- Prefer small, runnable increments over large speculative scaffolds.
