"""Write evidence-status reports without inventing empirical measurements."""
from __future__ import annotations

import json
from pathlib import Path

REPORTS = Path("eval/reports")
UNRUN = {"status": "NOT_RUN", "classification": "NOT REPRODUCIBLE", "reason": "No raw, independently captured evidence was supplied to the deterministic scorer."}


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    reports = {
        "phase19_evidence_forensics.json": {"status": "COMPLETE", "classification": {
            "phase18_checkpointing_51_3_to_81": "MODEL-PREDICTED COMPOUNDING ESTIMATE; NOT CAUSAL",
            "phase18_privacy_4619_bytes": "NARROW PAYLOAD-SCOPE TEST; NOT COMPLETE OUTBOUND BOUNDARY",
            "phase18_user_study": "DOCUMENTATION-ONLY; raw participant responses absent",
            "phase19_browser_native": "NOT REPRODUCIBLE; no MV3/Offscreen/browser execution artifact"}},
        "phase19_reproduction.json": UNRUN, "phase19_live_web.json": UNRUN,
        "phase19_user_study.json": UNRUN, "phase19_human_timing.json": UNRUN,
        "phase19_modality.json": UNRUN, "phase19_process.json": UNRUN,
        "phase19_browser_native.json": UNRUN,
        "phase19_ps_compliance.json": {"status": "NOT_TESTED", "browser_native_inference": "NOT SATISFIED", "host_local_inference": "PARTIALLY SATISFIED; not equivalent to browser-native inference"},
        "phase19_privacy.json": {"status": "NOT_RUN", "reason": "Complete outbound capture requires a controlled browser workflow and receiver-side capture; synthetic payload generation is not application-boundary evidence."},
        "phase19_safety.json": {"status": "NOT_RUN", "reason": "A simulated fail-closed branch is not control-plane fuzzing against the runtime."},
    }
    for name, value in reports.items():
        (REPORTS / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
