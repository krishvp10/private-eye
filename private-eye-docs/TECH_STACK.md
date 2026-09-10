# TECH_STACK.md — Decisions & Rationale

## Frontend / Client
*Decision:* Python 3.11 + Playwright (Chromium primary, Firefox secondary).
*Why:* a11y snapshot API is the only browser API giving role/name/value trees — our grounding layer and
PII-detection signal; first-class Firefox support satisfies the problem statement; SeeAct's own harness
uses Playwright. *Alternatives rejected:* Selenium (a11y weak, verbose), Puppeteer (Firefox immature),
MV3 extension + chrome.tabCapture (defers WebGPU model plumbing we don't have time to derisk — moved to V1).
*Cost:* free. *Complexity:* low. *Risk:* Playwright's bundled browsers need pre-install at venue (mitigate: pre-download).

## Local CV / inference
*Decision:* ONNX Runtime (CPU) + MediaPipe BlazeFace (ONNX port) + spaCy sm model + compiled regexes.
*Why:* zero-GPU client keeps the demo laptop-friendly; ONNX INT8 keeps ≤300 ms/frame; all licenses
Apache/MIT. *Rejected:* Ultralytics YOLO (AGPL-3.0 — see LICENSES.md), in-browser Transformers.js/WebGPU
(V1 — derisking), heavier face models (resources metric).
*Migration path:* swap BlazeFace→OmniParser-v3 screen parsing in V1 behind the same interface.

## Server framework
*Decision:* FastAPI + Uvicorn, pydantic v2 schemas shared with client via `shared/protocol.py`.
*Why:* async request handling for image payloads; pydantic gives strict validation (NFR-008) and code-gen
of the contract both sides import. *Rejected:* Flask (sync, weaker validation ergonomics), gRPC
(overkill for one endpoint at hackathon scale; reconsider at 100+ concurrent agents).

## Server VLM
*Decision:* Qwen2.5-VL-7B-Instruct on vLLM (AWQ 4-bit if VRAM <16 GB), OpenAI-compatible chat endpoint,
JSON-mode structured outputs.
*Why:* Apache-2.0; best-in-class document/GUI understanding among 7B open models; vLLM ≥0.7.2 +
transformers ≥4.49 pinned (verified version triangle); falls back to Ollama (`qwen2.5vl:7b`) on a
single consumer GPU.
*Alternatives rejected:* GPT-4o-class APIs (violates offline/open-weights requirement), LLaVA-1.6 (weaker
document/UI OCR), InternVL2.5-8B (heavier, marginal gain), UI-TARS-1.5-7B (excellent GUI grounding but
weaker instruction diversity; V1 experiment). *Risk:* vLLM/transformers drift → lock `requirements-server.txt`.

## Database
*Decision:* SQLite (WAL) for run logs, steps, redactions, metrics.
*Why:* zero-ops, single-file, sufficient for MVP evals; audit log = table. *Rejected:* Postgres
(no multi-writer need), no-DB JSONL (loses queryability for the benchmark report).

## Eval
*Decision:* pytest + custom eval harness; labeled synthetic corpus generated pre-event; MIDV-500 (COCO
converted) + WIDER FACE subsets for face/doc channels.
*Why:* rubric metrics 1–3 must be evidence-backed; synthetic corpus gives exact ground truth for
India-specific PII that no public dataset provides.

## Developer tooling
uv (or pip+venv) · ruff (lint+format) · mypy (protocol module) · pytest · pre-commit · conventional commits.
