# A-Eye — Architecture

## Design constraint that drives everything

A-Eye targets a **single consumer GPU with ~10 GB of VRAM** (reference machine: RTX 3080 10 GB / Ryzen 7 3700X / 32 GB RAM). You cannot hold a large video model + an audio model + a chat model resident at once. So A-Eye is a **pipeline of stages that load and unload sequentially**, not one monolithic model.

The pipeline runs **once per video** (the "index" pass) to produce a compact, timestamped document. Chat then operates over that cached document, keeping only the chat-capable model resident — so conversation is fast.

**Input is a local file *or* a pasted URL.** A leading **ingest** stage resolves a YouTube/Vimeo/web link to a local file with `yt-dlp`; everything downstream is identical regardless of source.

## Pipeline

```
┌──────────┐   ┌───────────┐   ┌─────────────┐   ┌─────────────┐   ┌──────────┐   ┌────────┐
│  INGEST  │──▶│  EXTRACT  │──▶│ TRANSCRIBE  │──▶│     SEE     │──▶│  INDEX   │──▶│  CHAT  │
└──────────┘   └───────────┘   └─────────────┘   └─────────────┘   └──────────┘   └────────┘
 yt-dlp /        ffmpeg          faster-whisper     Qwen2.5-VL-7B     assemble        Qwen2.5-VL
 local file      PySceneDetect   large-v3-turbo     captions + OCR    structured      (or text LLM)
 → local .mp4    keyframes,      timestamps         on keyframes      timestamped     over cached
 + platform      thumbnails,     + embedded subs                      doc + embeds    doc
   captions/      audio demux
   metadata
   net/CPU          CPU            ~2–4 GB VRAM       ~6–8 GB VRAM      CPU             ~6–8 GB VRAM
```

### Stages

0. **Ingest** (`aeye/ingest.py`) — source resolver, net/CPU.
   - **Local file:** used as-is.
   - **URL** (YouTube, Vimeo, 1000+ sites): downloaded locally with `yt-dlp`. Also fetches **platform captions** and **metadata** (title, description, chapters) when available — extra text signal for the Index stage.
   - Fails gracefully on DRM-protected / geo- or age-gated links that can't be retrieved.
   - **ToS/copyright:** downloading is the user's responsibility; A-Eye doesn't bypass DRM. See [`NOTICE`](../NOTICE).

1. **Extract** (`aeye/extract.py`) — CPU only.
   - Demux audio for transcription.
   - Detect scene changes (PySceneDetect) and pull representative **keyframes** instead of blind fixed-interval sampling.
   - Generate **scrubber thumbnails** + a WebVTT timestamp map (reused by the UI, see [ui-spec.md](ui-spec.md)).
   - Extract embedded subtitle tracks if present.

2. **Transcribe** (`aeye/transcribe.py`) — `faster-whisper`, `large-v3-turbo`.
   - Speech → timestamped text segments. Frees VRAM when done.

3. **See** (`aeye/vision.py`) — Qwen2.5-VL-7B (Apache-2.0).
   - Caption each keyframe; OCR on-screen text (UI, slides, code, signs).
   - Strong OCR + sequence understanding is exactly why this model was chosen.

4. **Index** (`aeye/index.py`) — CPU.
   - Merge transcript + captions + OCR + subtitles + platform metadata into one **timestamped structured document**.
   - Optionally embed chunks for retrieval on long videos.

5. **Chat** (`aeye/chat.py`).
   - The user prompts against the indexed document. Answers cite timestamps.
   - **Qwen2.5-VL can serve as both the "See" and "Chat" model** — it reasons over visuals and text — collapsing the model count and letting chat re-inspect specific frames on demand.

## VRAM budget (10 GB reference card)

| Stage | Model | Approx VRAM | Resident with chat? |
|-------|-------|-------------|---------------------|
| Transcribe | faster-whisper large-v3-turbo | 2–4 GB | No (load/unload) |
| See | Qwen2.5-VL-7B (AWQ/GGUF quant) | 6–8 GB | — |
| Chat | Qwen2.5-VL-7B / 7–8B text LLM | 6–8 GB | Yes, only this |

With 32 GB system RAM there's headroom to spill a larger (14B) model partly to CPU for higher-quality reasoning at reduced speed — a configurable option, not the default.

## Tech stack

| Layer | Choice | Why |
|-------|--------|-----|
| Backend | **Python + FastAPI** | Whisper, Qwen-VL, ffmpeg orchestration live in Python |
| Model serving | **Ollama** (primary) / vLLM (optional) | Easy local pulls; weights never committed |
| Media | **FFmpeg** + **PySceneDetect** | Demux, keyframes, thumbnails |
| Sources | **yt-dlp** | Resolve YouTube/Vimeo/web links to local files (+ captions, metadata) |
| Frontend | **React + Vite + TailwindCSS + shadcn/ui** | Modern, sleek AI-app UI |
| Motion / icons | **Framer Motion**, **Lucide** | Polished transitions |
| Packaging | **Local web app now** (FastAPI serves the React build at `localhost`) → **Tauri/Electron wrap later** | Fast iteration first; native installer when proven |

## Data flow at runtime

```
Browser (React UI)  ⇄  FastAPI  ⇄  Pipeline stages  ⇄  Ollama (local models)
        │                  │
        │                  └── serves /video, /thumbnails, /transcript, /chat (SSE stream)
        └── timestamped chat ⇄ scrubber (bidirectional seek)
```

## Repository layout (intended)

```
aeye/
├── aeye/                 # Python backend package
│   ├── ingest.py         # yt-dlp URL resolver / local-file source
│   ├── extract.py        # ffmpeg + scene detect + thumbnails
│   ├── transcribe.py     # faster-whisper
│   ├── vision.py         # Qwen2.5-VL captioning + OCR
│   ├── index.py          # assemble timestamped doc
│   ├── chat.py           # Q&A over the cached doc
│   └── server.py         # FastAPI app
├── frontend/             # React + Vite + Tailwind + shadcn/ui
├── docs/                 # this folder
├── .claude/              # guidance for Claude Code sessions
├── CLAUDE.md             # auto-loaded project context
├── LICENSE  NOTICE  README.md
```

## Open questions (track here)

- Long-video strategy: full-context vs. embedding retrieval threshold.
- Whether to expose model/quant choice in the UI or config-only.
- Caching/versioning of the indexed document so re-opening a video is instant.
