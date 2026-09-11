"""Integration tests for Authoritative Policy Engine enforcement (Phase 15).
Proves that the real PrivateEyeAgent execution path crosses LocalPolicyEngine,
blocking unpermitted, high-risk, or low-confidence actions before Playwright dispatch.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from client.agent import PrivateEyeAgent
from client.candidates import GroundingDecision
from client.policy_engine import LocalPolicyEngine, PolicyDecision, RiskClass
from shared.protocol import (
    SafeCandidate,
    ScreenGraph,
    ScreenNode,
)


def test_agent_has_authoritative_policy_engine():
    """Verify that PrivateEyeAgent always instantiates and holds LocalPolicyEngine."""
    agent = PrivateEyeAgent()
    assert hasattr(agent, "policy_engine"), "PrivateEyeAgent missing policy_engine attribute"
    assert isinstance(agent.policy_engine, LocalPolicyEngine), (
        "Agent policy_engine must be instance of LocalPolicyEngine"
    )


def test_custom_policy_engine_injection():
    """Verify custom LocalPolicyEngine instance can be injected for strict domains."""
    custom_engine = LocalPolicyEngine(
        high_confidence_threshold=0.95, medium_confidence_threshold=0.80
    )
    agent = PrivateEyeAgent(policy_engine=custom_engine)
    assert agent.policy_engine.high_conf == 0.95
    assert agent.policy_engine.med_conf == 0.80


@pytest.mark.asyncio
async def test_policy_engine_blocks_unpermitted_action_in_agent_run():
    """Prove that if LocalPolicyEngine refuses an action, agent.run halts fail-closed."""
    agent = PrivateEyeAgent()
    # Configure mock policy engine that strictly blocks any action
    strict_policy = MagicMock(spec=LocalPolicyEngine)
    strict_policy.evaluate_policy.return_value = PolicyDecision(
        action_permitted=False,
        risk_class=RiskClass.HIGH,
        requires_human_confirmation=True,
        requires_verifier=True,
        min_confidence_required=0.88,
        reason="Security test block: action prohibited by policy",
    )
    agent.policy_engine = strict_policy

    # Mock server response returning a CLICK action
    mock_action_response = {
        "action": "click",
        "target": {"ref": "c1", "name": "Unauthorized Submit"},
        "selection_status": "selected",
        "confidence": 0.95,
    }

    with (
        patch("client.agent.async_playwright") as mock_pw,
        patch("httpx.AsyncClient.post") as mock_post,
        patch("client.agent.capture_page") as mock_cap,
        patch("client.agent.generate_candidates") as mock_gc,
        patch("client.agent.verify_ranked_candidates") as mock_vc,
    ):
        # Setup mocks
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.url = "http://test.local/form"
        mock_browser.new_page.return_value = mock_page
        mock_pw_context = AsyncMock()
        mock_pw_context.chromium.launch.return_value = mock_browser
        mock_pw.return_value.__aenter__.return_value = mock_pw_context

        # Mock capture with valid PNG bytes
        import io

        from PIL import Image

        buf = io.BytesIO()
        Image.new("RGB", (100, 100), color="white").save(buf, format="PNG")
        cap_result = MagicMock()
        cap_result.raw_elements = []
        cap_result.screenshot_bytes = buf.getvalue()
        cap_result.visible_text = "Test page"
        cap_result.viewport = {"width": 1280, "height": 800}
        cap_result.screen_graph = ScreenGraph(
            url="http://test.local/form",
            root=ScreenNode(id="root", role="page", children=[]),
        )
        mock_cap.return_value = cap_result

        # Mock candidates
        cand = SafeCandidate(
            ref="c1", role="button", name="Unauthorized Submit", bbox=[0, 0, 100, 30]
        )
        mock_gc.return_value = [cand]
        mock_vc.return_value = GroundingDecision(
            selected_ref="c1",
            confidence=0.95,
            ambiguous=False,
            reason="Clear candidate",
        )

        # Mock VLM HTTP response
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_action_response
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        # Spy on executor
        agent.executor.execute = AsyncMock()

        # Run agent
        result = await agent.run("http://test.local/form")

        # Verify: Policy engine was evaluated
        assert strict_policy.evaluate_policy.called, (
            "LocalPolicyEngine MUST be evaluated during agent.run"
        )

        # Verify: Action was blocked fail-closed
        assert result.success is False
        assert any("policy engine blocked" in err.lower() for err in result.errors)

        # Verify: Playwright executor was NEVER called!
        assert not agent.executor.execute.called, (
            "Executor execute MUST NOT be called when policy forbids action"
        )
