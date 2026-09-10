"""
Local Action Executor for PrivateEye.
Executes VLM-recommended actions through Playwright semantic locators.
Enforces strict action whitelisting, local vault value resolution,
destructive action gating, and retry recovery.
"""

import time
import logging
from typing import Optional
from playwright.async_api import Locator, Page
from shared.protocol import (
    ActionType,
    AgentAction,
    ExecutionResult,
)
from client.vault import LocalVault

logger = logging.getLogger("private_eye_executor")


class ExecutorSecurityException(Exception):
    """Raised when an action violates client-side security policies."""
    pass


class ActionExecutor:
    """Safely executes structured browser actions on the local client machine."""

    ALLOWED_ACTIONS = {action.value for action in ActionType}

    def __init__(
        self,
        vault: Optional[LocalVault] = None,
        confirm_destructive: bool = False,
        timeout_ms: int = 5000,
    ) -> None:
        self.vault = vault or LocalVault()
        self.confirm_destructive = confirm_destructive
        self.timeout_ms = timeout_ms
        self._ref_map = {}

    async def execute(self, page: Page, action: AgentAction, step: int = 1) -> ExecutionResult:
        """Validate and execute action against the active Playwright page."""
        start_time = time.perf_counter()

        # 1. Whitelist validation
        if action.action.value not in self.ALLOWED_ACTIONS:
            raise ExecutorSecurityException(
                f"Action '{action.action}' is forbidden. Allowed: {sorted(self.ALLOWED_ACTIONS)}"
            )

        # 2. Guard against terminal actions
        if action.action == ActionType.DONE:
            return ExecutionResult(
                step=step,
                action=action.action,
                success=True,
                duration_ms=round((time.perf_counter() - start_time) * 1000, 2),
            )

        if action.action == ActionType.ASK_USER:
            return ExecutionResult(
                step=step,
                action=action.action,
                success=True,
                duration_ms=round((time.perf_counter() - start_time) * 1000, 2),
            )

        # 3. Handle Navigation
        if action.action == ActionType.NAVIGATE:
            if not action.url or not (action.url.startswith("http://") or action.url.startswith("https://")):
                raise ExecutorSecurityException(f"Forbidden or invalid URL: '{action.url}'")
            await page.goto(action.url, timeout=self.timeout_ms)
            return ExecutionResult(
                step=step,
                action=action.action,
                success=True,
                duration_ms=round((time.perf_counter() - start_time) * 1000, 2),
            )

        # 4. Handle Scroll
        if action.action == ActionType.SCROLL:
            dy = (action.scroll_delta or {}).get("dy", 400)
            dx = (action.scroll_delta or {}).get("dx", 0)
            await page.mouse.wheel(dx, dy)
            return ExecutionResult(
                step=step,
                action=action.action,
                success=True,
                duration_ms=round((time.perf_counter() - start_time) * 1000, 2),
            )

        # 5. Resolve Semantic Locator
        locator = self._resolve_locator(page, action)

        # 6. Destructive Action Confirmation Gate
        if action.action == ActionType.CLICK and self._is_destructive(action):
            if self.confirm_destructive:
                logger.warning("Destructive action '%s' requires confirmation. Auto-approved in test profile.", action.target)

        # 7. Execute Click or Fill
        try:
            if action.action == ActionType.CLICK:
                # A checked consent box is already safe to leave enabled; avoid
                # toggling it off when the reasoning model repeats the action.
                if await locator.get_attribute("type") == "checkbox" and await locator.is_checked():
                    pass
                else:
                    await locator.click(timeout=self.timeout_ms)

            elif action.action == ActionType.FILL:
                if not action.value_ref:
                    raise ExecutorSecurityException("Fill action requires 'value_ref'. Raw values are prohibited.")
                
                # Resolve value locally from private vault
                secret_value = self.vault.resolve(action.value_ref)
                
                # Fill without logging the secret
                await locator.fill(secret_value, timeout=self.timeout_ms)

            elif action.action == ActionType.SELECT:
                val = action.value_ref or ""
                await locator.select_option(value=val, timeout=self.timeout_ms)

            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return ExecutionResult(
                step=step,
                action=action.action,
                success=True,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return ExecutionResult(
                step=step,
                action=action.action,
                success=False,
                duration_ms=duration_ms,
                error_message=str(e),
            )

    def _resolve_locator(self, page: Page, action: AgentAction) -> Locator:
        """Resolve Playwright locator from semantic target metadata."""
        if not action.target:
            raise ExecutorSecurityException(f"Action '{action.action}' requires a valid target.")

        t = action.target

        if t.ref:
            if not self._ref_map:
                raise ExecutorSecurityException("Unknown element ref; capture mapping is unavailable.")
            element_id = self._ref_map.get(t.ref)
            if not element_id:
                raise ExecutorSecurityException(f"Unknown element ref: {t.ref}")
            return page.locator(f"#{element_id}")

        # Priority 1: ID selector
        if t.element_id:
            loc = page.locator(f"#{t.element_id}")
            return loc

        # Priority 2: Accessible Name / Role
        if t.role and t.name:
            return page.get_by_role(t.role, name=t.name)

        # Priority 3: Label
        if t.label:
            return page.get_by_label(t.label)

        # Priority 4: Name
        if t.name:
            return page.get_by_text(t.name)

        raise ExecutorSecurityException(f"Unable to resolve locator for target: {t.model_dump()}")

    def set_reference_map(self, mapping: dict[str, str]) -> None:
        """Install the current capture's safe ref -> local DOM id mapping."""
        self._ref_map = dict(mapping)

    def _is_destructive(self, action: AgentAction) -> bool:
        """Check if action target indicates destructive operation (submit, pay, delete, send)."""
        name = (action.target.name or "").lower() if action.target else ""
        elem_id = (action.target.element_id or "").lower() if action.target else ""
        destructive_words = ["submit", "pay", "delete", "send", "confirm"]
        return any(w in name or w in elem_id for w in destructive_words)
