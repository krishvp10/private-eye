"""Compare privacy-safe workflow telemetry from mock and real API servers."""

import argparse
import asyncio
import json
import time
from typing import Any

import httpx

from eval.test_real_vlm import run


async def probe(mode: str, url: str, server_url: str) -> dict[str, Any]:
    started = time.perf_counter()
    health = httpx.get(f"{server_url}/v1/health", timeout=5).json()
    result = await run(url, server_url, 20)
    result.update({
        "mode": mode,
        "reported_server_mode": health.get("mode"),
        "action_count": len(result["actions"]),
        "successful_steps": sum(1 for action in result["actions"] if action["execution_ms"] >= 0),
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
    })
    return result


async def main_async(args: argparse.Namespace) -> None:
    results = [await probe("mock", args.url, args.mock_server)]
    if args.real_server:
        results.append(await probe("real", args.url, args.real_server))
    print(json.dumps(results, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare a configured PrivateEye VLM server")
    parser.add_argument("--url", default="http://127.0.0.1:9001/login")
    parser.add_argument("--mock-server", default="http://127.0.0.1:8000")
    parser.add_argument("--real-server")
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
