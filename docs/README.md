# PrivateEye — Privacy-Preserving On-Device Visual Browser Agent

> SIH Problem 26171 · On-device Visual Perception for Light-weight Browser Agents · Dept. of Space / ISRO

## Overview

**PrivateEye** is a privacy-preserving browser agent. A local client (Playwright-driven browser on the
user's machine) captures the screen, **locally detects and redacts sensitive content** (faces, passwords,
Aadhaar/PAN numbers, names, phones, emails), and transmits **only the anonymized visual context + a
structured screen graph** to a central server running an open-weights VLM. The server reasons over the
sanitized context and returns **actionable commands** (click / fill / scroll), which the local client
executes. Sensitive values are resolved **only on the client** — they never traverse the network.

* **Problem**: Server-side agentic AI pipelines require users to ship raw screen data (PII, credentials,
  faces) to the cloud. This blocks adoption for sensitive workflows (banking, KYC, healthcare, government).
* **Solution**: Split the pipeline. Lightweight perception + redaction on the client; heavy reasoning on
  the server; a strict `RedactionMap` contract so the server knows *what it cannot see* and why.
* **Who it is for**: SIH/ISRO evaluation; privacy-conscious end users; any organization that wants LLM
  agents without surrendering raw screen data.

## Features

### MVP (hackathon scope — freeze this)
- Playwright-based local agent (Chromium + Firefox) with capture → redact → send → act loop
- Three PII channels: DOM heuristics (password/autocomplete fields), regex+NER text detection
  (Aadhaar, PAN, phone, email), local face detection (MediaPipe BlazeFace, ONNX)
- Pixel-exact redaction (blackout passwords, blur faces, partial-digit masking) via Playwright bounding boxes
- `ScreenContext` protocol: sanitized JPEG + a11y tree + RedactionMap + URL
- Server: FastAPI + open-weights VLM (Qwen2.5-VL-7B via vLLM, Ollama fallback) returning structured `AgentAction`
- Local value resolution: `fill` commands carry `value_ref`, client fills from a local profile
- Metrics dashboard: latency, CPU/RAM, redaction count, detection precision/recall vs ground truth
- 3 self-built demo sites (login, KYC form with Aadhaar/PAN + live camera-style face image, hospital appointment)

### V1
- MV3 browser extension variant (chrome.tabCapture) with ONNX Runtime Web + WebGPU in-browser inference
- Policy engine: per-category redaction rules (blur vs blackout vs mask), user-configurable
- Multi-step task planner with milestone verification and retry-on-failure
- Prompt-injection filter on returned commands (LLM01 guardrails)

### Future
- Differential-privacy noise on non-sensitive telemetry; federated redaction-model updates
- On-device Screen Parsing (OmniParser-style) to drop server dependence for common tasks
- Audit-grade redaction logs with cryptographic attestation

## Architecture Overview

```
[Local Browser (Playwright)]                 [Server]
 capture: screenshot + a11y tree      ──►     FastAPI /v1/analyze
 detect: DOM + regex/NER + faces              VLM (Qwen2.5-VL-7B, vLLM)
 redact: pixel masking + RedactionMap  ◄──     returns AgentAction JSON
 execute: click/fill/scroll                   (never sees raw PII)
```

See `ARCHITECTURE.md` for full C4-style diagrams (Mermaid).

## Technology Stack

| Layer | Choice | License |
|---|---|---|
| Browser control | Playwright (Python) | Apache-2.0 |
| Local CV | MediaPipe BlazeFace + ONNX Runtime | Apache-2.0 / MIT |
| Text PII | spaCy en_core_web_sm + regex | MIT |
| Server | FastAPI + Uvicorn | MIT |
| VLM serving | vLLM (>=0.7.2) + transformers>=4.49 | Apache-2.0 / Apache-2.0 |
| VLM model | Qwen/Qwen2.5-VL-7B-Instruct (fallback: Ollama) | Apache-2.0 |
| Eval data | MIDV-500, WIDER FACE, self-built synthetic forms | research use |
| Packaging | Docker Compose, pip/uv | — |

## Quick Start (planned)

```bash
git clone <repo> && cd private-eye
uv sync                              # or pip install -r requirements.txt
playwright install chromium firefox
# terminal 1 — server (GPU machine or cloud)
docker compose up server             # vLLM + FastAPI on :8000
# terminal 2 — client (user machine)
python -m client.agent --task "Complete the KYC form on http://localhost:9001/kyc"
# terminal 3 — demo sites + dashboard
docker compose up demo-sites dashboard
```

## Repository Structure

```
private-eye/
├── client/            # capture, redact/, vision, execute, agent loop
├── server/            # FastAPI, vlm.py, prompts.py, schemas.py
├── shared/            # protocol.py — ScreenContext, RedactionMap, AgentAction
├── eval/              # benchmark.py, latency.py, ground-truth fixtures
├── demo_sites/        # fake login / KYC / hospital portals
├── dashboard/         # live metrics (optional)
└── docs/              # this documentation package
```

## Development Status

**Research → Architecture complete · MVP in planning** (as of 2026-09-10)

## Documentation Index

| Doc | Content |
|---|---|
| `PRD.md` | Requirements, user stories, FR/NFR IDs, MVP definition |
| `RESEARCH.md` | Papers + how each shapes our implementation |
| `COMPETITIVE_ANALYSIS.md` | Operator, Computer Use, browser-use, UI-TARS, Skyvern… |
| `OPEN_SOURCE_RESOURCES.md` / `LICENSES.md` | Reusable repos, licenses, risks |
| `TECH_STACK.md` / `ARCHITECTURE.md` / `DESIGN.md` | Decisions, diagrams, UX spec |
| `TRD.md` / `API_SPEC.md` / `DATABASE.md` | Technical + API + data design |
| `SECURITY.md` / `TESTING.md` / `AI_ML.md` | Threat model, test strategy, model/prompt design |
| `DEVOPS.md` / `DEPLOYMENT.md` / `MONITORING.md` / `PERFORMANCE.md` / `SCALABILITY.md` / `ERROR_HANDLING.md` | Ops |
| `FULL_PLAN.md` | Phases + engineering tickets |
| `ADR/` | Architecture Decision Records |
| `RISKS.md` / `ASSUMPTIONS.md` / `OPEN_QUESTIONS.md` | Uncertainty register |
