"""Capture privacy evidence from one genuine real-VLM request."""

import argparse
import asyncio
import base64
import json
from pathlib import Path

import httpx
from playwright.async_api import async_playwright

from client.capture import capture_page
from eval.real_privacy_evidence import audit_wire_traffic, write_evidence_reports
from privacy.pipeline import PrivacyPipeline
from privacy.redaction.masker import RedactionEngine
from server.validation import validate_agent_action
from shared.protocol import ScreenContext


async def run_live(url: str, server_url: str) -> dict:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(url, wait_until="networkidle")
        captured = await capture_page(page)
        detections = PrivacyPipeline().detect(
            captured.raw_elements,
            captured.screenshot_bytes,
            captured.visible_text,
            captured.viewport,
        )
        redacted = RedactionEngine().redact(
            captured.screenshot_bytes,
            captured.screen_graph,
            detections,
        )
        context = ScreenContext(
            run_id="live-real-vlm-privacy",
            step=1,
            url=page.url,
            image_b64=base64.b64encode(redacted.sanitized_bytes).decode("ascii"),
            screen_graph=redacted.sanitized_graph,
            redactions=redacted.redaction_map.redactions,
            task="Identify the next safe KYC action",
        )
        payload = context.model_dump_json()
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{server_url.rstrip('/')}/v1/analyze",
                content=payload,
                headers={"content-type": "application/json"},
            )
            response.raise_for_status()
            action = validate_agent_action(response.json())
            runs_response = await client.get(f"{server_url.rstrip('/')}/v1/runs")
            runs_response.raise_for_status()
            server_logs = json.dumps(runs_response.json())
        await browser.close()

    return audit_wire_traffic(
        context,
        action,
        server_logs,
        evidence_source="live_real_vlm_request",
        live_real_vlm_traffic_verified=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit one live real-VLM request")
    parser.add_argument("--url", default="http://127.0.0.1:9001/kyc")
    parser.add_argument("--server-url", default="http://127.0.0.1:8100")
    parser.add_argument("--output-dir", type=Path, default=Path("eval/reports"))
    args = parser.parse_args()
    evidence = asyncio.run(run_live(args.url, args.server_url))
    write_evidence_reports(evidence, args.output_dir)
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
