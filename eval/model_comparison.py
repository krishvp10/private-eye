"""Generate a privacy-safe model comparison report.

The command records SKIPPED for models without a reachable real endpoint. It
does not substitute mock measurements for Qwen measurements.
"""

import argparse
import asyncio
import json
import os
import platform
from pathlib import Path
from typing import Any

import httpx

from eval.test_real_vlm import run


def unavailable(model: str, reason: str) -> dict[str, Any]:
    return {
        "model": model,
        "status": "SKIPPED",
        "reason": reason,
        "runs": [],
    }


def write_report(output: Path, report: dict[str, Any]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# PrivateEye model comparison",
        "",
        f"**Status:** {report['status']}",
        "",
        "| Model | Status | Workflow success | p50 total latency | p95 total latency |",
        "|---|---|---:|---:|---:|",
    ]
    for item in report["models"]:
        summary = item.get("summary", {})
        lines.append(
            f"| {item['model']} | {item['status']} | "
            f"{summary.get('workflow_success', '—')} | "
            f"{summary.get('p50_total_latency_ms', '—')} | "
            f"{summary.get('p95_total_latency_ms', '—')} |"
        )
    output.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def summarize(runs: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = sorted(
        item["elapsed_ms"] for item in runs if isinstance(item.get("elapsed_ms"), (int, float))
    )
    if not latencies:
        return {}
    p50 = latencies[(len(latencies) - 1) // 2]
    p95 = latencies[max(0, int(len(latencies) * 0.95) - 1)]
    return {
        "workflow_success": sum(bool(item.get("success")) for item in runs) / len(runs),
        "p50_total_latency_ms": p50,
        "p95_total_latency_ms": p95,
    }


async def measure_model(args: argparse.Namespace, model: str) -> dict[str, Any]:
    old_model = os.environ.get("PRIVATEEYE_VLM_MODEL")
    os.environ["PRIVATEEYE_VLM_MODEL"] = model
    try:
        try:
            async with httpx.AsyncClient(timeout=3) as health_client:
                health_response = await health_client.get(f"{args.server_url}/v1/health")
                health_response.raise_for_status()
                health = health_response.json()
        except httpx.HTTPError as exc:
            return unavailable(model, str(exc))
        if health.get("mode") != "real":
            return unavailable(model, "server is not running in real mode")
        runs = []
        for _ in range(args.runs):
            result = await run(args.url, args.server_url, args.max_steps)
            runs.append(result)
        return {
            "model": model,
            "status": "PASS" if all(item.get("success") for item in runs) else "FAIL",
            "runs": runs,
            "summary": summarize(runs),
        }
    finally:
        if old_model is None:
            os.environ.pop("PRIVATEEYE_VLM_MODEL", None)
        else:
            os.environ["PRIVATEEYE_VLM_MODEL"] = old_model


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    if os.getenv("PRIVATEEYE_VLM_MODE", "mock").lower() != "real":
        models = [unavailable(model, "PRIVATEEYE_VLM_MODE is not real") for model in args.models]
    else:
        models = [await measure_model(args, model) for model in args.models]
    report = {
        "status": "SKIPPED" if all(item["status"] == "SKIPPED" for item in models) else "COMPLETE",
        "environment": {"platform": platform.platform()},
        "models": models,
        "note": "No model ranking is made without measured real-model evidence.",
    }
    write_report(Path(args.output), report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare configured Qwen-VL models")
    parser.add_argument("--url", default="http://127.0.0.1:9001/login")
    parser.add_argument("--server-url", default="http://127.0.0.1:8100")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["Qwen/Qwen2.5-VL-3B-Instruct", "Qwen/Qwen2.5-VL-7B-Instruct"],
    )
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--max-steps", type=int, default=24)
    parser.add_argument("--output", default="eval/reports/model_comparison.json")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(main_async(args)), indent=2))


if __name__ == "__main__":
    main()
