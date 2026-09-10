# TESTING.md

## Strategy by layer
| Layer | Tool | Scope |
|---|---|---|
| Unit | pytest | detectors, masker geometry, protocol validation, whitelist filter |
| Integration | pytest + Playwright test | capture→redact→payload; server mock returns action; execution on demo sites |
| API | pytest + httpx | /v1/analyze schema accept/reject, error codes, size limits |
| E2E | pytest-playwright scripted flows | J-1 KYC flow completes; confirmation gate fires on Submit |
| Benchmark (metric evidence) | eval/benchmark.py | PII P/R/F1 vs 300-screen synthetic corpus; face/doc channels vs MIDV-500 subset & WIDER FACE val; redaction IoU; latency percentiles; leak-check |
| Security | CI: pip-audit, leak-grep, schema fuzz (hypothesis) | supply chain, log hygiene, validation robustness |
| Visual regression | pixelmatch on masked outputs | redaction precision ≥95% IoU gate |

## Test data
- `eval/corpus/` synthetic labeled screens (generated pre-event; ground-truth JSON sidecars).
- MIDV-500 frames (COCO-converted) + WIDER FACE validation subset — local only, never redistributed.

## Coverage & CI gates
- ≥80% on client/redact + server guard modules; benchmarks run on every PR to main (CPU-only; VLM in mock).
- CI fails on: leak-grep hit, pip-audit critical, redaction-IoU <0.95 on corpus, KYC E2E failure.

## Traceability matrix (excerpt)
| Req | Test | Expected |
|---|---|---|
| FR-003 | test_detect_password_autocomplete | flags all `type=password` fields |
| FR-006 | test_masker_iou_corpus | IoU ≥0.95 vs ground truth |
| NFR-001 | eval/leak_check.py | zero unredacted PII in outbound bytes |
| FR-011 | e2e_kyc_submit_gate | modal appears; no submit before approve |
| NFR-004 | eval/latency.py report | p50 ≤3 s over 50 runs |
