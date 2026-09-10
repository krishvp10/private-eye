# ASSUMPTIONS.md

| ID | Assumption | Why | Evidence | Confidence | Invalidates if | Verify |
|---|---|---|---|---|---|---|
| A-001 | Judges accept a locally-running Playwright agent as the "client-side component" | Problem says client extension/JS in Chrome/Firefox; Playwright controls those browsers locally and SeeAct's reference harness does the same | SeeAct paper (Playwright online eval); problem statement wording | Medium | Judges require literal MV3 extension | Ask mentor/org 1 week out; extension shell is our V1 hedge |
| A-002 | One LAN GPU machine (12 GB+) or equivalent cloud is available at finale | Server VLM needs it | SIH allows cloud-hosted OSS during finale | Medium | No GPU + no internet → R-03 fallback | Hardware survey with organizers |
| A-003 | Synthetic PII (generated names/IDs) is acceptable for demos & benchmarks | Real Aadhaar/PAN cannot be used (legal) | DPDP Act; MIDV uses synthetic/public-domain docs | High | Organizers supply licensed test data | — |
| A-004 | Our 300-screen synthetic corpus is a valid proxy for finale eval screens | No public India-PII screen dataset exists | Research gap documented in RESEARCH.md | Medium | Finale uses very different form archetypes | Build corpus with 6 diverse archetypes incl. ISRO-style portals |
| A-005 | Qwen2.5-VL-7B (Apache-2.0) satisfies "open-source/open-weights" | Explicitly allowed ("participants free to use any offline deployable open-source model") | Qwen blog license statement (verified) | High | Rule reinterpretation | Read finale rules on arrival |
| A-006 | a11y trees are available on all target pages | Chromium/Firefox CDP both expose AX trees | Playwright docs | High | A finale page kills AX (canvas-only app) | Vision-channel fallback note in ARCHITECTURE |
