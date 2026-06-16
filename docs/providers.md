# A-Eye — Model Providers (local-first, cloud-optional)

A-Eye is **local-first**: out of the box it runs entirely on your machine with no
account and no API key. But the two stages that use an LLM — **See** (frame
captioning + OCR) and **Chat** (reasoning over the indexed video) — are routed
through a **provider abstraction**, so a user can optionally plug in their own
**Claude or GPT API key (BYOK — "bring your own key")** to route those stages to
a frontier model.

This matters because the local pipeline is capped by a ~10 GB GPU (see
[architecture.md](architecture.md)). A frontier multimodal model can give far
deeper analysis — and since **Claude and GPT are multimodal**, a cloud key can
serve *both* the See and Chat stages, collapsing the local pipeline to just
ffmpeg + Whisper.

## The contract: default local, cloud is opt-in

| | Default (local) | Cloud (opt-in, BYOK) |
|---|---|---|
| See / Chat models | Ollama (Qwen2.5-VL-7B) | Claude or GPT via the user's key |
| Where data goes | Nothing leaves the machine | Frames + transcript + your prompt are sent to the provider's API |
| Account / key | None | User supplies their own API key |
| Cost | Free (your electricity) | Billed to the user's provider account |

**Privacy is the headline trade-off.** Enabling a cloud provider means the
sampled keyframes, the transcript, and your prompts are transmitted to that
provider for the See/Chat stages. The UI must make this explicit (a clear "cloud"
badge when a non-local provider is active). Audio extraction and transcription
stay local regardless; only the LLM stages are swappable.

## Provider abstraction

A small interface (`aeye/providers/`) with one implementation per backend:

- `OllamaProvider` — local, the default. No key.
- `AnthropicProvider` — Claude (multimodal + streaming).
- `OpenAIProvider` — GPT (multimodal + streaming).

Providers are selectable **per role**, so a user can keep vision local and route
only the heavy reasoning to Claude, or send both to the cloud. The Extract and
Transcribe stages never go through a provider — they're always local.

## Capabilities (Deep Reasoning, Web Search)

Two optional capabilities, exposed as **mode chips** by the input box (see
[ui-spec.md](ui-spec.md) → Mode chips), are also routed through the provider:

| Capability | Cloud (Claude / GPT) | Local (Ollama) |
|------------|----------------------|----------------|
| **Deep Reasoning** | Adaptive thinking at higher **effort**, with the reasoning summary surfaced. Trades latency + tokens for depth. | A slower, more deliberate pass (or a reasoning-tuned local model) — quality capped by the 10 GB GPU. |
| **Web Search** | The provider's **server-side web-search tool** — Claude/GPT search the web and return cited results. Lets answers go *beyond* the video to research the topics/visuals/claims it mentions. | Pluggable search backend (e.g. SearXNG / a search API) — a later enhancement, not in the first cut. |

**Privacy for Web Search:** it sends queries off the machine (to the provider or
a search backend), so it's gated like any other cloud feature — off by default,
clearly flagged when on. Deep Reasoning on a cloud provider inherits the same
data-leaves-the-machine contract as the rest of the cloud path.

## Claude (Anthropic) options

Claude models are multimodal (accept images, so they can caption keyframes) and
support streaming responses (SSE) for the chat loop — the same streaming UX as
the local path. Current model IDs and pricing (input / output per 1M tokens):

| Model | Model ID | Context | Price (in / out) | Use for |
|-------|----------|---------|------------------|---------|
| Claude Opus 4.8 | `claude-opus-4-8` | 1M | $5 / $25 | **Default cloud pick** — best analysis quality |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 1M | $3 / $15 | Cheaper, faster, still multimodal |
| Claude Haiku 4.5 | `claude-haiku-4-5` | 200K | $1 / $5 | Cheapest; quick/simple questions |
| Claude Fable 5 | `claude-fable-5` | 1M | $10 / $50 | Most capable; hardest analyses |

Implementation notes for when this lands (Phase 3): use the official `anthropic`
SDK, **stream** chat responses, and pass keyframes as image blocks for the See
stage. (OpenAI/GPT is the parallel path via the `openai` SDK.)

## Key security — non-negotiable

- **Keys live in the Python backend only.** The React frontend never sees a key;
  it talks to the local FastAPI server, which holds the key and calls the
  provider. A key must never be shipped to the browser.
- **Never committed.** Keys go in a local `.env` / config file that is
  `.gitignore`'d (already covered by `.env*` in [`.gitignore`](../.gitignore)).
  An OS keyring is a better store and a likely later enhancement.
- **Never logged.** Don't print keys or echo them in errors/telemetry (A-Eye has
  no telemetry anyway).
- Keys leave the machine only as the `Authorization` header to the provider's
  own API endpoint — nowhere else.

## How this reconciles with "local-first and private by default"

It doesn't weaken the principle — it preserves it as the **default**. A-Eye ships
fully local; cloud is an explicit, clearly-flagged opt-in for users who want more
power and accept that their video data goes to a third party under that
provider's terms. See [vision.md](vision.md) → Guiding principles.
