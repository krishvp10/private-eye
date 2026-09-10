"""
Unit tests for Real-VLM Outbound Packet Privacy Evidence Engine.
"""

import pytest

from eval.real_privacy_evidence import audit_wire_traffic
from shared.protocol import (
    ActionTarget,
    ActionType,
    AgentAction,
    ScreenContext,
    ScreenGraph,
    ScreenNode,
)


@pytest.fixture
def clean_context():
    root = ScreenNode(role="WebArea", name="KYC Form", id="root_0")
    return ScreenContext(
        run_id="test-clean-run",
        step=1,
        url="http://127.0.0.1:9001/kyc",
        image_b64="fake_sanitized_image_bytes",
        screen_graph=ScreenGraph(root=root, url="http://127.0.0.1:9001/kyc"),
        redactions=[],
        task="Complete KYC verification",
    )


@pytest.fixture
def clean_action():
    return AgentAction(
        action=ActionType.FILL,
        target=ActionTarget(kind="a11y", role="textbox", name="PAN", element_id="field_pan"),
        value_ref="user_profile.pan",
        reason="Filling PAN field via safe local reference",
    )


def test_clean_wire_traffic_passes(clean_context, clean_action):
    server_logs = "2026-09-10 19:25:01 [INFO] Step 1: URL=http://127.0.0.1:9001/kyc | Redactions=9 | Action=fill"
    evidence = audit_wire_traffic(clean_context, clean_action, server_logs)

    assert evidence["zero_leak_verified"] is True
    assert evidence["total_violations"] == 0
    assert evidence["secrets_tested_count"] > 10

    # Ensure all findings are marked PASS and ABSENT on wire
    for finding in evidence["findings"]:
        assert finding["status"] == "PASS"
        assert finding["request_wire_status"] == "ABSENT"
        assert finding["response_status"] == "ABSENT"
        assert finding["server_logs_status"] == "ABSENT"


def test_leaked_secret_in_request_is_detected(clean_action):
    # Context maliciously containing raw PAN in task or URL
    root = ScreenNode(role="WebArea", name="Leaked Context", id="root_0")
    leaked_context = ScreenContext(
        run_id="test-leaked-run",
        step=1,
        url="http://127.0.0.1:9001/kyc?leaked=ABCDE1234F",  # Raw PAN
        image_b64="fake_sanitized_image_bytes",
        screen_graph=ScreenGraph(root=root, url="http://127.0.0.1:9001/kyc"),
        redactions=[],
        task="Complete KYC verification with ABCDE1234F",
    )

    server_logs = "Clean server logs"
    evidence = audit_wire_traffic(leaked_context, clean_action, server_logs)

    assert evidence["zero_leak_verified"] is False
    assert evidence["total_violations"] >= 1

    pan_finding = next(f for f in evidence["findings"] if f["vault_ref"] == "user_profile.pan")
    assert pan_finding["status"] == "FAIL"
    assert pan_finding["request_wire_status"] == "LEAK_DETECTED"


def test_leaked_secret_in_server_logs_is_detected(clean_context, clean_action):
    server_logs_with_leak = (
        "2026-09-10 19:25:01 [ERROR] Failed to process PAN ABCDE1234F for user Rahul"
    )
    evidence = audit_wire_traffic(clean_context, clean_action, server_logs_with_leak)

    assert evidence["zero_leak_verified"] is False
    pan_finding = next(f for f in evidence["findings"] if f["vault_ref"] == "user_profile.pan")
    assert pan_finding["status"] == "FAIL"
    assert pan_finding["server_logs_status"] == "LEAK_DETECTED"
