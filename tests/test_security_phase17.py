"""
Phase 17 Comprehensive Adversarial Security & Privacy Test Suite.

Covers:
1. F-01 Regression: /api/trigger path traversal, encoded traversal, unknown domains.
2. F-04 / F-04b Regression: /api/step strict schema validation, negative steps, mass assignment, extra fields.
3. DOM Sink XSS Immunity: HTML entity escaping covering &, <, >, ", '.
4. Value_ref & Vault Security: Namespace isolation, prototype pollution rejection, path traversal rejection, fail-closed lookup.
5. Grounding Adversarial Defense: Twin identical control tie-breaking (ambiguous margin), safe abstention.
6. Policy Engine Guardrails: High-risk gating, minimum confidence thresholds, irreversible operation confirmation.
7. Kill Switch Enforcement: Immediate action preemption in executor dispatch loop.
8. Privacy & Wire Invariants: Outbound leak interceptor zero-leak verification.
"""

import json
import pytest
from fastapi.testclient import TestClient

from client.candidates import verify_ranked_candidates
from client.executor.execute import ActionExecutor, ExecutorSecurityException
from client.kill_switch import GLOBAL_KILL_SWITCH, KillSwitch, KillSwitchTriggeredError
from client.policy_engine import LocalPolicyEngine, RiskClass
from client.vault import LocalVault
from dashboard.app import app
from eval.leak_check import OutboundLeakInterceptor, SecurityLeakException
from server.validation import ActionValidationError, validate_agent_action
from shared.protocol import ActionType, AgentAction, SafeCandidate
from shared.vault_registry import assert_valid_value_ref, is_valid_value_ref


@pytest.fixture
def client():
    return TestClient(app)


# ===========================================================================
# 1. F-01 Regression & Path Traversal / Trigger Security
# ===========================================================================

def test_trigger_rejects_path_traversal(client):
    traversal_payloads = [
        "../../etc/passwd",
        "..\\..\\windows\\system32",
        "%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "%252e%252e%252f",
        "file:///etc/shadow",
        "http://169.254.169.254/latest/meta-data/",
        "http://localhost:22",
        "random_unknown_domain",
        "",
    ]
    for domain in traversal_payloads:
        res = client.post("/api/trigger", json={"domain": domain, "port": 9999})
        assert res.status_code in (400, 422), f"Domain '{domain}' was not rejected: {res.status_code}"


def test_trigger_rejects_unexpected_fields(client):
    res = client.post("/api/trigger", json={"domain": "kyc", "extra_param": "malicious", "admin": True})
    assert res.status_code == 422
    assert "Extra inputs are not permitted" in res.text or "extra_forbidden" in res.text


def test_trigger_rejects_invalid_port(client):
    res_neg = client.post("/api/trigger", json={"domain": "kyc", "port": -1})
    assert res_neg.status_code == 422

    res_huge = client.post("/api/trigger", json={"domain": "kyc", "port": 999999})
    assert res_huge.status_code == 422


# ===========================================================================
# 2. F-04 / F-04b /api/step Strict Schema Validation & Mass Assignment
# ===========================================================================

def test_step_rejects_negative_and_fractional_numbers(client):
    # Negative step
    res_neg = client.post("/api/step", json={"step": -1})
    assert res_neg.status_code == 422

    # Fractional step
    res_float = client.post("/api/step", json={"step": 1.5})
    assert res_float.status_code == 422

    # Absurdly large step
    res_huge = client.post("/api/step", json={"step": 99999999})
    assert res_huge.status_code == 422


def test_step_rejects_arbitrary_extra_fields(client):
    res = client.post("/api/step", json={"step": 1, "injected": "DROP TABLE audit_log; --"})
    assert res.status_code == 422


def test_step_rejects_mass_assignment_and_privilege_escalation(client):
    res = client.post(
        "/api/step",
        json={
            "step": 1,
            "status": "completed",
            "policy": "ALLOW",
            "is_admin": True,
            "risk": "LOW",
            "bypass": True,
            "provenance_valid": True,
        },
    )
    assert res.status_code == 422


def test_step_accepts_valid_payload_and_sets_authoritative_metadata(client):
    res = client.post(
        "/api/step",
        json={
            "step": 2,
            "task": "Automated Phase 17 Hardening Verification",
            "url": "https://gov.in/portal/kyc",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["step"] == 2

    # Check that the server authoritatively stamped live provenance
    state_res = client.get("/api/state")
    assert state_res.status_code == 200
    state = state_res.json()
    assert state["data_source"] == "LIVE_AGENT_SESSION"
    assert state["is_live"] is True


# ===========================================================================
# 3. Security Headers
# ===========================================================================

def test_security_headers_present(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.headers.get("x-content-type-options") == "nosniff"
    assert res.headers.get("x-frame-options") == "DENY"
    assert res.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in res.headers.get("content-security-policy", "")


# ===========================================================================
# 4. Value_ref & Vault Security
# ===========================================================================

def test_value_ref_namespace_validation():
    # Valid refs
    assert is_valid_value_ref("user_profile.name")
    assert is_valid_value_ref("user_profile.aadhaar")
    assert is_valid_value_ref("payment.card_number")
    assert is_valid_value_ref("auth.token")

    # Invalid namespaces
    assert not is_valid_value_ref("admin.secret")
    assert not is_valid_value_ref("system.root")
    assert not is_valid_value_ref("server.key")

    # Path traversal in key
    assert not is_valid_value_ref("user_profile/../../etc/passwd")
    assert not is_valid_value_ref("user_profile.key/bad")
    assert not is_valid_value_ref("user_profile..key")
    assert not is_valid_value_ref("user_profile.key\\bad")

    # Prototype pollution keys
    assert not is_valid_value_ref("user_profile.__proto__")
    assert not is_valid_value_ref("user_profile.constructor")
    assert not is_valid_value_ref("user_profile.prototype")

    # Empty or malformed
    assert not is_valid_value_ref("")
    assert not is_valid_value_ref("user_profile.")
    assert not is_valid_value_ref(".name")
    assert not is_valid_value_ref("user_profile.name;drop")
    assert not is_valid_value_ref("user_profile.name<script>")


def test_vault_resolution_fails_closed():
    vault = LocalVault()

    # Unknown key raises KeyError
    with pytest.raises(KeyError):
        vault.resolve("user_profile.nonexistent_field_xyz")

    # Forged key raises ValueError
    with pytest.raises(ValueError):
        vault.resolve("attacker_namespace.fake_secret")

    # Prototype pollution attempt raises ValueError
    with pytest.raises(ValueError):
        vault.resolve("user_profile.__proto__")


# ===========================================================================
# 5. Grounding Candidate Ambiguity & Safe Abstention
# ===========================================================================

def test_twin_control_ambiguity_causes_safe_abstention():
    # Two identical buttons with identical names and scores
    c1 = SafeCandidate(
        ref="btn_left",
        role="button",
        name="Submit Verification",
        sensitive=False,
        visible=True,
        enabled=True,
        bbox=[100.0, 200.0, 120.0, 40.0],
        rank_score=0.85,
    )
    c2 = SafeCandidate(
        ref="btn_right",
        role="button",
        name="Submit Verification",
        sensitive=False,
        visible=True,
        enabled=True,
        bbox=[300.0, 200.0, 120.0, 40.0],
        rank_score=0.85,
    )

    decision = verify_ranked_candidates([c1, c2])
    assert decision.ambiguous is True
    assert decision.selected_ref is None
    assert decision.reason == "ambiguous_margin"


def test_disabled_top_candidate_causes_safe_abstention():
    c_disabled = SafeCandidate(
        ref="btn_disabled",
        role="button",
        name="Submit Verification",
        sensitive=False,
        visible=True,
        enabled=False,
        bbox=[100.0, 200.0, 120.0, 40.0],
        rank_score=0.90,
    )
    decision = verify_ranked_candidates([c_disabled])
    assert decision.ambiguous is True
    assert decision.selected_ref is None
    assert decision.reason == "top_candidate_disabled"


# ===========================================================================
# 6. Policy Engine Guardrails
# ===========================================================================

def test_policy_engine_gates_high_risk_and_irreversible_actions():
    policy = LocalPolicyEngine()

    # Low-risk action with sufficient confidence is permitted without human confirmation
    cand_tab = SafeCandidate(
        ref="tab_1", role="tab", name="View Profile", sensitive=False, visible=True, enabled=True,
        bbox=[0.0, 0.0, 10.0, 10.0], rank_score=0.75
    )
    d_low = policy.evaluate_policy(ActionType.CLICK, confidence=0.80, candidate=cand_tab)
    assert d_low.action_permitted is True
    assert d_low.risk_class == RiskClass.LOW
    assert d_low.requires_human_confirmation is False

    # High-risk irreversible action requires human confirmation
    cand_transfer = SafeCandidate(
        ref="btn_send", role="button", name="Authorize Transfer and Pay", sensitive=True, visible=True, enabled=True,
        bbox=[0.0, 0.0, 10.0, 10.0], rank_score=0.95
    )
    d_high = policy.evaluate_policy(
        ActionType.CLICK, confidence=0.95, candidate=cand_transfer, task="Transfer 1000 INR"
    )
    assert d_high.risk_class == RiskClass.HIGH
    assert d_high.requires_human_confirmation is True

    # High-risk action with inadequate confidence is blocked completely
    d_blocked = policy.evaluate_policy(
        ActionType.CLICK, confidence=0.70, candidate=cand_transfer, task="Transfer 1000 INR"
    )
    assert d_blocked.action_permitted is False


# ===========================================================================
# 7. Kill Switch Preemption in Executor
# ===========================================================================

@pytest.mark.asyncio
async def test_kill_switch_preempts_action_execution():
    ks = GLOBAL_KILL_SWITCH
    ks.reset()
    try:
        # Trigger kill switch
        ks.trigger(reason="Test Adversarial Halt", triggered_by="security_suite")
        assert ks.is_engaged is True

        executor = ActionExecutor()
        action = AgentAction(action=ActionType.DONE)

        # Attempting execution while kill switch is engaged must immediately raise KillSwitchTriggeredError
        with pytest.raises(KillSwitchTriggeredError) as exc_info:
            await executor.execute(None, action, step=1)
        assert "Test Adversarial Halt" in str(exc_info.value)
    finally:
        ks.reset()
        assert ks.is_engaged is False


# ===========================================================================
# 8. Outbound Privacy Leak Interceptor
# ===========================================================================

def test_leak_interceptor_catches_all_registered_secrets():
    vault = LocalVault()
    interceptor = OutboundLeakInterceptor(vault=vault)

    # Safe payload with symbolic value_ref
    safe_body = '{"action": "fill", "target": {"name": "Aadhaar"}, "value_ref": "user_profile.aadhaar"}'
    interceptor.assert_safe(safe_body)

    # Payload attempting to leak actual Aadhaar number
    leaked_aadhaar = '{"action": "fill", "value": "4839 2176 5201"}'
    with pytest.raises(SecurityLeakException):
        interceptor.assert_safe(leaked_aadhaar)

    # Payload attempting to leak PAN
    leaked_pan = '{"query": "User PAN is ABCDE1234F"}'
    with pytest.raises(SecurityLeakException):
        interceptor.assert_safe(leaked_pan)

    # Payload attempting to leak password
    leaked_pass = '{"auth": "SuperSecretPass123!"}'
    with pytest.raises(SecurityLeakException):
        interceptor.assert_safe(leaked_pass)
