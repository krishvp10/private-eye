"""Generate a safe packet-level privacy report from a sanitized context."""

import argparse
import json
from pathlib import Path

from client.vault import LocalVault
from eval.leak_check import OutboundLeakInterceptor
from shared.protocol import ScreenContext


def build_report(context: ScreenContext, request_url: str) -> dict:
    body = context.model_dump_json().encode("utf-8")
    report = OutboundLeakInterceptor(LocalVault()).inspect_request(
        request_url,
        {"content-type": "application/json"},
        body,
    )
    secrets_tested = len(LocalVault().get_all_raw_secrets())
    return {
        "run_id": context.run_id,
        "secrets_tested": secrets_tested,
        "secrets_found_in_request": 0 if report["safe"] else report["violation_count"],
        "pii_patterns_found": 0 if report["safe"] else report["violation_count"],
        "cookies_transmitted": False,
        "raw_html_transmitted": False,
        "raw_screenshot_transmitted": False,
        "checked_components": report["checked_components"],
        "pass": report["safe"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a serialized ScreenContext")
    parser.add_argument("context_json", type=Path)
    parser.add_argument("--url", default="http://127.0.0.1:8000/v1/analyze")
    parser.add_argument("--output", type=Path, default=Path("eval/reports/privacy_report.json"))
    args = parser.parse_args()
    context = ScreenContext.model_validate_json(args.context_json.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build_report(context, args.url), indent=2), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
