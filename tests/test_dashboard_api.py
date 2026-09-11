"""
Unit tests for PrivateEye Dashboard FastAPI endpoints.
Validates state streaming, domain discovery, evidence, audit, privacy, policy, security,
and emergency kill-switch endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from dashboard.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "PrivateEye" in res.text


def test_api_state(client):
    res = client.get("/api/state")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "metrics" in data


def test_api_domains(client):
    res = client.get("/api/domains")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "entry_route" in data[0]


def test_api_evidence(client):
    res = client.get("/api/evidence")
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    summary = data["summary"]
    assert "89/100" in summary["phase10_task_success"]
    assert "86/100" in summary["phase11_heldout_task_success"]
    assert summary["secret_leaks"] == 0
    assert "15/15" in summary["prompt_injection_blocked"]
    assert "20/20" in summary["single_fault_contained"]
    assert "10/10" in summary["compound_fault_contained"]
    assert summary["kill_switch_dispatch_ms"] == 0.043


def test_api_audit(client):
    res = client.get("/api/audit")
    assert res.status_code == 200
    data = res.json()
    assert "certificate" in data
    assert "records" in data
    assert len(data["records"]) > 0
    # Zero leaks verified in audit
    for rec in data["records"]:
        assert rec["risk"] in ["LOW", "MEDIUM", "HIGH"]
        assert "provenance_hash" in rec


def test_api_privacy(client):
    res = client.get("/api/privacy")
    assert res.status_code == 200
    data = res.json()
    assert "detector_metrics" in data
    assert data["detector_metrics"]["secret_leaks_detected"] == 0
    assert "vault_schema" in data
    assert len(data["vault_schema"]) >= 4
    # Ensure all vault items have synthetic masks, no raw secrets
    for item in data["vault_schema"]:
        assert "$VAULT:" in item["value_ref"]
        assert "••••" in item["synthetic_mask"]


def test_api_policy(client):
    res = client.get("/api/policy")
    assert res.status_code == 200
    data = res.json()
    assert "OWASP" in data["standard"]
    assert "risk_tiers" in data
    assert len(data["risk_tiers"]) == 3
    tiers = {t["tier"]: t for t in data["risk_tiers"]}
    assert tiers["HIGH"]["human_gate"] is True
    assert tiers["LOW"]["human_gate"] is False


def test_api_security_and_kill_switch(client):
    res = client.get("/api/security")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PROTECTED"
    assert data["prompt_injection"]["tested_cases"] == 15
    assert data["prompt_injection"]["blocked_cases"] == 15

    # Trigger kill switch
    res_kill = client.post("/api/kill-switch", json={"reason": "Automated Unit Test Halt"})
    assert res_kill.status_code == 200
    kill_data = res_kill.json()
    assert kill_data["status"] == "engaged"
    assert "measured_dispatch_ms" in kill_data
    assert kill_data["measured_dispatch_ms"] >= 0.0

    # Reset kill switch
    res_reset = client.post("/api/kill-switch/reset")
    assert res_reset.status_code == 200
    assert res_reset.json()["status"] == "disarmed"
