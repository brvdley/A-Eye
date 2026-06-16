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
│          │     (Research)(Build)(Plain)(Learn) ┊ (Reason)(Search)  │  ← MODE CHIPS
│          │          ╭───────────────────────────────────╮         │    (glow + white border)
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

### 5. Mode chips (above the input)

A row of small, glowing **pill chips** sits just above the input. They set *how*
A-Eye answers the next prompt. Two groups, separated by a thin divider (`┊`):

- **Persona presets — single-select** (pick one, or none = default). Each is a
  system-prompt preset (see [vision.md](vision.md) → personas):
  *Researcher · Builder · Plain-language · Learner.*
- **Capabilities — independent toggles** (stack freely):
  *Deep Reasoning · Web Search.* These lean on provider features — see
  [providers.md](providers.md) and [architecture.md](architecture.md):
  - **Deep Reasoning** — spend more thinking on the answer (cloud: adaptive
    thinking at higher effort, with the reasoning surfaced; local: a slower,
    more deliberate pass). Trades latency/cost for depth.
  - **Web Search** — let the answer go *beyond* the video to research topics,
    visuals, or claims it mentions (cloud: the provider's server-side search
    tool with citations; local: a pluggable search backend, later). **Note:**
    this sends queries off-machine, so it's gated like any cloud feature.

#### Chip styling — outline at rest, fills + glows when active

Each chip is a rounded-full pill that lives in **two states**, with a smooth
transition between them:

- **Idle (unselected):** **transparent** — the dark UI shows straight through.
  Only a **1px outline in the chip's hue** and a **label in that same hue**. No
  fill, no glow (or the faintest hint). Reads as a colored ghost button.
- **Active (selected):** the pill **fills with its gradient**, the **label
  crossfades to white** (legible on the bright fill), a **soft outer glow** in the
  hue ramps up, and a **thin white-ish border** appears so the filled pill pops
  against the dark canvas.

**The click transition is the moment.** On select (~180–220ms `ease-out`): the
gradient fill grows in (opacity + subtle scale), the glow fades up, the outline
warms from hue → white, and the text color crossfades hue → white. Deselect
reverses it. `prefers-reduced-motion` → instant state swap, no ramp/pulse.

| Chip | Hue | Gradient fill (from → to) | Outline + idle text | Glow (active) |
|------|-----|----------------------------|---------------------|---------------|
| Researcher | Blue | `#60A5FA → #3B82F6` | `#60A5FA` | `#3B82F6` |
| Builder | Orange | `#FB923C → #F97316` | `#FB923C` | `#F97316` |
| Plain-language | Green | `#34D399 → #10B981` | `#34D399` | `#10B981` |
| Learner | Purple | `#C084FC → #A855F7` | `#C084FC` | `#A855F7` |
| Deep Reasoning | Rose/Red | `#FF6B6B → #EF4444` | `#FF6B6B` | `#EF4444` |
| Web Search | Cyan | `#22D3EE → #06B6D4` | `#22D3EE` | `#06B6D4` |

Shared tokens:
- Idle: `background: transparent` · `border: 1px solid <hue>` · `color: <hue>` · no shadow.
- Active: gradient `<from> → <to>` fill · `color: #FFFFFF` · `border: 1px solid rgba(255,255,255,0.85)` · `box-shadow: 0 0 14px <glow>66, 0 0 4px <glow>40`.
- Hover (idle): nudge the outline/text toward the brighter `from` hue and add a faint `0 0 6px <glow>33` glow as an affordance.
- Radius: full pill · small label, optional leading icon.

> **Decision to confirm:** Deep Reasoning uses a **rose/red** gradient (`#EF4444`),
> deliberately a touch off the brand scrub-dial red (`#E5392F`) so the two don't
> read as the same thing. If you'd rather keep red exclusively for the brand /
> transport, Deep Reasoning can move to **amber** (`#F59E0B`) and Web Search stays
> cyan. Flagging it rather than silently overloading red.

> **Provider gating:** when a capability needs a provider the current setup can't
> serve well (e.g. Web Search, or high-quality Deep Reasoning on a local-only
> setup), the chip shows a subtle "needs a model/key" hint rather than failing
> mid-answer. See [providers.md](providers.md).

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
- `ModeChipBar` → `ModeChip` (gradient + glow + white border; persona single-select group + capability toggles)
- `PromptInput` (floating pill)
- `ThemeToggle`

## Accessibility

- Keyboard: space = play/pause, ←/→ = seek, [/] = speed, `/` = focus input.
- Respect `prefers-reduced-motion`. Maintain AA contrast on the red accent (use for fills/icons, not body text).
