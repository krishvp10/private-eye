# Phase 4 Plan: Generic Agent and Demo Reliability

## Objective

Make the offline demo prove the same property required by the real-VLM path:
the client captures a current safe screen, the model returns one structured
action, and local policy executes it. Demo-specific behavior belongs in
declarative fixtures or the deterministic test oracle, not in the production
agent loop.

## Research basis

The Playwright/vLLM decisions in this phase are based on the official-source
note `private-eye-docs/PLAYWRIGHT_VLLM_RESEARCH.md`:

- Python Playwright 1.62 supports `page.aria_snapshot(mode="ai", boxes=True)`.
- The JSON ARIA snapshot API is JavaScript-only in the researched release line;
  the Python YAML parser is the compatible path.
- vLLM exposes OpenAI-compatible `/v1/chat/completions` and structured output.
- Qwen2.5-VL serving should begin with image-only inputs and an explicit
  `{"image": 2, "video": 0}` multimodal limit.

## Execution order

1. **Configuration boundary** — centralize hosts/ports and preserve legacy
   environment aliases.
2. **Generic oracle** — derive field and post-field control actions from
   `SiteConfig`; never branch on KYC/checkout/patient route names.
3. **Generic fixture** — retain `sample_fixture` as a fourth layout/label
   variation and test it without changing agent/executor code.
4. **One-command supervisor** — validate ports, launch services, poll health,
   open the dashboard, and terminate the process tree on shutdown.
5. **Replay/evidence UI** — retain step history, expose historical endpoints,
   and show only safe metadata across the dashboard transport boundary.
6. **Geometry** — transform source boxes into `object-fit: contain` display
   coordinates and unit-test letterboxing/resizing cases.
7. **Privacy report** — emit JSON/HTML technical evidence without legal or
   compliance claims.
8. **CI/security** — run tests, static quality gates, CodeQL, dependency review,
   and manual mock/real benchmark modes.

## Completion status

The current worktree has completed the non-GPU implementation for all eight
items. The current baseline is 56 passing tests. Real Qwen canaries, five-run
reliability, and model comparison remain explicitly skipped until a reachable
GPU-backed endpoint is supplied.

## Acceptance evidence

- `pytest -q` is the primary regression command.
- `python demo.py --domain sample_fixture --no-browser` is the supervisor smoke
  path; alternate ports can be supplied for parallel local services.
- `eval/reports/privacy_verification_report.{json,html}` are privacy-safe
  evidence artifacts.
- `eval/reports/context_ablation.*`, `real_vlm_canaries.*`, and
  `model_comparison.*` distinguish skipped live runs from measured runs.

## Next phase

Provision and health-check Qwen2.5-VL-3B first. Run canaries, full KYC, five
consecutive workflows, context ablation, packet inspection, then repeat with
7B. Do not start browser extensions, WebGPU, video, or model training before
that evidence exists.
