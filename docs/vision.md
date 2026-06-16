# A-Eye — Vision

## One-line

A-Eye lets you load any video and have a conversation with an AI that has **watched it** — seeing the pixels, hearing the audio, and reading the text — entirely on your own machine.

## The problem

"Chat with a video" already exists, but today's tools share two limits:

1. **They're cloud-based.** Your video (which may be private, sensitive, or simply large) is uploaded to someone else's servers.
2. **They're transcript-only.** They feed the captions to an LLM and ignore the *visuals* — the on-screen UI, the slides, the diagrams, the demo someone is performing. For a huge class of videos (tutorials, software demos, lectures with whiteboards, product walkthroughs), the transcript is only half the story.

## The A-Eye difference

A-Eye **actually watches the video** and does it **locally**:

- **Visual** — samples scene-change keyframes and runs a vision-language model to caption what's happening and read on-screen text (OCR).
- **Audible** — transcribes speech with timestamps.
- **Textual** — pulls embedded subtitles when present.

These three streams are fused into a single **timestamped understanding** the user can interrogate. Answers cite the moment they came from, and clicking a citation jumps the video there.

## Who it's for (personas)

These are **system-prompt presets over one engine**, not separate products:

| Persona | What they want | How A-Eye serves it |
|---------|----------------|---------------------|
| **Researcher** | Go deeper on topics, visuals, claims | Cross-references transcript + on-screen detail; surfaces and expands ideas |
| **Builder** | "How do I make my own version of this?" | Reads the tool/UI shown, infers stack and steps, drafts a build plan |
| **Accessibility / plain-language** | Patient, clear explanation | Calm tone, defines jargon, summarizes at the user's pace |
| **Learner** | Turn a video into a tutor | Q&A, quizzes, chapter summaries, "explain this part" |

## What A-Eye is *not* (for now)

- Not real-time / live-stream analysis. It indexes a video first, then chat is instant.
- Not frame-perfect. It samples keyframes, so sub-second visual events between samples can be missed.
- Not a cloud service. No accounts, no upload, no telemetry.

## Guiding principles

1. **Local-first and private by default.** Nothing leaves the machine.
2. **It watches, it doesn't just read.** Visuals are first-class.
3. **Every answer is grounded.** Cite timestamps; make them clickable.
4. **Runs on a real person's GPU.** Designed around a 10 GB consumer card, not a datacenter.
5. **Open and forkable.** Apache-2.0, no bundled weights, cross-platform.
