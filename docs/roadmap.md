# A-Eye — Roadmap

Phased so each stage is runnable before the next begins. Vision and UI are documented up front; code lands incrementally.

## Phase 0 — Foundations ✅ (in progress)
- [x] License (Apache-2.0), NOTICE, README, .gitignore
- [x] Docs: vision, architecture, UI spec, roadmap
- [x] `.claude/` + `CLAUDE.md` for future sessions
- [x] Git init + first push to GitHub
- [ ] `pyproject.toml` / `requirements.txt` skeleton

## Phase 1 — Core pipeline (CLI, headless)
The engine before the interface. Prove video → understanding → answer.
- [ ] `ingest.py` — source resolver: local file passthrough + `yt-dlp` URL download (YouTube/Vimeo/web) with captions/metadata; graceful failure on DRM/gated links
- [ ] `extract.py` — ffmpeg demux, PySceneDetect keyframes, thumbnails + WebVTT, subtitle extraction
- [ ] `transcribe.py` — faster-whisper timestamped transcript
- [ ] `vision.py` — Qwen2.5-VL keyframe captioning + OCR
- [ ] `index.py` — assemble timestamped structured document (+ caching)
- [ ] `chat.py` — single-turn Q&A over the indexed doc with timestamp citations
- [ ] `cli.py` — `aeye analyze <video>` then ask a question

## Phase 2 — Local web app (the UI)
- [ ] FastAPI server: upload/select video **or paste a URL**, stream chat (SSE), serve video + thumbnails
- [ ] "Analyze this link" flow in the prompt input with download/ingest progress
- [ ] React + Vite + Tailwind + shadcn/ui shell (dark + red theme tokens)
- [ ] `SplitPane` (horizontal/vertical, draggable), `VideoView`
- [ ] `TransportBar`: scrubber w/ thumbnail previews, red dial, transport + speed
- [ ] `ChatThread` + floating `PromptInput`
- [ ] **Bidirectional timestamp sync** (clickable citations ⇄ seek)
- [ ] `ChatHistoryRail` with persisted sessions

## Phase 3 — Depth & personas
- [ ] Persona presets (Researcher / Builder / Accessibility / Learner) as system prompts
- [ ] Multi-turn conversation with retrieval for long videos
- [ ] "Ask about this moment" (frame-grounded follow-ups)
- [ ] Chapter summaries / auto-outline

## Phase 4 — Polish & distribution
- [ ] Light theme
- [ ] Settings: model/quant selection, CPU-offload toggle
- [ ] Tauri (or Electron) wrap → native installer
- [ ] Performance pass (indexing speed, VRAM management)
- [ ] Contributor docs, example videos, demo GIF for README

## Backlog / ideas
- Diarization (who's speaking)
- Export analysis (Markdown/PDF) with timestamped citations
- Batch / playlist analysis
- Optional pluggable cloud model for users who want more horsepower
