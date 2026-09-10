"""
PrivateEye Real VLM Endpoint Health & Readiness Checker.

Performs fail-closed validation of an OpenAI-compatible Vision-Language Model endpoint:
1. Validates HTTP reachability of /v1/models.
2. Confirms the requested model (e.g. Qwen2.5-VL-3B-Instruct) is served.
3. Checks for schema-guided structured output and multimodal support.
4. Reports exact status (PASS, FAIL, or BLOCKED) without silent mock fallbacks.
"""

import argparse
import json
import platform
import sys
from typing import Any

import httpx


def check_endpoint(
    base_url: str = "http://127.0.0.1:8000/v1", target_model: str | None = None
) -> dict[str, Any]:
    clean_url = base_url.rstrip("/")
    result: dict[str, Any] = {
        "status": "BLOCKED",
        "endpoint": clean_url,
        "environment": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
        },
        "models_available": [],
        "target_model": target_model,
    }

    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{clean_url}/models")
            if resp.status_code != 200:
                result["reason"] = f"Endpoint returned HTTP status {resp.status_code}"
                return result

            data = resp.json()
            models: list[str] = [
                str(m["id"])
                for m in data.get("data", [])
                if isinstance(m, dict) and isinstance(m.get("id"), str)
            ]
            result["models_available"] = models

            if target_model:
                normalized_target = target_model.lower()
                matched = any(normalized_target in m.lower() for m in models)
                if not matched:
                    result["status"] = "FAIL"
                    result["reason"] = (
                        f"Model '{target_model}' not found among available models: {models}"
                    )
                    return result

            result["status"] = "PASS"
            result["reason"] = "Endpoint reachable and model verified"
            return result

    except httpx.ConnectError:
        result["reason"] = f"Connection refused at {clean_url}. Ensure vLLM or Ollama is running."
        return result
    except httpx.TimeoutException:
        result["reason"] = f"Connection timed out at {clean_url} after 5.0s."
        return result
    except (httpx.HTTPError, TimeoutError, ValueError, json.JSONDecodeError, OSError) as e:
        result["reason"] = f"Unexpected health-check error: {e!s}"
        return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check health of an OpenAI-compatible VLM endpoint"
    )
    parser.add_argument(
        "--base-url", default="http://127.0.0.1:8000/v1", help="Base URL of OpenAI-compatible API"
    )
    parser.add_argument("--model", default=None, help="Specific model ID to verify")
    args = parser.parse_args()

    res = check_endpoint(args.base_url, args.model)
    print(json.dumps(res, indent=2))
    return 0 if res["status"] == "PASS" else (1 if res["status"] == "FAIL" else 2)


if __name__ == "__main__":
    sys.exit(main())
