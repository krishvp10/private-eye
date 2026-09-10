"""Run a real-VLM experiment when an endpoint is configured.

Without PRIVATEEYE_VLM_MODE=real and a reachable endpoint, this command emits a
SKIPPED report rather than pretending that a real model was exercised.
"""

import argparse
import asyncio
import json
import os
import platform
import time
from pathlib import Path

import httpx

from eval.test_real_vlm import run


def skipped(reason: str, output: Path) -> dict:
    report = {
        "status": "SKIPPED",
        "reason": reason,
        "mode": os.getenv("PRIVATEEYE_VLM_MODE", "mock"),
        "model": os.getenv("PRIVATEEYE_VLM_MODEL", "unknown"),
        "environment": {"platform": platform.platform()},
        "runs": [],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    output.with_suffix(".md").write_text(
        "# PrivateEye real-VLM experiment\n\n"
        f"**Status:** SKIPPED\n\n**Reason:** {reason}\n\n"
        "No live Qwen2.5-VL result is claimed. Configure a reachable real endpoint "
        "and set `PRIVATEEYE_VLM_MODE=real` to run the experiment.\n",
        encoding="utf-8",
    )
    return report


async def main_async(args: argparse.Namespace) -> dict:
    output = Path(args.output)
    if os.getenv("PRIVATEEYE_VLM_MODE", "mock").lower() != "real":
        return skipped("PRIVATEEYE_VLM_MODE is not real", output)
    try:
        health = httpx.get(f"{args.server_url}/v1/health", timeout=3).json()
    except httpx.HTTPError:
        return skipped("real VLM server is unreachable", output)
    if health.get("mode") != "real":
        return skipped("server is not running in real mode", output)

    runs = []
    for index in range(args.runs):
        started = time.perf_counter()
        result = await run(args.url, args.server_url, args.max_steps)
        result["run_index"] = index + 1
        result["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)
        runs.append(result)
    report = {
        "status": "PASS" if all(item["success"] for item in runs) else "FAIL",
        "mode": "real",
        "model": os.getenv("PRIVATEEYE_VLM_MODEL", "unknown"),
        "environment": {"platform": platform.platform()},
        "runs": runs,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    output.with_suffix(".md").write_text(
        "# PrivateEye real-VLM experiment\n\n"
        f"**Status:** {report['status']}\n\n"
        f"**Model:** {report['model']}\n\n"
        f"**Runs:** {len(runs)}\n\n"
        "This report contains metadata only; raw prompts, screenshots, and secrets "
        "are intentionally excluded.\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the real-VLM reliability experiment")
    parser.add_argument("--url", default="http://127.0.0.1:9001/login")
    parser.add_argument("--server-url", default="http://127.0.0.1:8100")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--max-steps", type=int, default=24)
    parser.add_argument("--output", default="eval/reports/real_vlm_report.json")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(main_async(args)), indent=2))


if __name__ == "__main__":
    main()
