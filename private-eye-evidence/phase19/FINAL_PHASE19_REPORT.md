# Phase 19 — Forensic Evidence Status

## Verdict

**INSUFFICIENT EVIDENCE**

This is not a negative result about PrivateEye's capabilities. It is the only
defensible conclusion from the evidence currently stored in this repository.

## What the forensic audit established

| Claim | Finding | Status |
| --- | --- | --- |
| 51.3% to 81.0% at 30 steps | Derived from a compounding model, not matched trajectories | Not causal evidence |
| 0 / 4,619 privacy bytes | Isolated synthetic request-payload scope | Not complete outbound-boundary evidence |
| 100-case control-plane fuzzing | The prior runner simulated a fail-closed result | Not runtime fuzz evidence |
| MV3/Offscreen/WebGPU profile | No extension, browser profile, or raw performance trace exists | Not executed |
| 15-site live-web and user-study outcomes | No raw task records, consent records, or participant responses exist | Not reproducible |

## Required evidence before a changed verdict

1. At least 30 resettable matched pairs, each with task, initial-state hash,
   model, seed, fault-schedule hash, step budget, and both condition traces.
2. A controlled browser workflow with receiver-side capture of every tested
   outbound request/frame and per-run dynamic canaries.
3. Runtime—not simulated—control-plane fuzz traces and deterministic scoring.
4. Consent-backed anonymized participant records for any human-study metric.
5. A reproducible MV3 extension benchmark with raw browser profiling output.

The deterministic scorer in `eval/phase19_causal_engine.py` accepts matched
JSONL evidence and rejects pairs whose experimental invariants differ.

## External-method limit

See `docs/PHASE19_EXTERNAL_METHODS.md` for primary-source methodology. The
reported SIH 26171 weights and wording were not verified from an official
public problem statement and are therefore not treated as authoritative here.
