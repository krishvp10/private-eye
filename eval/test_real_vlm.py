"""Run a configured real VLM workflow and emit privacy-safe measurements.

This script intentionally does not persist screenshots, prompts, or model output
containing page content. It records only action metadata and timing.
"""

import argparse
import asyncio
import json
import time

from client.agent import PrivateEyeAgent


async def run(url: str, server_url: str, max_steps: int) -> dict:
    started = time.perf_counter()
    result = await PrivateEyeAgent(
        server_url=server_url,
        max_steps=max_steps,
        task="Complete the KYC verification form",
    ).run(url)
    return {
        "success": result.success,
        "final_url": result.final_url,
        "steps": result.steps,
        "workflow_latency_ms": round((time.perf_counter() - started) * 1000, 2),
        "actions": [
            {
                "step": row["step"],
                "url": row["url"],
                "detections": row["detections"],
                "redactions": row["redactions"],
                "network_ms": row["network_ms"],
                "execution_ms": row["execution_ms"],
                "total_ms": row["total_ms"],
            }
            for row in result.telemetry
        ],
        "errors": result.errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a configured PrivateEye VLM endpoint")
    parser.add_argument("--url", default="http://127.0.0.1:9001/login")
    parser.add_argument("--server-url", default="http://127.0.0.1:8000")
    parser.add_argument("--max-steps", type=int, default=20)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.url, args.server_url, args.max_steps)), indent=2))


if __name__ == "__main__":
    main()
