"""
Generic Configuration-Driven Mock VLM Test Oracle.

ARCHITECTURAL SEPARATION OF CONCERNS:
- This Mock Oracle is used exclusively for unit testing, offline CI, and automated test harnesses.
  It consults declarative SiteConfig definitions in demo_configs/ to act as a deterministic test oracle.
- The Real VLM implementation (server/vlm.py) NEVER consumes site configuration.
  The real VLM reasons strictly and exclusively from the sanitized JPEG screenshot,
  safe ScreenGraph, and user task prompt.
"""

from demo_sites.site_loader import registry
from shared.protocol import (
    ActionTarget,
    ActionType,
    AgentAction,
    ScreenContext,
)


class MockVLM:
    """Generic configuration-driven test oracle emulating VLM reasoning over forms."""

    def __init__(self) -> None:
        self.step_counter = 0

    def analyze(self, context: ScreenContext) -> AgentAction:
        self.step_counter += 1
        url = context.url.lower()

        # Success / terminal state check
        if "/success" in url or "success" in url:
            return AgentAction(
                action=ActionType.DONE,
                reason="Target workflow completed successfully. Verification confirmed.",
            )

        # Match route dynamically from declarative site registry
        found = registry.find_route(url)
        if not found:
            # Fallback for unconfigured or dynamic URLs
            return AgentAction(
                action=ActionType.DONE,
                reason=f"Reached unconfigured page: {context.url}",
            )

        site, route = found

        # Case A: Success template
        if route.template == "success":
            return AgentAction(
                action=ActionType.DONE,
                reason="Reached success terminal state in site configuration.",
            )

        # Case B: Login template (prefilled credentials advance with single click)
        if route.template == "login":
            submit_action = next((a for a in route.actions if a.is_submit), None) or (route.actions[0] if route.actions else None)
            target_id = submit_action.id if submit_action else "btn_login"
            target_name = submit_action.label if submit_action else "Sign In"
            return AgentAction(
                action=ActionType.CLICK,
                target=ActionTarget(kind="a11y", role="button", name=target_name, element_id=target_id),
                reason=f"Single-click authentication via {target_id}.",
            )

        # Case C: Multi-field form template
        fillable_fields = [f for f in route.fields if f.vault_ref]
        step_idx = context.step - 1  # 0-indexed form step

        if step_idx < len(fillable_fields):
            target_field = fillable_fields[step_idx]
            role = "textbox"
            return AgentAction(
                action=ActionType.FILL,
                target=ActionTarget(
                    kind="a11y",
                    role=role,
                    name=target_field.label,
                    element_id=target_field.id,
                ),
                value_ref=target_field.vault_ref,
                reason=f"Fill required field '{target_field.label}' from local vault reference '{target_field.vault_ref}'.",
            )

        # Any configured consent/control action can occur after fields and
        # before the configured submit action. No route name is inspected.
        post_fill_controls = [a for a in route.actions if a.role == "checkbox"]
        if post_fill_controls and context.step == len(fillable_fields) + 1:
            control = post_fill_controls[0]
            return AgentAction(
                action=ActionType.CLICK,
                target=ActionTarget(
                    kind="a11y",
                    role=control.role,
                    name=control.label,
                    element_id=control.id,
                ),
                reason=f"Complete configured control '{control.label}'.",
            )

        # All fields filled -> click submit action
        submit_action = next((a for a in route.actions if a.is_submit), None) or (route.actions[0] if route.actions else None)
        target_id = submit_action.id if submit_action else "btn_submit"
        target_name = submit_action.label if submit_action else "Submit"
        return AgentAction(
            action=ActionType.CLICK,
            target=ActionTarget(kind="a11y", role="button", name=target_name, element_id=target_id),
            reason=f"All form inputs completed; proceed to {target_name}.",
        )
