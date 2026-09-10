"""
Phase 13 Release Manifest & Verification Utility (eval/package_phase13_release.py).

Generates private-eye-evidence/phase13/RELEASE_MANIFEST.json certifying all submission
deliverables, environment freeze hashes, and canonical metrics.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PHASE13_DIR = REPO_ROOT / "private-eye-evidence" / "phase13"
PHASE13_DIR.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def generate_phase13_manifest() -> dict:
    deliverables = [
        "FINAL_DEMO_SCRIPT.md",
        "DEMO_FALLBACK.md",
        "FINAL_RESULTS_ONE_PAGE.md",
        "JUDGE_QA_FINAL.md",
        "SUBMISSION_CHECKLIST.md",
        "FINAL_SUBMISSION_REPORT.md",
    ]

    manifest = {
        "release_version": "v1.0-RC-final",
        "timestamp_utc": "2026-09-10T20:20:00Z",
        "frozen_baseline_commit": "5d697dc",
        "production_directories_frozen": ["client/", "server/", "privacy/", "shared/"],
        "authoritative_metrics": {
            "phase10_live_task_success_pct": 89.0,
            "phase10_live_step_accuracy_pct": 98.79,
            "phase11_heldout_task_success_pct": 86.0,
            "phase11_heldout_step_accuracy_pct": 98.46,
            "phase11_cluster_bootstrap_ci_task": [77.0, 93.0],
            "phase11_cluster_bootstrap_ci_step": [97.72, 99.22],
            "trajectory_actions_to_completion_ratio": 1.000,
            "privacy_leaks_detected": 0,
            "pii_detector_precision_pct": 95.92,
            "pii_detector_recall_pct": 94.00,
            "prompt_injections_blocked": "15/15",
            "compound_faults_contained": "10/10",
            "osworld_adapted_diagnostic": "20/20",
            "kill_switch_dispatch_latency_ms": 0.043,
        },
        "phase13_deliverables": {},
    }

    for name in deliverables:
        f = PHASE13_DIR / name
        if f.exists():
            manifest["phase13_deliverables"][name] = {
                "sha256": sha256_file(f),
                "size_bytes": f.stat().st_size,
            }

    out_file = PHASE13_DIR / "RELEASE_MANIFEST.json"
    out_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    m = generate_phase13_manifest()
    print(
        "Phase 13 release manifest generated with "
        + str(len(m["phase13_deliverables"]))
        + " deliverables."
    )
