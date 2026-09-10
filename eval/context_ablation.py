"""Run screenshot/graph/redaction-context ablation against a real VLM server.

The command never substitutes mock results. If the configured real endpoint is
unavailable, it writes a SKIPPED report with no fabricated accuracy numbers.
"""

import argparse
import asyncio
import json
import os
import platform
from pathlib import Path
from typing import Any, cast

import httpx

from client.capture import capture_page
from privacy.pipeline import PrivacyPipeline
from privacy.redaction.masker import RedactionEngine
from server.vlm import VLMAdapter
from shared.protocol import ScreenContext

VARIANTS = ("screenshot_only", "screenshot_graph", "screenshot_graph_redactions")


def write_report(output: Path, report: dict[str, Any]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    rows = report.get("variants", {})
    lines = [
        "# PrivateEye context ablation",
        "",
        f"**Status:** {report['status']}",
        "",
        (
            "This report distinguishes real-model results from skipped runs. "
            "No raw screenshots, prompts, or secrets are stored."
        ),
        "",
        "| Variant | Status | Grounding accuracy | Workflow success | Latency |",
        "|---|---|---:|---:|---:|",
    ]
    for name, value in rows.items():
        lines.append(
            f"| {name} | {value.get('status', 'SKIPPED')} | "
            f"{value.get('grounding_accuracy', '—')} | "
            f"{value.get('workflow_success', '—')} | "
            f"{value.get('latency_ms', '—')} |"
        )
    output.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def safe_variant_context(context: ScreenContext, variant: str) -> ScreenContext:
    data = context.model_dump()
    if variant == "screenshot_only":
        data["screen_graph"] = context.screen_graph.model_copy(
            update={"root": context.screen_graph.root.model_copy(update={"children": []})}
        )
        data["redactions"] = []
    elif variant == "screenshot_graph":
        data["redactions"] = []
    return cast(ScreenContext, ScreenContext.model_validate(data))


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    output = Path(args.output)
    variants: dict[str, dict[str, Any]] = {name: {"status": "SKIPPED"} for name in VARIANTS}
    if os.getenv("PRIVATEEYE_VLM_MODE", "mock").lower() != "real":
        report: dict[str, Any] = {
            "status": "SKIPPED",
            "reason": "PRIVATEEYE_VLM_MODE is not real",
            "environment": {"platform": platform.platform()},
            "variants": variants,
        }
        write_report(output, report)
        return report
    try:
        async with httpx.AsyncClient(timeout=3) as health_client:
            health_response = await health_client.get(f"{args.server_url}/v1/health")
            health_response.raise_for_status()
            health = health_response.json()
        if health.get("mode") != "real":
            raise RuntimeError("server is not in real mode")
    except (httpx.HTTPError, RuntimeError) as exc:
        report = {
            "status": "SKIPPED",
            "reason": str(exc),
            "environment": {"platform": platform.platform()},
            "variants": variants,
        }
        write_report(output, report)
        return report

    timeout = float(os.getenv("PRIVATEEYE_VLM_TIMEOUT", "120"))
    async with httpx.AsyncClient(timeout=timeout) as client:
        from playwright.async_api import async_playwright

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1280, "height": 800})
            await page.goto(args.url, wait_until="networkidle")
            captured = await capture_page(page)
            detections = PrivacyPipeline().detect(
                captured.raw_elements,
                captured.screenshot_bytes,
                captured.visible_text,
                captured.viewport,
            )
            redacted = RedactionEngine().redact(
                captured.screenshot_bytes, captured.screen_graph, detections
            )
            import base64

            base_context = ScreenContext(
                run_id="context-ablation",
                step=1,
                url=page.url,
                image_b64=base64.b64encode(redacted.sanitized_bytes).decode("ascii"),
                screen_graph=redacted.sanitized_graph,
                redactions=redacted.redaction_map.redactions,
                task=args.task,
            )
            adapter = VLMAdapter()
            for variant in VARIANTS:
                context = safe_variant_context(base_context, variant)
                started = asyncio.get_running_loop().time()
                response = await client.post(
                    f"{args.server_url}/v1/analyze",
                    json=context.model_dump(),
                )
                latency_ms = round((asyncio.get_running_loop().time() - started) * 1000, 2)
                variants[variant] = {
                    "status": "PASS" if response.is_success else "FAIL",
                    "schema_valid": response.is_success,
                    "grounding_accuracy": None,
                    "workflow_success": None,
                    "latency_ms": latency_ms,
                    "action": response.json().get("action") if response.is_success else None,
                }
            await browser.close()
    report = {
        "status": "PASS",
        "model": adapter.model_name,
        "environment": {"platform": platform.platform()},
        "variants": variants,
        "note": "This canary measures response validity and latency; full grounding/workflow denominators require the real action runner.",
    }
    write_report(output, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run real-VLM context ablation")
    parser.add_argument("--url", default="http://127.0.0.1:9001/kyc")
    parser.add_argument("--server-url", default="http://127.0.0.1:8100")
    parser.add_argument("--task", default="Identify the next safe KYC action")
    parser.add_argument("--output", default="eval/reports/context_ablation.json")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(main_async(args)), indent=2))


if __name__ == "__main__":
    main()
