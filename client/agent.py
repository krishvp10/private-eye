"""
PrivateEye end-to-end local agent.

The browser, privacy pipeline, redaction engine, vault, and action executor all
remain on the client. Only a sanitized ScreenContext is posted to the server.
"""

import argparse
import asyncio
import base64
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx
from playwright.async_api import async_playwright

from client.capture import CapturedContext, capture_page
from client.executor.execute import ActionExecutor
from eval.leak_check import OutboundLeakInterceptor
from privacy.pipeline import PrivacyPipeline
from privacy.redaction.masker import RedactionEngine
from server.validation import validate_agent_action
from shared.protocol import AgentAction, ActionType, ScreenContext


@dataclass
class AgentRunResult:
    run_id: str
    success: bool
    final_url: str
    steps: int
    telemetry: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class PrivateEyeAgent:
    """Runs a bounded capture -> sanitize -> reason -> execute loop."""

    def __init__(
        self,
        server_url: str = "http://127.0.0.1:8000",
        max_steps: int = 24,
        task: str = "Complete the KYC verification form",
        executor: Optional[ActionExecutor] = None,
    ) -> None:
        self.server_url = server_url.rstrip("/")
        self.max_steps = max_steps
        self.task = task
        self.pipeline = PrivacyPipeline()
        self.redactor = RedactionEngine()
        self.leak_interceptor = OutboundLeakInterceptor()
        self.executor = executor or ActionExecutor()

    async def run(self, url: str) -> AgentRunResult:
        run_id = str(uuid.uuid4())
        telemetry: List[Dict[str, Any]] = []
        errors: List[str] = []

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1280, "height": 800})
            await page.goto(url, wait_until="networkidle")

            async with httpx.AsyncClient(timeout=15.0) as http:
                for step in range(1, self.max_steps + 1):
                    step_started = time.perf_counter()
                    captured = await capture_page(page)
                    detections = self.pipeline.detect(
                        captured.raw_elements,
                        screenshot_bytes=captured.screenshot_bytes,
                        visible_text=captured.visible_text,
                        viewport=captured.viewport,
                    )
                    redacted = self.redactor.redact(
                        captured.screenshot_bytes,
                        captured.screen_graph,
                        detections,
                    )
                    self.executor.set_reference_map({
                        node.ref: {
                            "element_id": node.id,
                            "role": node.role,
                            "name": node.name or "",
                        }
                        for node in redacted.sanitized_graph.root.children
                        if node.ref
                    })
                    image_b64 = base64.b64encode(redacted.sanitized_bytes).decode("ascii")
                    context = ScreenContext(
                        run_id=run_id,
                        step=step,
                        url=page.url,
                        image_b64=image_b64,
                        screen_graph=redacted.sanitized_graph,
                        redactions=redacted.redaction_map.redactions,
                        task=self.task,
                    )

                    payload = context.model_dump_json()
                    self.leak_interceptor.assert_safe(payload)
                    network_started = time.perf_counter()
                    response = await http.post(
                        f"{self.server_url}/v1/analyze",
                        content=payload,
                        headers={"content-type": "application/json"},
                    )
                    response.raise_for_status()
                    action = validate_agent_action(response.json())
                    network_ms = (time.perf_counter() - network_started) * 1000

                    execution = await self.executor.execute(page, action, step=step)
                    target_ref = action.target.ref if action.target else None
                    telemetry.append(
                        {
                            "step": step,
                            "url": page.url,
                            "action_type": action.action.value,
                            "target_ref": target_ref,
                            "detections": len(detections),
                            "redactions": len(redacted.redaction_map.redactions),
                            "payload_bytes": len(payload.encode("utf-8")),
                            "network_ms": round(network_ms, 2),
                            "execution_ms": execution.duration_ms,
                            "total_ms": round((time.perf_counter() - step_started) * 1000, 2),
                            "retry_count": 0,
                            "result": "success" if execution.success else "failure",
                        }
                    )
                    if not execution.success:
                        errors.append(execution.error_message or "Action execution failed")
                        await browser.close()
                        return AgentRunResult(run_id, False, page.url, step, telemetry, errors)
                    if action.action == ActionType.DONE:
                        final_url = page.url
                        await browser.close()
                        return AgentRunResult(run_id, True, final_url, step, telemetry, errors)

            final_url = page.url
            await browser.close()
            errors.append(f"Maximum step count ({self.max_steps}) exceeded")
            return AgentRunResult(run_id, False, final_url, self.max_steps, telemetry, errors)


async def run_cli(url: str, server_url: str, task: str, max_steps: int) -> None:
    result = await PrivateEyeAgent(server_url=server_url, task=task, max_steps=max_steps).run(url)
    print(json.dumps({
        "success": result.success,
        "run_id": result.run_id,
        "final_url": result.final_url,
        "steps": result.steps,
        "telemetry": result.telemetry,
        "errors": result.errors,
    }, indent=2))
    if not result.success:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the PrivateEye local browser agent")
    parser.add_argument("--url", default="http://127.0.0.1:9001/login")
    parser.add_argument("--server-url", default="http://127.0.0.1:8000")
    parser.add_argument("--task", default="Complete the KYC verification form")
    parser.add_argument("--max-steps", type=int, default=24)
    args = parser.parse_args()
    asyncio.run(run_cli(args.url, args.server_url, args.task, args.max_steps))
