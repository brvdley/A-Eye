# A-Eye — Roadmap

Phased so each stage is runnable before the next begins. Vision and UI are documented up front; code lands incrementally.

## Phase 0 — Foundations ✅ (in progress)
- [x] License (Apache-2.0), NOTICE, README, .gitignore
- [x] Docs: vision, architecture, UI spec, roadmap
- [x] `.claude/` + `CLAUDE.md` for future sessions
- [x] Git init + first push to GitHub
- [ ] `pyproject.toml` / `requirements.txt` skeleton

## Phase 1 — Core pipeline (CLI, headless) ✅
The engine before the interface. Prove video → understanding → answer. **Done — runs fully local end-to-end.**
- [x] `ingest.py` — source resolver: local file passthrough + `yt-dlp` URL download (YouTube/Vimeo/web) with captions/metadata; graceful failure on DRM/gated links
- [x] `extract.py` — ffmpeg (system or bundled) audio + scene-detect keyframes (interval fallback) + sidecar subtitle parsing
- [x] `transcribe.py` — faster-whisper timestamped transcript (GPU→CPU fallback)
- [x] `providers/` — provider interface for the See/Chat stages, with the local `OllamaProvider` first (cloud providers come in Phase 3)
- [x] `vision.py` — keyframe captioning + OCR via the provider interface
- [x] `index.py` — assemble timestamped structured document (+ save/load cache)
- [x] `chat.py` — single-turn Q&A over the indexed doc with timestamp citations
- [x] `cli.py` — `aeye ask <video> "<question>"` (+ `ingest`/`extract`/`transcribe`)
- [ ] Scrubber thumbnails (sprite + WebVTT) — deferred to Phase 2 (UI asset, not needed for analysis)

## Phase 2 — Local web app (the UI)
- [ ] FastAPI server: upload/select video **or paste a URL**, stream chat (SSE), serve video + thumbnails
- [ ] "Analyze this link" flow in the prompt input with download/ingest progress
- [ ] React + Vite + Tailwind + shadcn/ui shell (dark + red theme tokens)
- [ ] `SplitPane` (horizontal/vertical, draggable), `VideoView`
- [ ] `TransportBar`: scrubber w/ thumbnail previews, red dial, transport + speed
- [ ] `ChatThread` + floating `PromptInput`
- [ ] **Bidirectional timestamp sync** (clickable citations ⇄ seek)
- [ ] `ChatHistoryRail` with persisted sessions

## Phase 3 — Depth, personas & cloud providers
- [ ] BYOK cloud providers: `AnthropicProvider` (Claude) + `OpenAIProvider` (GPT) behind the provider interface; key stored backend-side, never committed/logged
- [ ] Settings UI for keys + per-role provider selection (local vs cloud); clear "cloud" badge when active
- [ ] Persona presets (Researcher / Builder / Accessibility / Learner) as system prompts
- [ ] **Mode chips** above the input: persona single-select + capability toggles, with the gradient/glow/white-border styling (see ui-spec)
- [ ] **Deep Reasoning** capability (cloud: adaptive thinking + higher effort, surfaced; local: deliberate pass)
- [ ] **Web Search** capability (cloud: provider server-side search w/ citations) — research beyond the video
- [ ] Multi-turn conversation with retrieval for long videos
- [ ] "Ask about this moment" (frame-grounded follow-ups)
- [ ] Chapter summaries / auto-outline

## Phase 4 — Polish & distribution
- [ ] Light theme
- [ ] Settings: model/quant selection, CPU-offload toggle
- [ ] Tauri (or Electron) wrap → native installer
- [ ] Performance pass (indexing speed, VRAM management)
- [ ] GPU acceleration for faster-whisper (cuBLAS + cuDNN for CUDA 12; currently falls back to CPU when absent)
- [ ] Contributor docs, example videos, demo GIF for README

## Backlog / ideas
- Local Web Search backend (e.g. SearXNG / search API) so the capability works without a cloud key
- Diarization (who's speaking)
- Export analysis (Markdown/PDF) with timestamped citations
- Batch / playlist analysis
- Optional pluggable cloud model for users who want more horsepower
