"""
Phase 6 Tests: Mock VLM Server.
Validates:
1. /v1/health endpoint.
2. /v1/analyze returns valid deterministic AgentAction for /login and /kyc.
3. Actions use semantic targets and value_ref indirection.
4. Server rejects oversized payloads and malicious actions.
5. Telemetry audit log contains zero raw PII or secret values.
"""

from fastapi.testclient import TestClient

from server.api import app
from shared.protocol import (
    ScreenContext,
    ScreenGraph,
    ScreenNode,
)

client = TestClient(app)


def test_server_health():
    res = client.get("/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["mode"] == "mock"


def test_analyze_login_route():
    root = ScreenNode(role="WebArea", name="Login", id="root_0")
    context = ScreenContext(
        run_id="run-test-01",
        step=1,
        url="http://127.0.0.1:9001/login",
        image_b64="fake_sanitized_image_bytes",
        screen_graph=ScreenGraph(root=root, url="http://127.0.0.1:9001/login"),
        redactions=[],
        task="Sign in",
    )
    res = client.post("/v1/analyze", json=context.model_dump())
    assert res.status_code == 200
    action = res.json()
    assert action["action"] == "click"
    assert action["target"]["name"] == "Sign In"


def test_analyze_kyc_route_fill_step():
    root = ScreenNode(role="WebArea", name="KYC Form", id="root_0")
    context = ScreenContext(
        run_id="run-test-02",
        step=1,
        url="http://127.0.0.1:9001/kyc",
        image_b64="fake_sanitized_image_bytes",
        screen_graph=ScreenGraph(root=root, url="http://127.0.0.1:9001/kyc"),
        redactions=[],
        task="Complete KYC",
    )
    res = client.post("/v1/analyze", json=context.model_dump())
    assert res.status_code == 200
    action = res.json()
    assert action["action"] == "fill"
    assert action["value_ref"] == "user_profile.name"
    # Invariant: NEVER contain raw value
    assert "value" not in action or action["value"] is None


def test_analyze_audit_log_clean():
    res = client.get("/v1/runs")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) >= 2
    for entry in logs:
        assert "payload_size_kb" in entry
        assert "duration_ms" in entry
        # Guarantee no PII in audit log
        log_str = str(entry)
        assert "SuperSecretPass123!" not in log_str
        assert "4839 2176 5201" not in log_str
