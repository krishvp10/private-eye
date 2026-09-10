# FULL_PLAN.md — Implementation Roadmap & Tickets

> Phases sized for a 36–48 h hackathon, 4–6 people. Pre-event week = the real schedule insurance.

## PHASE 0 — Pre-event week (offline, critical)
**Objective:** zero venue-day downloads. **Tasks:** T-000 repo+CI; T-001 pin & freeze server lockfile,
verify Qwen2.5-VL on target GPU (vLLM triangle); T-002 download Playwright browsers, BlazeFace ONNX,
spaCy model, Ollama fallback; T-003 build 3 demo sites; T-004 generate 300-screen labeled corpus;
T-005 MIDV-500 COCO conversion + WIDER FACE val subset local; T-006 write protocol.py + mock server.
**Acceptance:** `PE_MOCK_VLM=1` loop runs end-to-end on a laptop with airplane-mode Wi-Fi.

## PHASE 1 — Kickoff alignment (hours 0–3)
**Objective:** frozen scope. **Tasks:** T-010 team walkthrough of this package; T-011 answer Q-001..003
(ask mentor); T-012 assign owners; T-013 scope freeze sign-off (extension = V1, non-negotiable).
**Acceptance:** one-sentence scope on wall: "KYC flow, benchmarked, masked, demoed."

## PHASE 2 — Client capture (hours 3–8)
**Tasks:** T-020 screenshot+a11y capture pipeline; T-021 screen_graph serialization with node cap;
T-022 DOM heuristic detector; T-023 text extraction + regex/NER detector; T-024 unit tests.
**Deliverable:** `client.capture` dumps context JSON + screenshot. **Acceptance:** FR-001..004 unit-green.

## PHASE 3 — Server skeleton (hours 6–14, parallel)
**Tasks:** T-030 FastAPI + pydantic validation; T-031 action whitelist/guard; T-032 VLM adapter
(mock → vLLM/OpenAI-compatible); T-033 prompt template + JSON repair pass; T-034 /health + /runs.
**Acceptance:** mock-mode full loop; real-VLM spike answers Q-006.

## PHASE 4 — Redaction core (hours 8–18, parallel)
**Tasks:** T-040 masker (blackout/blur/digit-mask) with bbox mapping; T-041 BlazeFace integration;
T-042 RedactionMap builder; T-043 outbound leak-check interceptor; T-044 eval/leak_check.py.
**Acceptance:** FR-005..007 + NFR-001 tests green.

## PHASE 5 — Execution & safety (hours 16–22)
**Tasks:** T-050 execute.py (getByRole/getByLabel/scroll); T-051 value_ref vault resolution;
T-052 destructive-action confirmation gate; T-053 retry/escalation policy (ERROR_HANDLING.md).
**Acceptance:** FR-010/011 e2e-green on demo site 1.

## PHASE 6 — Integration (hours 22–28)
**Tasks:** T-060 wire real VLM; T-061 run J-1 repeatedly, tune prompts/thresholds; T-062 Firefox parity
(Q-004); T-063 latency instrumentation + levers. **Acceptance:** 5/5 consecutive J-1 successes.

## PHASE 7 — Evidence (hours 26–32)
**Tasks:** T-070 benchmark report (P/R/F1, IoU, confusion); T-071 latency percentile report;
T-072 resource dashboard strip; T-073 slides from reports. **Acceptance:** PRD §14 targets met or
honestly reported with mitigations.

## PHASE 8 — Hardening & rehearsal (hours 32–36)
**Tasks:** T-080 chaos passes (kill server mid-run, dead node, VLM gibberish); T-081 5× full rehearsal
timed; T-082 demo-day runbook printed; T-083 freeze `demo-v1.0` tag. **Acceptance:** rehearsal ≤5 min,
zero unexplained failures.

## Engineering tickets (canonical set)

```text
ID: T-000 Type: TASK Pri: P0 "Repo skeleton + CI gates" Deps: — Files: .github/, pyproject.toml
    DoD: ruff/mypy/pytest/leak-grep/IoU gates run on PR.
ID: T-006 Type: FEATURE Pri: P0 "shared/protocol.py schemas" Deps: T-000 DoD: both sides import; fuzz-valid.
ID: T-020 Type: FEATURE Pri: P0 "capture.py screenshot+a11y" Deps: T-006 DoD: FR-001/002.
ID: T-022 Type: FEATURE Pri: P0 "detectors: DOM + regex/NER" Deps: T-020 DoD: FR-003/004 tests.
ID: T-030 Type: FEATURE Pri: P0 "server API + guard" Deps: T-006 DoD: /v1/analyze validates; whitelist.
ID: T-032 Type: FEATURE Pri: P0 "VLM adapter mock+vllm" Deps: T-030 DoD: switchable via env.
ID: T-040 Type: FEATURE Pri: P0 "masker + RedactionMap" Deps: T-022 DoD: FR-006/007; IoU≥0.95 corpus.
ID: T-043 Type: FEATURE Pri: P0 "leak-check interceptor" DeD: blocks send on any unredacted match (NFR-001).
ID: T-050 Type: FEATURE Pri: P0 "execute.py + vault" Deps: T-006 DoD: FR-010; values never serialized.
ID: T-052 Type: FEATURE Pri: P0 "confirmation gate" Deps: T-050 DoD: FR-011 e2e.
ID: T-060 Type: FEATURE Pri: P0 "real VLM integration" Deps: T-030/032/040 DoD: J-1 5/5.
ID: T-070 Type: TASK Pri: P0 "benchmark+latency reports" Deps: T-040 DoD: PRD §14 evidence tables.
ID: T-080 Type: TASK Pri: P1 "chaos + rehearsal" Deps: all P0 DoD: 5× clean, runbook printed.
ID: T-090 Type: SPIKE Pri: P1 "Firefox parity" Deps: T-050 DoD: Q-004 answered.
ID: T-100 Type: RESEARCH Pri: P2 "UI-TARS swap feasibility" Deps: T-060 DoD: one-page verdict (V1).
```

## Phase risk roll-up
P0 fails = schedule slip (mitigate: mock server decouples tracks). P1 slips are absorbed by hour-32 freeze.
