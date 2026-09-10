"""Unit tests for Phase 9 Run Manifest, Fail-Closed Policy, Kill Switch, and Provenance."""

import pytest
from pathlib import Path

from client.manifest import create_run_manifest, RunManifest
from client.release_config import FROZEN_RELEASE_CONFIG, ReleaseConfig
from client.fail_closed import FailClosedPolicy, FailureClass, FailClosedAction
from client.kill_switch import KillSwitch, KillSwitchTriggeredError
from client.provenance import ActionProvenance, ProvenanceTracker


def test_manifest_creation():
    manifest = create_run_manifest(
        benchmark_id="test_suite_v9",
        model="qwen2.5-vl:3b",
        resolution=768,
        temperature=0.0,
    )
    assert isinstance(manifest, RunManifest)
    assert manifest.model == "qwen2.5-vl:3b"
    assert manifest.resolution == 768
    assert manifest.benchmark_id == "test_suite_v9"
    assert manifest.commit_sha != ""
    assert "os" in manifest.environment
    assert "python" in manifest.environment

    d = manifest.to_dict()
    assert d["candidate_k"] == 5
    assert d["verifier_mode"] == "selective"
    assert d["fail_closed_enabled"] is True


def test_release_config_immutability():
    cfg = FROZEN_RELEASE_CONFIG
    assert cfg.version == "v1.0-RC"
    assert cfg.model == "qwen2.5-vl:3b"
    assert cfg.resolution == 768
    assert cfg.temperature == 0.0
    assert cfg.verifier_mode == "selective"
    assert cfg.policy_engine is True
    assert cfg.fail_closed is True
    assert cfg.human_confirmation_high_risk is True


def test_fail_closed_privacy_gate():
    # Healthy case
    d1 = FailClosedPolicy.evaluate_privacy(True, True, detected_secrets_count=2)
    assert d1.allowed is True
    assert d1.failure_class is None

    # Detector error -> DO_NOT_TRANSMIT
    d2 = FailClosedPolicy.evaluate_privacy(False, True)
    assert d2.allowed is False
    assert d2.action == FailClosedAction.DO_NOT_TRANSMIT
    assert d2.failure_class == FailureClass.PRIVACY_DETECTOR_FAILURE

    # Redaction error -> DO_NOT_TRANSMIT
    d3 = FailClosedPolicy.evaluate_privacy(True, False)
    assert d3.allowed is False
    assert d3.action == FailClosedAction.DO_NOT_TRANSMIT
    assert d3.failure_class == FailureClass.REDACTION_FAILURE


def test_fail_closed_candidates_and_refs():
    # 0 candidates extracted -> DO_NOT_EXECUTE
    d1 = FailClosedPolicy.evaluate_candidate(False, 0, "c1", {"c1", "c2"})
    assert d1.allowed is False
    assert d1.failure_class == FailureClass.CANDIDATE_EXTRACTION_FAILURE

    # Unknown candidate ref -> DO_NOT_EXECUTE
    d2 = FailClosedPolicy.evaluate_candidate(True, 5, "unknown_ref", {"c1", "c2"})
    assert d2.allowed is False
    assert d2.failure_class == FailureClass.UNKNOWN_CANDIDATE_REF

    # Valid candidate
    d3 = FailClosedPolicy.evaluate_candidate(True, 5, "c1", {"c1", "c2"})
    assert d3.allowed is True


def test_fail_closed_model_response():
    # Malformed response
    d1 = FailClosedPolicy.evaluate_model_response(None, 0.9)
    assert d1.allowed is False
    assert d1.failure_class == FailureClass.MALFORMED_VLM_RESPONSE

    # Low confidence
    d2 = FailClosedPolicy.evaluate_model_response({"action": "click"}, 0.42, confidence_low_threshold=0.65)
    assert d2.allowed is False
    assert d2.failure_class == FailureClass.LOW_CONFIDENCE

    # Ambiguous target
    d3 = FailClosedPolicy.evaluate_model_response({"action": "click"}, 0.89, is_ambiguous=True)
    assert d3.allowed is False
    assert d3.failure_class == FailureClass.AMBIGUOUS_TARGET


def test_fail_closed_infrastructure():
    # Model unavailable -> Safe stop, no silent fallback
    d1 = FailClosedPolicy.evaluate_infrastructure(model_available=False, browser_connected=True)
    assert d1.allowed is False
    assert d1.action == FailClosedAction.SAFE_STOP
    assert d1.failure_class == FailureClass.MODEL_UNAVAILABLE

    # Browser disconnected -> Safe stop
    d2 = FailClosedPolicy.evaluate_infrastructure(model_available=True, browser_connected=False)
    assert d2.allowed is False
    assert d2.action == FailClosedAction.SAFE_STOP
    assert d2.failure_class == FailureClass.BROWSER_DISCONNECTED

    # Model timeout within retry budget
    d3 = FailClosedPolicy.evaluate_infrastructure(True, True, timed_out=True, retry_count=0, max_retries=2)
    assert d3.allowed is False
    assert d3.action == FailClosedAction.BOUNDED_RETRY

    # Model timeout exceeding budget
    d4 = FailClosedPolicy.evaluate_infrastructure(True, True, timed_out=True, retry_count=2, max_retries=2)
    assert d4.allowed is False
    assert d4.action == FailClosedAction.SAFE_STOP


def test_kill_switch_lifecycle():
    ks = KillSwitch()
    assert not ks.is_engaged
    ks.assert_not_engaged()

    # Trigger kill switch
    ev = ks.trigger(reason="Test kill switch trigger", triggered_by="tester", interrupted_step=3)
    assert ks.is_engaged
    assert ev.reason == "Test kill switch trigger"
    assert ev.interrupted_step == 3

    with pytest.raises(KillSwitchTriggeredError) as exc:
        ks.assert_not_engaged()
    assert "Test kill switch trigger" in str(exc.value)

    # Reset
    ks.reset()
    assert not ks.is_engaged
    ks.assert_not_engaged()


def test_provenance_recording(tmp_path: Path):
    tracker = ProvenanceTracker(task_id="kyc_form_task")
    prov = ActionProvenance(
        task_id="kyc_form_task",
        step_id=1,
        user_goal="Fill SSN",
        model="qwen2.5-vl:3b",
        model_decision="fill",
        candidate_ref="c3",
        candidate_source="Playwright",
        candidate_score=0.92,
        verifier_used=False,
        verifier_result=None,
        confidence=0.94,
        risk_level="HIGH",
        policy_decision="allow_with_local_vault",
        human_confirmation_required=False,
        human_confirmed=False,
        execution_result="PASS",
        post_condition_result="PASS",
        progress_state="advanced",
        retry_count=0,
        failure_class=None,
        started_at_utc="2026-09-11T00:00:00Z",
        completed_at_utc="2026-09-11T00:00:01Z",
        latency_ms_components={"vlm": 7100.0, "local": 45.0},
        rationale="Selected input field matching SSN label.",
    )
    tracker.record(prov)
    assert len(tracker.records) == 1
    expl = tracker.get_explanations()[0]
    assert "SSN" in expl
    assert "Score: 0.920" in expl

    json_file = tmp_path / "provenance.json"
    tracker.save(json_file)
    assert json_file.exists()
    assert "kyc_form_task" in json_file.read_text(encoding="utf-8")
