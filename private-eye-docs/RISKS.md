# RISKS.md — Register

| ID | Risk | Prob | Impact | Severity | Mitigation | Owner | Trigger |
|---|---|---|---|---|---|---|---|
| R-01 | Venue Wi-Fi blocks model pulls / HF | High | High | Critical | Pre-download everything incl. Playwright browsers, vLLM image, model weights; bring offline wheels | DevOps | 1 week before event |
| R-02 | vLLM/transformers version drift breaks Qwen2.5-VL | Med | High | High | Pin vLLM≥0.7.2 + transformers 4.49.x + flash-attn in lockfile; test on target GPU before event; Ollama fallback ready | Server | CI fail / first deploy |
| R-03 | No GPU available at venue | Med | High | High | Ollama q4 fallback on any 8 GB GPU laptop; final fallback: mock-VLM scripted demo + recorded real run | Server | hardware survey day 0 |
| R-04 | Demo site flow changes / dynamic ads break selectors | Low | Med | Med | We self-host static demo sites; Playwright getByRole is layout-independent | Agent | e2e CI |
| R-05 | PII recall below target on unseen eval screens | Med | High | High | Over-mask bias; ensemble 3 channels; threshold tuning on corpus the night before; report honest F1 | Privacy | benchmark report |
| R-06 | e2e latency >3 s p50 | Med | Med | Med | Optimization levers (PERFORMANCE.md §2); pre-warmed server; smaller image as demo-day knob | Server | latency report |
| R-07 | Face detector misses at odd angles/lighting | Med | Med | Med | BlazeFace + YuNet ensemble; synthetic face images included in corpus tuning | Privacy | benchmark face recall |
| R-08 | AGPL contamination via Ultralytics/OmniParser weights | Low | Med | Med | Ban ultralytics import; only OmniParser v3 MIT weights; license gate in CI | All | LICENSES audit |
| R-09 | VLM chooses wrong element on live stage | Med | Med | Med | Post-condition checks + retry; keep flows deterministic; rehearse 5× | Agent | rehearsal |
| R-10 | Scope creep to extension/WebGPU | High | Med | Med | Extension is explicitly V1; PM enforces freeze (FULL_PLAN hour 0 checkpoint) | PM | any "what if we also…" |
| R-11 | Time lost on dashboard polish | Med | Low | Low | Dashboard is P1; metrics strip is the only mandatory piece | Demo | hour 24 checkpoint |
| R-12 | Team laptop sleep/thermal throttle mid-demo | Low | Med | Med | Plugged-in, power settings locked, spare laptop imaged | DevOps | rehearsal |
