# ADR-0002: Qwen2.5-VL-7B-Instruct on vLLM as server model
Status: Accepted (2026-09-10)
Context: Need open-weights VLM with strong document/GUI understanding, vLLM-servable, permissive license.
Decision: Qwen2.5-VL-7B-Instruct, Apache-2.0, AWQ 4-bit; pin vLLM≥0.7.2 + transformers 4.49.x
(verified compatibility triangle); Ollama q4 fallback.
Alternatives: Qwen3-VL (newer — EXPERIMENT REQUIRED before adopting at event), UI-TARS-1.5-7B
(GUI-tuned but narrower instructions — V1 candidate), InternVL2.5-8B (heavier), hosted GPT-4o
(violates open-weights constraint).
Consequences: 12 GB VRAM server; deterministic JSON prompting; known-good docs.
Risks: version drift (lockfile + pre-event verification).
Migration: adapter pattern in server/vlm.py — swap model name/env.
