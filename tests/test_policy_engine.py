"""Unit Tests for Local Safety Policy Engine (Phase 8.6)."""

import pytest
from client.policy_engine import LocalPolicyEngine, RiskClass
from shared.protocol import ActionType, SafeCandidate


def test_classify_low_risk():
    engine = LocalPolicyEngine()
    cand = SafeCandidate(ref="e1", role="link", name="Privacy Policy")
    risk = engine.classify_risk(ActionType.CLICK, cand, "Read Privacy Policy")
    assert risk == RiskClass.LOW

    scroll_risk = engine.classify_risk(ActionType.SCROLL)
    assert scroll_risk == RiskClass.LOW


def test_classify_medium_risk():
    engine = LocalPolicyEngine()
    cand = SafeCandidate(ref="e2", role="textbox", name="Search Products")
    risk = engine.classify_risk(ActionType.FILL, cand, "Search shoes")
    assert risk == RiskClass.MEDIUM


def test_classify_high_risk_by_keyword():
    engine = LocalPolicyEngine()
    cand = SafeCandidate(ref="e3", role="button", name="Delete Account Permanently")
    risk = engine.classify_risk(ActionType.CLICK, cand, "Delete Account")
    assert risk == RiskClass.HIGH


def test_classify_high_risk_by_sensitivity():
    engine = LocalPolicyEngine()
    cand = SafeCandidate(ref="e4", role="textbox", name="Tax ID", sensitive=True)
    risk = engine.classify_risk(ActionType.FILL, cand, "Enter Tax ID")
    assert risk == RiskClass.HIGH


def test_evaluate_policy_low_risk_permits():
    engine = LocalPolicyEngine()
    cand = SafeCandidate(ref="e1", role="tab", name="Overview")
    decision = engine.evaluate_policy(ActionType.CLICK, confidence=0.75, candidate=cand)
    assert decision.action_permitted is True
    assert decision.requires_human_confirmation is False


def test_evaluate_policy_high_risk_blocks_low_confidence():
    engine = LocalPolicyEngine()
    cand = SafeCandidate(ref="e_del", role="button", name="Delete Cluster")
    decision = engine.evaluate_policy(ActionType.CLICK, confidence=0.70, candidate=cand, task="Delete Cluster")
    # Requires confidence >= 0.88
    assert decision.action_permitted is False
    assert decision.risk_class == RiskClass.HIGH
    assert "High-risk action blocked" in decision.reason


def test_evaluate_policy_high_risk_requires_confirmation_when_irreversible():
    engine = LocalPolicyEngine()
    cand = SafeCandidate(ref="e_del", role="button", name="Delete Workspace")
    decision = engine.evaluate_policy(ActionType.CLICK, confidence=0.95, candidate=cand, task="Delete Workspace")
    assert decision.action_permitted is True
    assert decision.risk_class == RiskClass.HIGH
    assert decision.requires_human_confirmation is True
