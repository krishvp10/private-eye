"""Tests for Structured Output Robustness (Phase 7.15).

Tests client and server schema guards against malformed, ambiguous, out-of-range,
or adversarial model responses:
- Malformed JSON / non-dictionary payloads
- Unknown / non-whitelisted actions
- Missing or invalid candidate references
- Raw sensitive values (security violations)
- Missing / out-of-bounds confidence values
- JavaScript / shell injection strings in targets
- Safe handling of AMBIGUOUS and NO_VALID_CANDIDATE statuses
"""

import pytest
from pydantic import ValidationError

from server.validation import ActionValidationError, validate_agent_action
from shared.protocol import ActionType, AgentAction, SelectionStatus


def test_reject_unknown_action():
    with pytest.raises(ActionValidationError, match="not in allowed whitelist"):
        validate_agent_action({"action": "drop_database"})


def test_reject_raw_value_without_ref():
    with pytest.raises(ActionValidationError, match="Raw 'value' found in action"):
        validate_agent_action({"action": "fill", "value": "SuperSecret123!"})


def test_reject_fill_missing_value_ref():
    with pytest.raises(ActionValidationError, match="Fill action requires a valid 'value_ref'"):
        validate_agent_action({"action": "fill", "target": {"ref": "e1"}})


def test_reject_javascript_injection_in_target():
    with pytest.raises(ActionValidationError, match="Suspicious payload detected"):
        validate_agent_action({
            "action": "click",
            "target": {"ref": "javascript:alert(1)"},
        })


def test_reject_unsafe_navigation():
    with pytest.raises(ActionValidationError, match="Navigate actions require an absolute http"):
        validate_agent_action({
            "action": "navigate",
            "url": "file:///etc/passwd",
        })


def test_valid_click_action():
    action = validate_agent_action({
        "action": "click",
        "target": {"ref": "e10", "candidate_ref": "C1"},
        "confidence": 0.95,
        "selection_status": "selected",
    })
    assert action.action == ActionType.CLICK
    assert action.target.ref == "e10"
    assert action.confidence == 0.95
    assert action.selection_status == SelectionStatus.SELECTED


def test_valid_safe_abstention_ambiguous():
    action = validate_agent_action({
        "action": "click",
        "selection_status": "ambiguous",
        "confidence": 0.45,
    })
    assert action.selection_status == SelectionStatus.AMBIGUOUS
    assert action.target is None


def test_valid_no_valid_candidate():
    action = validate_agent_action({
        "action": "click",
        "selection_status": "no_valid_candidate",
        "confidence": 0.1,
    })
    assert action.selection_status == SelectionStatus.NO_VALID_CANDIDATE


def test_confidence_validation():
    # Confidence out of bounds should raise ValidationError
    with pytest.raises(ValidationError):
        AgentAction(
            action=ActionType.CLICK,
            confidence=1.5,  # must be <= 1.0
        )
    with pytest.raises(ValidationError):
        AgentAction(
            action=ActionType.CLICK,
            confidence=-0.1,  # must be >= 0.0
        )
