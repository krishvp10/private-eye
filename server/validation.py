"""
Server-side action validation and schema guard (LLM01 Prompt Injection defense).
Ensures any action emitted by a VLM conforms strictly to safe operations.
"""

from typing import Any
from urllib.parse import urlparse

from shared.protocol import ActionType, AgentAction


class ActionValidationError(Exception):
    """Raised when an action violates safety or schema constraints."""


ALLOWED_ACTIONS = {action.value for action in ActionType}


def validate_agent_action(action_dict: dict[str, Any]) -> AgentAction:
    """
    Strictly validate and parse an incoming action from the VLM.
    Rejects:
    - Arbitrary JavaScript / eval
    - Shell commands
    - Raw secrets in fill
    - Non-whitelisted action verbs
    """
    raw_action = action_dict.get("action")
    if raw_action not in ALLOWED_ACTIONS:
        raise ActionValidationError(
            f"Action '{raw_action}' is not in allowed whitelist: {sorted(ALLOWED_ACTIONS)}"
        )

    # Check for raw secret exposure
    if "value" in action_dict and not action_dict.get("value_ref"):
        raise ActionValidationError(
            "Security policy violation: Raw 'value' found in action. Must use 'value_ref'."
        )

    # If action is fill, value_ref is required
    if raw_action == ActionType.FILL.value and not action_dict.get("value_ref"):
        raise ActionValidationError("Fill action requires a valid 'value_ref'.")

    # Reject suspicious strings in targets or values
    target = action_dict.get("target") or {}
    for key, val in target.items():
        if isinstance(val, str):
            lower_val = val.lower()
            if any(forbidden in lower_val for forbidden in ["javascript:", "<script", "exec(", "eval("]):
                raise ActionValidationError(f"Suspicious payload detected in target {key}: '{val}'")

    if raw_action == ActionType.NAVIGATE.value:
        url = action_dict.get("url")
        parsed = urlparse(url or "")
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ActionValidationError("Navigate actions require an absolute http(s) URL.")
        if any(token in (url or "").lower() for token in ["javascript:", "data:", "file:", "localhost:"]):
            raise ActionValidationError("Navigate URL is not permitted by the server policy.")

    value_ref = action_dict.get("value_ref")
    if value_ref is not None:
        if not isinstance(value_ref, str) or not value_ref.startswith("user_profile."):
            raise ActionValidationError("value_ref must reference the local user_profile vault.")
        if len(value_ref) > 80 or any(token in value_ref.lower() for token in ["..", "/", "\\", ":", " "]):
            raise ActionValidationError("value_ref contains forbidden characters.")

    return AgentAction.model_validate(action_dict)
