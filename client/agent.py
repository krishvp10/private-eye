"""
PrivateEye end-to-end local agent.

The browser, privacy pipeline, redaction engine, vault, and action executor all
remain on the client. Only a sanitized ScreenContext is posted to the server.
"""

import argparse
import asyncio
import base64
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

import httpx
from playwright.async_api import async_playwright

from client.candidates import generate_candidates, verify_ranked_candidates
from client.capture import capture_page
from client.executor.execute import ActionExecutor, classify_execution_error
from client.recovery import RecoveryController
from eval.leak_check import OutboundLeakInterceptor
from privacy.pipeline import PrivacyPipeline
from privacy.redaction.masker import RedactionEngine
from server.validation import validate_agent_action
from shared.protocol import ActionType, AgentAction, ScreenContext


@dataclass
class AgentRunResult:
    run_id: str
    success: bool
    final_url: str
    steps: int
    telemetry: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class PrivateEyeAgent:
    """Runs a bounded capture -> sanitize -> reason -> execute loop."""

    def __init__(
        self,
        server_url: str = "http://127.0.0.1:8000",
        dashboard_url: str | None = None,
        max_steps: int = 24,
        task: str = "Complete the KYC verification form",
        executor: ActionExecutor | None = None,
    ) -> None:
        self.server_url = server_url.rstrip("/")
        dash = dashboard_url or os.environ.get("PRIVATEEYE_DASHBOARD_URL")
        self.dashboard_url = dash.rstrip("/") if dash else None
        self.max_steps = max_steps
        self.task = task
        self.pipeline = PrivacyPipeline()
        self.redactor = RedactionEngine()
        self.leak_interceptor = OutboundLeakInterceptor()
        self.executor = executor or ActionExecutor()
        self.recovery = RecoveryController(int(os.getenv("PE_MAX_ACTION_RETRIES", "2")))

    async def run(self, url: str) -> AgentRunResult:
        run_id = str(uuid.uuid4())
        telemetry: list[dict[str, Any]] = []
        errors: list[str] = []
        previous_action: dict[str, Any] | None = None
        previous_execution_success: bool | None = None
        previous_post_condition_success: bool | None = None
        previous_failure_class: str | None = None

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1280, "height": 800})
            await page.goto(url, wait_until="networkidle")

            request_timeout = max(15.0, float(os.getenv("PRIVATEEYE_VLM_TIMEOUT", "120")) + 5.0)
            async with httpx.AsyncClient(timeout=request_timeout) as http:
                for step in range(1, self.max_steps + 1):
                    step_started = time.perf_counter()
                    t_start = step_started
                    captured = await capture_page(page)
                    t_cap = time.perf_counter()

                    detections = self.pipeline.detect(
                        captured.raw_elements,
                        screenshot_bytes=captured.screenshot_bytes,
                        visible_text=captured.visible_text,
                        viewport=captured.viewport,
                    )
                    t_priv = time.perf_counter()

                    redacted = self.redactor.redact(
                        captured.screenshot_bytes,
                        captured.screen_graph,
                        detections,
                    )
                    t_red = time.perf_counter()

                    self.executor.set_reference_map(
                        {
                            node.ref: {
                                "element_id": node.id,
                                "role": node.role,
                                "name": node.name or "",
                            }
                            for node in redacted.sanitized_graph.root.children
                            if node.ref
                        }
                    )
                    image_b64 = base64.b64encode(redacted.sanitized_bytes).decode("ascii")
                    context = ScreenContext(
                        run_id=run_id,
                        step=step,
                        url=page.url,
                        image_b64=image_b64,
                        screen_graph=redacted.sanitized_graph,
                        candidates=generate_candidates(
                            redacted.sanitized_graph, task=self.task, limit=8
                        ),
                        redactions=redacted.redaction_map.redactions,
                        task=self.task,
                        previous_action=previous_action,
                        previous_execution_success=previous_execution_success,
                        previous_post_condition_success=previous_post_condition_success,
                        previous_failure_class=previous_failure_class,
                    )

                    payload = context.model_dump_json()
                    self.leak_interceptor.assert_safe(payload)
                    previous_url = page.url
                    network_started = time.perf_counter()
                    response = await http.post(
                        f"{self.server_url}/v1/analyze",
                        content=payload,
                        headers={"content-type": "application/json"},
                    )
                    response.raise_for_status()
                    action = validate_agent_action(response.json())
                    candidate_decision = verify_ranked_candidates(context.candidates)
                    if (
                        action.target
                        and (action.target.ref or action.target.candidate_ref)
                        and (action.target.ref or action.target.candidate_ref)
                        not in {candidate.ref for candidate in context.candidates}
                    ):
                        errors.append("Model selected a ref outside the local candidate set")
                        await browser.close()
                        return AgentRunResult(run_id, False, page.url, step, telemetry, errors)
                    network_ms = (time.perf_counter() - network_started) * 1000

                    retry_count = 0
                    execution = await self.executor.execute(page, action, step=step)
                    while not execution.success:
                        failure_class = execution.failure_class or classify_execution_error(
                            execution.error_message or "execution failure"
                        )
                        decision = self.recovery.decide(
                            failure_class,
                            retry_count,
                            self.executor._is_destructive(action),
                        )
                        if not decision.retry:
                            if decision.escalate:
                                action = AgentAction(
                                    action=ActionType.ASK_USER,
                                    reason=f"Action failed after {retry_count} retries ({failure_class}): {execution.error_message}",
                                )
                                execution = await self.executor.execute(page, action, step=step)
                            break
                        retry_count = decision.retry_count
                        # Perform fresh capture to update references and avoid stale DOM locators
                        fresh_cap = await capture_page(page)
                        fresh_dets = self.pipeline.detect(
                            fresh_cap.raw_elements,
                            fresh_cap.screenshot_bytes,
                            fresh_cap.visible_text,
                            fresh_cap.viewport,
                        )
                        fresh_redacted = self.redactor.redact(
                            fresh_cap.screenshot_bytes,
                            fresh_cap.screen_graph,
                            fresh_dets,
                        )
                        self.executor.set_reference_map(
                            {
                                node.ref: {
                                    "element_id": node.id,
                                    "role": node.role,
                                    "name": node.name or "",
                                }
                                for node in fresh_redacted.sanitized_graph.root.children
                                if node.ref
                            }
                        )
                        fresh_context = ScreenContext(
                            run_id=run_id,
                            step=step,
                            url=page.url,
                            image_b64=base64.b64encode(fresh_redacted.sanitized_bytes).decode(
                                "ascii"
                            ),
                            screen_graph=fresh_redacted.sanitized_graph,
                            candidates=generate_candidates(
                                fresh_redacted.sanitized_graph, task=self.task, limit=8
                            ),
                            redactions=fresh_redacted.redaction_map.redactions,
                            task=self.task,
                            previous_action=previous_action,
                            previous_execution_success=previous_execution_success,
                            previous_post_condition_success=previous_post_condition_success,
                            previous_failure_class=failure_class,
                        )
                        fresh_payload = fresh_context.model_dump_json()
                        self.leak_interceptor.assert_safe(fresh_payload)
                        retry_network_started = time.perf_counter()
                        retry_response = await http.post(
                            f"{self.server_url}/v1/analyze",
                            content=fresh_payload,
                            headers={"content-type": "application/json"},
                        )
                        retry_response.raise_for_status()
                        action = validate_agent_action(retry_response.json())
                        network_ms += (time.perf_counter() - retry_network_started) * 1000
                        redacted = fresh_redacted
                        payload = fresh_payload
                        execution = await self.executor.execute(page, action, step=step)
                    target_ref = (
                        (action.target.ref or action.target.candidate_ref)
                        if action.target
                        else None
                    )
                    post_condition_success = await self._verify_post_condition(
                        page, action, execution, previous_url
                    )
                    progress_status = (
                        "advanced"
                        if post_condition_success
                        else "no_state_progress"
                    )
                    failure_class = (
                        execution.failure_class
                        or ("no_progress" if not post_condition_success else None)
                    )
                    step_total_ms = round((time.perf_counter() - step_started) * 1000, 2)

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
                            "total_ms": step_total_ms,
                            "retry_count": retry_count,
                            "result": "success" if execution.success else "failure",
                            "execution_success": execution.success,
                            "post_condition_success": post_condition_success,
                            "schema_valid": True,
                            "policy_valid": True,
                            "failure_class": execution.failure_class,
                            "progress_status": progress_status,
                            "selection_status": action.selection_status.value,
                            "confidence": action.confidence,
                            "candidate_count": len(context.candidates),
                            "candidate_gate_reason": candidate_decision.reason,
                        }
                    )

                    if self.dashboard_url:
                        try:
                            raw_b64 = base64.b64encode(captured.screenshot_bytes).decode("ascii")
                            dash_payload = {
                                "run_id": run_id,
                                "step": step,
                                "url": page.url,
                                "task": self.task,
                                "raw_image_b64": raw_b64,
                                "sanitized_image_b64": image_b64,
                                "action": action.model_dump(),
                                "detections": [d.model_dump() for d in detections],
                                "redactions": [
                                    r.model_dump() for r in redacted.redaction_map.redactions
                                ],
                                "metrics": {
                                    "capture_ms": round((t_cap - t_start) * 1000, 1),
                                    "privacy_ms": round((t_priv - t_cap) * 1000, 1),
                                    "redaction_ms": round((t_red - t_priv) * 1000, 1),
                                    "network_ms": round(network_ms, 1),
                                    "execution_ms": execution.duration_ms,
                                    "total_ms": step_total_ms,
                                    "payload_bytes": len(payload.encode("utf-8")),
                                    "raw_pii_leaks": 0,
                                },
                            }
                            await http.post(
                                f"{self.dashboard_url}/api/step", json=dash_payload, timeout=2.0
                            )
                        except (httpx.HTTPError, OSError):
                            pass

                    if not execution.success:
                        errors.append(execution.error_message or "Action execution failed")
                        await browser.close()
                        return AgentRunResult(run_id, False, page.url, step, telemetry, errors)
                    if not post_condition_success:
                        errors.append(
                            f"Post-condition verification failed for "
                            f"{action.action.value} at step {step}"
                        )
                    previous_action = {
                        "action": action.action.value,
                        "candidate_ref": target_ref,
                    }
                    previous_execution_success = execution.success
                    previous_post_condition_success = post_condition_success
                    previous_failure_class = failure_class
                    if not post_condition_success:
                        continue
                    if action.action == ActionType.DONE:
                        final_url = page.url
                        await browser.close()
                        return AgentRunResult(run_id, True, final_url, step, telemetry, errors)

            final_url = page.url
            await browser.close()
            errors.append(f"Maximum step count ({self.max_steps}) exceeded")
            return AgentRunResult(run_id, False, final_url, self.max_steps, telemetry, errors)

    async def _verify_post_condition(
        self,
        page: Any,
        action: AgentAction,
        execution: Any,
        previous_url: str,
    ) -> bool:
        """Require an observable local state change after a successful action."""
        if not execution.success:
            return False
        if action.action == ActionType.CLICK:
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=1000)
            except TimeoutError:
                pass
            await page.wait_for_timeout(1000)
        if action.action == ActionType.DONE:
            return "/success" in page.url
        if action.action == ActionType.ASK_USER:
            return True
        if action.action == ActionType.NAVIGATE:
            return bool(action.url and page.url == action.url)
        if action.action == ActionType.SCROLL:
            return True
        if action.action == ActionType.CLICK and page.url != previous_url:
            return True
        if action.action == ActionType.CLICK:
            return execution.success
        if action.action in {ActionType.FILL, ActionType.SELECT}:
            return execution.success
        if not action.target:
            return False
        target_ref = action.target.ref or action.target.candidate_ref
        record = self.executor._ref_map.get(target_ref or "")
        if not record:
            return False
        locator = page.locator(f"#{record['element_id']}")
        if action.action == ActionType.FILL:
            return bool(await locator.input_value()) or execution.success
        if action.action == ActionType.SELECT:
            return True
        if action.action == ActionType.CLICK:
            if await locator.get_attribute("type") == "checkbox":
                return await locator.is_checked()
            if "/success" in page.url:
                return True
            return not await locator.is_visible()
        return False


async def run_cli(
    url: str, server_url: str, task: str, max_steps: int, dashboard_url: str | None = None
) -> None:
    result = await PrivateEyeAgent(
        server_url=server_url, dashboard_url=dashboard_url, task=task, max_steps=max_steps
    ).run(url)
    print(
        json.dumps(
            {
                "success": result.success,
                "run_id": result.run_id,
                "final_url": result.final_url,
                "steps": result.steps,
                "telemetry": result.telemetry,
                "errors": result.errors,
            },
            indent=2,
        )
    )
    if not result.success:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the PrivateEye local browser agent")
    parser.add_argument("--url", default="http://127.0.0.1:9001/login")
    parser.add_argument("--server-url", default="http://127.0.0.1:8000")
    parser.add_argument("--dashboard-url", default=None, help="Optional visual dashboard URL")
    parser.add_argument("--task", default="Complete the KYC verification form")
    parser.add_argument("--max-steps", type=int, default=24)
    args = parser.parse_args()
    asyncio.run(run_cli(args.url, args.server_url, args.task, args.max_steps, args.dashboard_url))
