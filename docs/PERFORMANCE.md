# PERFORMANCE.md — Budgets & Measurement

| Budget | Target | How measured |
|---|---|---|
| Local detect+redact | ≤300 ms/frame @1280×800 | eval/latency.py, psutil, ONNX profiling |
| Step e2e p50 / p95 | ≤3 s / ≤6 s | waterfall sums over ≥50 runs |
| Payload | ≤400 KB | len(image_b64) at encode |
| Client RSS / CPU | ≤1.5 GB / ≤2 cores | psutil sampler thread |
| Server VLM TTFT+gen | ≤2.5 s typical step | vLLM metrics, 1.5k-token prompt |
| Startup (cold) | ≤10 min client / ≤15 min server | deployment checklist timing |

## Optimization levers (ranked)
1. JPEG q70 + downscale to 1280px (10× size win, tiny accuracy cost for layout).
2. Re-run detection only on DOM-mutation frames (content-hash of a11y tree).
3. a11y-tree capping (400 interactive nodes) — biggest prompt-token saver.
4. AWQ 4-bit server weights; `enforce_eager=False` for CUDA graphs; prefix caching across steps of a run.
5. BlazeFace on downscaled (640px) side-image, boxes scaled back up.
6. Skip frames entirely if a11y tree + pixels both unchanged.

## Measurement honesty
Report medians AND p95; run evals on battery vs plugged-in; state laptop spec next to every number in the report.
