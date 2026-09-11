"""Phase 19 evidence evaluator.

This program deliberately does *not* simulate an agent and label its output an
experiment. It scores only externally captured, paired JSONL trajectories.
Absent raw evidence is a valid result: ``NOT_RUN``.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

REPORTS_DIR = Path("eval/reports")
RAW_PAIRS = Path("eval/evidence/phase19/checkpoint_pairs.jsonl")
TRACE_DIR = REPORTS_DIR / "traces" / "phase19"
HORIZONS = (5, 10, 15, 20, 30, 40, 50)
REQUIRED = {
    "pair_id", "task_id", "initial_state_hash", "environment", "model",
    "seed", "step_budget", "fault_schedule_hash", "condition", "success",
    "first_failure_step", "rollback_count", "recovery_success",
}


def load_pairs(path: Path = RAW_PAIRS) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        missing = REQUIRED - row.keys()
        if missing:
            raise ValueError(f"{path}:{line_number}: missing {sorted(missing)}")
        if row["condition"] not in {"off", "on"} or not isinstance(row["success"], bool):
            raise ValueError(f"{path}:{line_number}: invalid condition or success")
        rows.append(row)
    return rows


def matched_pairs(rows: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["pair_id"], []).append(row)
    pairs = []
    invariants = ("task_id", "initial_state_hash", "environment", "model", "seed", "step_budget", "fault_schedule_hash")
    for pair_id, group in grouped.items():
        if len(group) != 2 or {r["condition"] for r in group} != {"off", "on"}:
            raise ValueError(f"pair {pair_id} must contain exactly one off and one on trajectory")
        off, on = sorted(group, key=lambda r: r["condition"])
        if any(off[key] != on[key] for key in invariants):
            raise ValueError(f"pair {pair_id} violates matched-condition invariants")
        pairs.append((off, on))
    return pairs


def evaluate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    pairs = matched_pairs(rows)
    if not pairs:
        return {
            "status": "NOT_RUN", "reason": "No raw paired trajectories found.",
            "raw_input": str(RAW_PAIRS), "required_minimum_pairs": 30,
            "causal_verdict": "INSUFFICIENT EVIDENCE",
        }
    off_success = sum(off["success"] for off, _ in pairs)
    on_success = sum(on["success"] for _, on in pairs)
    discordant = Counter((off["success"], on["success"]) for off, on in pairs)
    return {
        "status": "SCORED_FROM_RAW_TRAJECTORIES",
        "sample_size_pairs": len(pairs),
        "condition_off_success": {"numerator": off_success, "denominator": len(pairs), "unit": "tasks"},
        "condition_on_success": {"numerator": on_success, "denominator": len(pairs), "unit": "tasks"},
        "paired_success_difference_percentage_points": round(100 * (on_success - off_success) / len(pairs), 2),
        "discordant_pairs": {"off_fail_on_success": discordant[(False, True)], "off_success_on_fail": discordant[(True, False)]},
        "horizons_requested": list(HORIZONS),
        "causal_verdict": "EXPERIMENTAL ESTIMATE ONLY; report confidence interval before causal conclusion.",
    }


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    result = evaluate(load_pairs())
    for name in ("phase19_checkpoint_causal.json", "phase19_long_horizon.json"):
        (REPORTS_DIR / name).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
