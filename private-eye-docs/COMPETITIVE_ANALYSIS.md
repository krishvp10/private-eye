# COMPETITIVE ANALYSIS

| Product | Strengths | Weaknesses | Tech | Pricing | Users | Differentiator |
|---|---|---|---|---|---|---|
| OpenAI Operator (Computer-Using Agent) | Strong reasoning; polished UX | Closed; screenshots (incl. PII) go to OpenAI; $200/mo tier | Proprietary GPT-4o-class CUA | $200/mo | Consumers | None available to us |
| Anthropic Computer Use | Good safety refusals; API | Closed; raw screen to Anthropic | Claude 3.5/3.7 + tools | API $/token | Devs | None |
| browser-use (OSS, MIT, ~114k stars) | Easy API; any LLM incl. local; huge community | Sends raw DOM/screens to LLM — no privacy layer; no redaction | Python + Playwright | Free + cloud credits | Devs | **Market gap we fill: privacy layer** |
| UI-TARS / Agent TARS (ByteDance, Apache-2.0) | SOTA open GUI agent; native grounding | Heavy; screenshots (faces/PII) go to chosen endpoint; no redaction | 7B VLM + desktop app | Free model | Researchers | We add verifiable redaction + local value resolution |
| OmniParser (Microsoft, MIT w/ caveat) | Excellent pure-vision screen parsing | Perception only; output unredacted; no agent loop | YOLOv9 + Florence-2 | Free | Researchers | We constrain it to local inference + redaction (V1) |
| Skyvern (OSS) | Document-heavy automation workflows | Visual+DOM to LLM unredacted; automation not agentic-assist | YOLO + LLM | OSS + cloud | Enterprises | Privacy boundary again |
| SeeAct (research) | Rigorous plan→ground methodology | Research code; GPT-4V-dependent (data leaves) | GPT-4V + Playwright | — | Research | Our a11y-grounding + redaction contract operationalizes it |

## What to copy conceptually
- browser-use's element-index → action ergonomics (we use a11y-role targeting instead, more robust).
- SeeAct's strict separation of *planning* (LLM) and *grounding/execution* (client) — the exact split
  our privacy model requires.
- UI-TARS's insight that 7B VLMs suffice for GUI grounding → keeps our server cheap and offline-deployable.

## What to avoid
- Sending raw DOM innerText wholesale (browser-use default) — defeats the privacy purpose.
- Pixel-coordinate actions from the server (fragile, resolution-dependent); always a11y-role targets.
- Rigid workflow scripts (Skyvern-style) — we want task-level instructions, not fixed paths.

## Where the opportunity is
**Nobody ships a machine-verifiable privacy contract.** Every competitor says "trust us" or "run it
locally" (weak models). PrivateEye's `RedactionMap` + `eval/leak_check.py` turns privacy into a
*testable property* — that's the slide judges remember.

## What makes this project significantly better
1. Verifiable privacy (leak-check re-scans the outbound image).
2. India-specific PII (Aadhaar/PAN) — no OSS competitor handles this.
3. Grounding solved client-side (a11y), so a smaller/cheaper server VLM suffices → lower latency (metric 5).
