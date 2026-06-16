<div align="center">

<img src="assets/logo.svg" alt="A-Eye" width="280">

# A-Eye

**Watch any video with an AI that actually *sees* it.**

A-Eye is a fully-local tool that analyzes a video **visually, audibly, and through its text/subtitles**, then lets you chat with it — for research, learning, accessibility, reverse-engineering how something was built, or just understanding what a video is really about.

*A play on "AI" and the ability to watch.*

![status](https://img.shields.io/badge/status-pre--alpha-red)
![license](https://img.shields.io/badge/license-Apache--2.0-blue)
![runs-local](https://img.shields.io/badge/runs-100%25%20local-green)

</div>

---

> ⚠️ **Pre-alpha / planning stage.** This repository currently holds the vision, architecture, and UI specification. Code is being built out in phases — see [`docs/roadmap.md`](docs/roadmap.md).

## Why A-Eye?

Plenty of tools can "chat with a video" — but almost all of them are **cloud-based and transcript-only**. They read the captions and ignore the actual pixels. A-Eye is different:

- **It watches the pixels**, not just the transcript — on-screen text, UI, slides, charts, scenes.
- **It runs 100% locally.** Your videos never leave your machine.
- **It fuses three signals** — vision + audio + text/subtitles — into one timestamped understanding you can question.

### Who it's for

- 🔬 **Researchers** digging deeper into topics, visuals, or ideas in a video.
- 🛠️ **Builders** asking "how would I make my own version of this?"
- 🧓 **Accessibility / plain-language** users who want a patient explainer.
- 🎓 **Learners** turning any video into an interactive tutor.

## How it works

A-Eye turns a video into a rich, timestamped document, then chats over it:

```
video ──▶ extract        ──▶ transcribe     ──▶ see            ──▶ index            ──▶ chat
         (ffmpeg +           (faster-whisper)   (Qwen2.5-VL:        (timestamped        (ask anything,
          scene detect,                          captions + OCR      structured doc)     answers cite
          keyframes,                             over keyframes)                         timestamps)
          thumbnails)
```

Models load and unload **sequentially** so the whole pipeline fits on a single consumer GPU. Full design in [`docs/architecture.md`](docs/architecture.md).

## Quickstart

> Not runnable yet — this is the intended workflow once Phase 1 lands.

```bash
# 1. Backend (Python)
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Pull local models (via Ollama)
ollama pull qwen2.5-vl:7b

# 3. Run the local web app
python -m aeye serve            # opens http://localhost:8000
```

## Requirements

| Component | Minimum | Notes |
|-----------|---------|-------|
| GPU       | ~8 GB VRAM (e.g. RTX 3060/3080) | Pipeline is designed around a 10 GB card |
| RAM       | 16 GB (32 GB recommended) | Headroom for CPU offload |
| Disk      | ~15 GB for models | Weights pulled at runtime, never committed |
| Tools     | FFmpeg, Python 3.11+, Node 20+, Ollama | Cross-platform |

## Documentation

- [`docs/vision.md`](docs/vision.md) — what A-Eye is and who it serves
- [`docs/architecture.md`](docs/architecture.md) — the pipeline, models, and stack
- [`docs/ui-spec.md`](docs/ui-spec.md) — the interface design and theme
- [`docs/roadmap.md`](docs/roadmap.md) — phased build plan

## Contributing

Early days — issues and ideas welcome. By contributing you agree your work is licensed under Apache-2.0.

## License

[Apache License 2.0](LICENSE). A-Eye orchestrates third-party models at runtime under their own licenses and does not redistribute their weights — see [`NOTICE`](NOTICE).
