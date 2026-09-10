"""Fail-closed health check for an OpenAI-compatible VLM endpoint."""

import argparse
import json
import sys

import httpx


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--model")
    args = parser.parse_args()
    try:
        response = httpx.get(f"{args.base_url.rstrip('/')}/models", timeout=5)
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}))
        return 2
    models = [item.get("id") for item in payload.get("data", [])]
    result = {"status": "PASS", "models": models}
    if args.model and args.model not in models:
        result.update({"status": "FAIL", "reason": "requested model is not served"})
        print(json.dumps(result))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
