# A-Eye — UI Specification

Goal: a **modern, sleek interface that feels like a contemporary AI app**, purpose-built around video. Dark-first, cinematic, with a single red accent that ties to the scrub dial.

## Layout

```
┌──────────┬───────────────────────────────────────────────────────┐
│          │   ┌───────────────────┬───────────────────────────┐    │
│  Chat    │   │                   │                           │    │
│ history  │   │    Video view     │     AI discussion         │    │  ← MAIN SPLIT
│          │   │                   │     (scrollable thread)   │    │    user toggles
│ (collap- │   │                   │                           │    │    horizontal /
│  sible   │   │                   │                           │    │    vertical;
│  rail)   │   └───────────────────┴───────────────────────────┘    │    draggable
│          │   ╞═══◉ thumbs ════════🔴════════ timestamps ═══════╡    │    divider
│          │      ⏮  ◀◀   ▶   ▶▶  ⏭        1.0× ▾                     │  ← TRANSPORT BAR
│          │          ╭───────────────────────────────────╮         │
│          │          │  Ask about this video…          ↑ │         │  ← INPUT (floating,
│          │          ╰───────────────────────────────────╯         │    rounded, centered)
└──────────┴───────────────────────────────────────────────────────┘
```

### 1. Left rail — chat history
- Collapsible. Expanded: list of past sessions (each tied to a video) with title + thumbnail. Collapsed: thin icon rail.
- Top: "New analysis" button. Bottom: settings, persona preset, theme toggle.

### 2. Main area — resizable split
- Two panes: **Video view** and **AI discussion**.
- User chooses **horizontal or vertical** split; divider is **draggable** to resize.
- Layout preference persists per session.

### 3. Transport bar (full-width, above input)
Global video controls, spanning both panes:
- **Scrubber** with **thumbnail previews on hover** and **timestamp labels** (thumbnails come from the extract stage as a sprite + WebVTT map — see [architecture.md](architecture.md)).
- **Red scrub dial** (◉) — the signature accent element; draggable playhead.
- **Transport buttons (right):** rewind ◀◀, play/pause ▶, fast-forward ▶▶ (and ⏮/⏭ to jump scenes/keyframes).
- **Playback speed** control (e.g. 0.5× – 2×) via a dropdown/segmented control.

> **Decision noted:** the transport bar is *global* (full-width) rather than attached to the video pane. This keeps controls consistent regardless of split orientation. Alternative (scrubber docked inside the video pane) is recorded but not chosen.

### 4. Input box (floating, centered)
- Rounded, floating "pill" spanning the bottom, centered.
- Placeholder reflects context: *"Ask about this video…"*.
- Send button + attach (load video) affordance; supports multi-line + streaming responses.
- **Two ways to load a video:** drop/attach a local file, **or paste a video URL** (YouTube/Vimeo/web). When the input detects a pasted link with no video loaded yet, it switches to an "Analyze this link" action and shows download/ingest progress (resolved via `yt-dlp` — see [architecture.md](architecture.md)).

## Signature interaction — bidirectional timestamp sync

This is A-Eye's defining behavior, not a nice-to-have:

- **Chat → video:** every timestamp the AI mentions renders as a **clickable chip**; clicking **seeks the video** to that moment.
- **Video → chat:** the current playhead position is referenceable — e.g. an "Ask about this moment" action injects the current timestamp/frame into the prompt ("what's happening *here*?").
- Active citations can subtly highlight on the scrubber.

## Theme tokens — Dark, cinematic red accent

| Token | Value | Use |
|-------|-------|-----|
| `--bg` | `#0A0A0B` | App canvas (near-black) |
| `--surface-1` | `#141416` | Panels, rail |
| `--surface-2` | `#1C1C1F` | Cards, input pill |
| `--border` | `#2A2A2E` | Dividers, outlines |
| `--text` | `#EDEDED` | Primary text |
| `--text-muted` | `#A1A1AA` | Secondary text |
| `--accent` | `#E5392F` | Red — scrub dial, primary actions, citations |
| `--accent-hover` | `#FF4438` | Hover/active red |
| `--success` | `#3FB950` | Status (ready/indexed) |
| `--radius` | `14px` | Rounded corners (input pill larger) |

- **Dark-first.** A light theme is deferred (roadmap), built on the same tokens.
- Generous spacing, soft shadows, subtle borders. Motion via **Framer Motion** (pane resize, message entrance, scrubber hover).

## Component inventory (build order hints)

- `AppShell` (rail + main + bottom dock)
- `ChatHistoryRail`
- `SplitPane` (orientation toggle + drag resize)
- `VideoView` (player surface)
- `TransportBar` → `Scrubber` (thumb previews, red dial), `TransportControls`, `SpeedControl`
- `ChatThread` → `Message`, `TimestampChip` (clickable seek)
- `PromptInput` (floating pill)
- `PersonaSwitcher`, `ThemeToggle`

## Accessibility

- Keyboard: space = play/pause, ←/→ = seek, [/] = speed, `/` = focus input.
- Respect `prefers-reduced-motion`. Maintain AA contrast on the red accent (use for fills/icons, not body text).
