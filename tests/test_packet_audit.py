"""
Unit tests for the Verifiable Packet Audit Engine (eval/packet_audit.py).
"""

import json
import tempfile
from pathlib import Path

from client.vault import LocalVault
from eval.packet_audit import PacketAuditEngine, calculate_shannon_entropy


def test_shannon_entropy():
    # Constant string has 0 entropy
    assert calculate_shannon_entropy("AAAAAA") == 0.0
    # High diversity text has higher entropy
    h_entropy = calculate_shannon_entropy("4532-1148-9201-8842-AbCdEfG!#$")
    assert h_entropy > 3.0


def test_packet_audit_safe_payload():
    vault = LocalVault()
    engine = PacketAuditEngine(vault=vault)

    safe_payload = json.dumps({
        "run_id": "test-run-001",
        "step": 1,
        "action": {
            "action": "fill",
            "target": {"kind": "a11y", "element_id": "field_card_number"},
            "value_ref": "user_profile.card_number"
        },
        "sanitized_graph": {"nodes": []},
        "redactions": []
    })

    record = engine.audit_payload(safe_payload)
    assert record.passed is True
    assert record.violations_detected == 0
    assert record.byte_count == len(safe_payload.encode("utf-8"))
    assert len(record.sha256_hash) == 64


def test_packet_audit_catches_leaks():
    vault = LocalVault()
    engine = PacketAuditEngine(vault=vault)

    # Corrupt payload containing direct raw vault secret
    leaked_payload = json.dumps({
        "run_id": "test-run-leak",
        "raw_secret": "4532 1148 9201 8842"  # Credit card raw secret from vault
    })

    record = engine.audit_payload(leaked_payload)
    assert record.passed is False
    assert record.violations_detected >= 1
    assert "violations" in record.details


def test_audit_certificate_generation():
    vault = LocalVault()
    engine = PacketAuditEngine(vault=vault)

    safe_payload_1 = json.dumps({"step": 1, "status": "ok", "value_ref": "user_profile.name"})
    safe_payload_2 = json.dumps({"step": 2, "status": "ok", "value_ref": "user_profile.card_number"})

    engine.audit_payload(safe_payload_1)
    engine.audit_payload(safe_payload_2)

    with tempfile.TemporaryDirectory() as tmpdir:
        cert_path = Path(tmpdir) / "audit_certificate.json"
        cert = engine.generate_certificate(output_path=str(cert_path))

        assert cert.certified_zero_leak is True
        assert cert.total_packets_inspected == 2
        assert cert.raw_pii_leaks_found == 0
        assert cert.compliance_status == "CERTIFIED_100_PERCENT_ZERO_RAW_PII_EXPOSURE"
        assert cert_path.exists()

        saved_data = json.loads(cert_path.read_text(encoding="utf-8"))
        assert saved_data["certified_zero_leak"] is True
        assert saved_data["total_packets_inspected"] == 2
