# MONITORING.md

## Signals
- **Metrics (per step)**: waterfall timings (capture/detect/redact/encode/network/vlm/execute), RSS,
  CPU%, payload bytes, redaction count by category. Sink: SQLite + dashboard strip.
- **Logs**: structured JSON, PII-free by decorator; `run_id` correlation; levels INFO/WARN/ERROR.
- **Traces**: not needed MVP (single request path); waterfall suffices.
- **Health**: `/v1/health` polled every 5 s from dashboard; client degrades to paused if 2 failures.

## Alerts (demo-scale)
- leak-check block fired (critical — show red banner, halt run).
- vlm_ms >5 s twice in a row (warn: switch message or fall back to smaller image).
- client RSS >1.5 GB (warn: memory profile).

## SLOs (for the rubric story)
| SLI | Target |
|---|---|
| step latency p50 | ≤3 s |
| redaction IoU | ≥0.95 |
| outbound leak | 0 |
| demo flow success | ≥90% |
