"""Summarize separately measured Qwen 3B and 7B runs without rerouting models."""

import json
import platform
import statistics
import subprocess
from pathlib import Path
from typing import Any

REPORT_DIR = Path("eval/reports")


def load(path: str) -> dict[str, Any]:
    return json.loads((REPORT_DIR / path).read_text(encoding="utf-8"))


def gpu_snapshot() -> dict[str, str]:
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.used,memory.total,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        fields = [part.strip() for part in result.stdout.strip().split(",")]
        if len(fields) == 4:
            return {
                "name": fields[0],
                "memory_used_mib": fields[1],
                "memory_total_mib": fields[2],
                "utilization_percent": fields[3],
            }
    except (OSError, subprocess.SubprocessError):
        pass
    return {"status": "unavailable"}


def summarize(workflow: dict[str, Any], canary: dict[str, Any]) -> dict[str, Any]:
    runs = workflow.get("runs", [])
    latencies = sorted(
        run["elapsed_ms"] for run in runs if isinstance(run.get("elapsed_ms"), (int, float))
    )
    canaries = canary.get("canaries", [])
    target_correct = [bool(item.get("target_correct")) for item in canaries]
    return {
        "model": workflow.get("model", canary.get("model", "unknown")),
        "workflow_runs": len(runs),
        "workflow_success_count": sum(bool(run.get("success")) for run in runs),
        "workflow_success_rate": (
            sum(bool(run.get("success")) for run in runs) / len(runs) if runs else None
        ),
        "grounding_accuracy": (
            sum(target_correct) / len(target_correct) if target_correct else None
        ),
        "schema_valid_rate": (
            sum(bool(item.get("schema_valid")) for item in canaries) / len(canaries)
            if canaries
            else None
        ),
        "p50_workflow_latency_ms": statistics.median(latencies) if latencies else None,
        "p95_workflow_latency_ms": (
            latencies[max(0, int(len(latencies) * 0.95) - 1)] if latencies else None
        ),
        "canary_failures": sum(item.get("status") != "PASS" for item in canaries),
        "canary_failure_classes": [
            item.get("failure_class") for item in canaries if item.get("failure_class")
        ],
    }


def main() -> None:
    models = [
        summarize(load("real_vlm_report.json"), load("real_vlm_canaries.json")),
        summarize(load("real_vlm_report_7b.json"), load("real_vlm_canaries_7b.json")),
    ]
    report = {
        "status": "COMPLETE",
        "evidence_source": "live_real_vlm_runs",
        "environment": {"platform": platform.platform(), "gpu": gpu_snapshot()},
        "models": models,
        "note": "Comparison is descriptive; no model is declared superior without equivalent resource and task coverage.",
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "model_comparison_real.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    lines = [
        "# PrivateEye live Qwen model comparison",
        "",
        f"**Status:** {report['status']}",
        "",
        "| Model | Workflow success | Grounding accuracy | p50 workflow ms | p95 workflow ms | Canary failures |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in models:
        lines.append(
            f"| {item['model']} | {item['workflow_success_count']}/{item['workflow_runs']} | "
            f"{item['grounding_accuracy']} | {item['p50_workflow_latency_ms']} | "
            f"{item['p95_workflow_latency_ms']} | {item['canary_failures']} |"
        )
    (REPORT_DIR / "model_comparison_real.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
