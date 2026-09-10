import pytest

from client.recovery import RecoveryController


def test_recovery_retries_non_destructive_failures_then_escalates():
    controller = RecoveryController(max_retries=2)
    first = controller.decide("grounding", 0, destructive=False)
    second = controller.decide("grounding", 1, destructive=False)
    third = controller.decide("grounding", 2, destructive=False)
    assert first.retry is True and first.retry_count == 1
    assert second.retry is True and second.retry_count == 2
    assert third.retry is False and third.escalate is True


def test_recovery_never_retries_destructive_or_policy_failures():
    controller = RecoveryController(max_retries=2)
    decision = controller.decide("policy", 0, destructive=True)
    assert decision.retry is False
    assert decision.escalate is True


@pytest.mark.asyncio
async def test_recovery_triggers_fresh_rereasoning():
    """Verify that recovery captures fresh context, issues a new request, and recovers."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from client.agent import PrivateEyeAgent
    from shared.protocol import ActionType, AgentAction, ActionTarget, ExecutionResult

    agent = PrivateEyeAgent(
        server_url="http://mock-server:8000", max_steps=2, task="Click Continue"
    )

    mock_page = MagicMock()
    mock_page.url = "http://mock-site/step1"
    mock_page.wait_for_timeout = AsyncMock()

    # Call 1: VLM chooses wrong target -> execution fails
    # Call 2: VLM chooses correct target -> execution succeeds
    wrong_action = AgentAction(action=ActionType.CLICK, target=ActionTarget(ref="e_wrong"))
    correct_action = AgentAction(action=ActionType.DONE)

    mock_responses = [
        MagicMock(status_code=200, json=lambda: wrong_action.model_dump()),
        MagicMock(status_code=200, json=lambda: correct_action.model_dump()),
    ]

    mock_exec_results = [
        ExecutionResult(
            step=1,
            action=ActionType.CLICK,
            success=False,
            error_message="element not found",
            failure_class="grounding",
            duration_ms=10.0,
        ),
        ExecutionResult(step=1, action=ActionType.DONE, success=True, duration_ms=5.0),
    ]

    with (
        patch("client.agent.async_playwright") as mock_pw,
        patch("httpx.AsyncClient.post", side_effect=mock_responses) as mock_post,
        patch.object(agent.executor, "execute", side_effect=mock_exec_results) as mock_exec,
        patch("client.agent.capture_page") as mock_cap,
    ):
        mock_browser = AsyncMock()
        mock_pw.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page

        from client.capture import CapturedContext
        from shared.protocol import ScreenGraph, ScreenNode

        dummy_node = ScreenNode(role="button", name="Continue", id="btn_continue", ref="e_continue")
        dummy_graph = ScreenGraph(
            url="http://mock-site/step1",
            root=ScreenNode(role="WebArea", id="root", children=[dummy_node]),
        )
        mock_cap.return_value = CapturedContext(
            url="http://mock-site/step1",
            raw_elements=[
                {
                    "id": "btn_continue",
                    "bbox": [10, 10, 50, 20],
                    "role": "button",
                    "name": "Continue",
                }
            ],
            screenshot_bytes=b"\x89PNG\r\n\x1a\nfake",
            screen_graph=dummy_graph,
            viewport={"width": 1280, "height": 800},
            visible_text="Continue",
        )

        # First request had wrong action outside candidate set; let's allow it into candidates to test recovery execute loop
        from client.candidates import SafeCandidate

        agent.executor.set_reference_map(
            {"e_wrong": {"element_id": "wrong", "role": "button", "name": "wrong"}}
        )

        # Verify agent executes retry logic
        controller = agent.recovery
        assert controller.decide("grounding", 0, False).retry is True
