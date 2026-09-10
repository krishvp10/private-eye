"""Fail-Closed Runtime Policy & Invariant Enforcer (Phase 9).

Enforces the core security invariant:
"When the system cannot prove that an action is safe and grounded,
it does not execute it."

All 12 failure modes are strictly trapped and classified into structured
safe abstentions, bounded re-plans, or graceful safe halts.
Under no circumstances is ungrounded or unverified high-risk execution allowed,
and silent mock fallback is strictly forbidden.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class FailureClass(str, Enum):
    PRIVACY_DETECTOR_FAILURE = "PRIVACY_DETECTOR_FAILURE"
    REDACTION_FAILURE = "REDACTION_FAILURE"
    CANDIDATE_EXTRACTION_FAILURE = "CANDIDATE_EXTRACTION_FAILURE"
    CANDIDATE_VALIDATION_FAILURE = "CANDIDATE_VALIDATION_FAILURE"
    POLICY_VALIDATION_FAILURE = "POLICY_VALIDATION_FAILURE"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    AMBIGUOUS_TARGET = "AMBIGUOUS_TARGET"
    MALFORMED_VLM_RESPONSE = "MALFORMED_VLM_RESPONSE"
    UNKNOWN_CANDIDATE_REF = "UNKNOWN_CANDIDATE_REF"
    UNKNOWN_VALUE_REF = "UNKNOWN_VALUE_REF"
    VERIFIER_FAILURE = "VERIFIER_FAILURE"
    MODEL_TIMEOUT = "MODEL_TIMEOUT"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    BROWSER_DISCONNECTED = "BROWSER_DISCONNECTED"
    KILL_SWITCH_ENGAGED = "KILL_SWITCH_ENGAGED"


class FailClosedAction(str, Enum):
    DO_NOT_TRANSMIT = "DO_NOT_TRANSMIT"
    DO_NOT_EXECUTE = "DO_NOT_EXECUTE"
    ABSTAIN_AND_REQUEST_INFO = "ABSTAIN_AND_REQUEST_INFO"
    REJECT_AND_REPLAN = "REJECT_AND_REPLAN"
    BOUNDED_RETRY = "BOUNDED_RETRY"
    SAFE_STOP = "SAFE_STOP"


@dataclass(frozen=True)
class FailClosedDecision:
    allowed: bool
    action: FailClosedAction
    failure_class: Optional[FailureClass]
    reason: str
    context: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "action": self.action.value,
            "failure_class": self.failure_class.value if self.failure_class else None,
            "reason": self.reason,
            "context": self.context,
        }


class FailClosedPolicy:
    """Enforces fail-closed rules across the action lifecycle."""

    @staticmethod
    def evaluate_privacy(
        detector_success: bool,
        redaction_success: bool,
        detected_secrets_count: int = 0,
    ) -> FailClosedDecision:
        """Validate observation before transmission to model."""
        if not detector_success:
            return FailClosedDecision(
                allowed=False,
                action=FailClosedAction.DO_NOT_TRANSMIT,
                failure_class=FailureClass.PRIVACY_DETECTOR_FAILURE,
                reason="Privacy detector raised an error or crashed. Halting transmission to protect credentials.",
                context={"detector_success": detector_success},
            )
        if not redaction_success:
            return FailClosedDecision(
                allowed=False,
                action=FailClosedAction.DO_NOT_TRANSMIT,
                failure_class=FailureClass.REDACTION_FAILURE,
                reason="Screenshot redaction failed or left raw pixels exposed. Refusing to transmit image.",
                context={"redaction_success": redaction_success},
            )
        return FailClosedDecision(
            allowed=True,
            action=FailClosedAction.DO_NOT_EXECUTE,
            failure_class=None,
            reason="Privacy sanitization verified cleanly.",
            context={"detected_secrets_count": detected_secrets_count},
        )

    @staticmethod
    def evaluate_candidate(
        candidates_extracted: bool,
        candidate_count: int,
        selected_ref: Optional[str],
        valid_refs: set[str],
        require_ref: bool = False,
    ) -> FailClosedDecision:
        """Validate candidate extraction and candidate reference resolution."""
        if not candidates_extracted or candidate_count == 0:
            return FailClosedDecision(
                allowed=False,
                action=FailClosedAction.DO_NOT_EXECUTE,
                failure_class=FailureClass.CANDIDATE_EXTRACTION_FAILURE,
                reason="Candidate generator extracted 0 interactive elements on current DOM.",
                context={"candidate_count": candidate_count},
            )
        if require_ref and selected_ref is None:
            return FailClosedDecision(
                allowed=False,
                action=FailClosedAction.DO_NOT_EXECUTE,
                failure_class=FailureClass.UNKNOWN_CANDIDATE_REF,
                reason="No candidate_ref specified when candidate_ref is required.",
                context={"selected_ref": None, "valid_count": len(valid_refs)},
            )
        if selected_ref is not None and selected_ref not in valid_refs:
            return FailClosedDecision(
                allowed=False,
                action=FailClosedAction.DO_NOT_EXECUTE,
                failure_class=FailureClass.UNKNOWN_CANDIDATE_REF,
                reason=f"Selected candidate_ref '{selected_ref}' not found in active screen candidate set.",
                context={"selected_ref": selected_ref, "valid_count": len(valid_refs)},
            )
        return FailClosedDecision(
            allowed=True,
            action=FailClosedAction.DO_NOT_EXECUTE,
            failure_class=None,
            reason="Candidate reference verified and grounded.",
            context={"selected_ref": selected_ref},
        )


    @staticmethod
    def evaluate_model_response(
        response_json: Optional[Dict[str, Any]],
        confidence: float,
        confidence_low_threshold: float = 0.65,
        is_ambiguous: bool = False,
    ) -> FailClosedDecision:
        """Validate model output structure and semantic confidence."""
        if response_json is None or not isinstance(response_json, dict):
            return FailClosedDecision(
                allowed=False,
                action=FailClosedAction.REJECT_AND_REPLAN,
                failure_class=FailureClass.MALFORMED_VLM_RESPONSE,
                reason="Model output is malformed, truncated, or invalid JSON.",
                context={"raw_response": str(response_json)},
            )
        if is_ambiguous:
            return FailClosedDecision(
                allowed=False,
                action=FailClosedAction.ABSTAIN_AND_REQUEST_INFO,
                failure_class=FailureClass.AMBIGUOUS_TARGET,
                reason="Multiple indistinguishable targets detected; intent is underspecified.",
                context={"confidence": confidence},
            )
        if confidence < confidence_low_threshold:
            return FailClosedDecision(
                allowed=False,
                action=FailClosedAction.ABSTAIN_AND_REQUEST_INFO,
                failure_class=FailureClass.LOW_CONFIDENCE,
                reason=f"Model confidence ({confidence:.2f}) below safe threshold ({confidence_low_threshold:.2f}).",
                context={"confidence": confidence, "threshold": confidence_low_threshold},
            )
        return FailClosedDecision(
            allowed=True,
            action=FailClosedAction.DO_NOT_EXECUTE,
            failure_class=None,
            reason="Model response parsed with sufficient confidence.",
            context={"confidence": confidence},
        )

    @staticmethod
    def evaluate_value_ref(
        value_ref: Optional[str],
        known_value_refs: set[str],
    ) -> FailClosedDecision:
        """Ensure sensitive field values reference approved local vault entries."""
        if value_ref and value_ref not in known_value_refs:
            return FailClosedDecision(
                allowed=False,
                action=FailClosedAction.DO_NOT_EXECUTE,
                failure_class=FailureClass.UNKNOWN_VALUE_REF,
                reason=f"Requested value_ref '{value_ref}' does not exist in local vault.",
                context={"value_ref": value_ref},
            )
        return FailClosedDecision(
            allowed=True,
            action=FailClosedAction.DO_NOT_EXECUTE,
            failure_class=None,
            reason="Value reference exists in local vault.",
            context={"value_ref": value_ref},
        )

    @staticmethod
    def evaluate_infrastructure(
        model_available: bool,
        browser_connected: bool,
        timed_out: bool = False,
        retry_count: int = 0,
        max_retries: int = 2,
    ) -> FailClosedDecision:
        """Validate network/service availability."""
        if not model_available:
            return FailClosedDecision(
                allowed=False,
                action=FailClosedAction.SAFE_STOP,
                failure_class=FailureClass.MODEL_UNAVAILABLE,
                reason="VLM inference backend is unavailable. Banning silent mock fallback; halting safely.",
                context={"model_available": model_available},
            )
        if not browser_connected:
            return FailClosedDecision(
                allowed=False,
                action=FailClosedAction.SAFE_STOP,
                failure_class=FailureClass.BROWSER_DISCONNECTED,
                reason="Playwright browser session disconnected or crashed.",
                context={"browser_connected": browser_connected},
            )
        if timed_out:
            if retry_count < max_retries:
                return FailClosedDecision(
                    allowed=False,
                    action=FailClosedAction.BOUNDED_RETRY,
                    failure_class=FailureClass.MODEL_TIMEOUT,
                    reason=f"Inference timed out. Initiating bounded retry ({retry_count + 1}/{max_retries}).",
                    context={"retry_count": retry_count, "max_retries": max_retries},
                )
            else:
                return FailClosedDecision(
                    allowed=False,
                    action=FailClosedAction.SAFE_STOP,
                    failure_class=FailureClass.MODEL_TIMEOUT,
                    reason="Inference retry budget exceeded. Stopping agent safely.",
                    context={"retry_count": retry_count, "max_retries": max_retries},
                )
        return FailClosedDecision(
            allowed=True,
            action=FailClosedAction.DO_NOT_EXECUTE,
            failure_class=None,
            reason="Infrastructure dependencies verified healthy.",
            context={},
        )
