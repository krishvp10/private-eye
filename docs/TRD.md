# TRD — Technical Requirements Document

## Technical goals
Split-perception architecture: all PII-bearing perception on client; server perceives only sanitized
context; actions grounded client-side; privacy testable by machine.

## System requirements
- Client: Python 3.11, Playwright 1.x (Chromium + Firefox channels pre-installed), ONNX Runtime,
  spaCy en_core_web_sm, 2 cores / 4 GB RAM min.
- Server: Python 3.11, FastAPI, vLLM ≥0.7.2, transformers ≥4.49 (pinned pair), GPU 12 GB+ (AWQ 7B)
  or Ollama fallback on 8 GB.

## API requirements
Single endpoint family `/v1/analyze` (request/response per API_SPEC.md); JSON schema validated both
sides from shared/protocol.py; OpenAPI auto-generated for judges.

## Database requirements
SQLite WAL, 4 tables (runs, steps, redactions, metrics); no PII in any column (NFR-010 enforced by a
logging decorator that scans payloads before write).

## Infrastructure requirements
Docker Compose: server (vLLM+API), demo-sites (nginx), dashboard (vite build, static). TLS optional at
demo via ssh tunnel; production profile adds Caddy with internal CA.

## Security requirements
TB-1 outbound interceptor; vault indirection; action whitelist; schema strictness; see SECURITY.md.

## Performance requirements
NFR-003..NFR-006: ≤300 ms local detect+redact; ≤3 s p50 step; ≤400 KB payload; ≤1.5 GB RSS.

## Integration requirements
Demo sites expose deterministic flows (ids stable, no CAPTCHA, no third-party JS) — part of repo.

## Operational requirements
One-command start; logs PII-free by construction; benchmark runnable offline.

## Development requirements
ruff/mypy clean on shared/ + server/; pytest gates in CI; conventional commits.

## Constraints mapped to PRD
G-1↔FR-010/011 · G-2↔FR-006..008 + NFR-001/002 · G-3↔NFR-004 · G-4↔NFR-006 · G-5↔FR-013.
