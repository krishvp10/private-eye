import json

from server.vlm import VLMAdapter
from shared.protocol import ScreenContext, ScreenGraph, ScreenNode


def test_progress_state_is_serialized_without_sensitive_values(monkeypatch):
    monkeypatch.setenv("PRIVATEEYE_VLM_MODE", "real")
    context = ScreenContext(
        run_id="progress-test",
        step=2,
        url="https://example.test/login",
        image_b64="SANITIZED",
        screen_graph=ScreenGraph(
            url="https://example.test/login",
            root=ScreenNode(role="WebArea", id="root", children=[]),
        ),
        task="Sign in",
        previous_action={"action": "click", "candidate_ref": "e10"},
        previous_execution_success=True,
        previous_post_condition_success=False,
        previous_failure_class="no_progress",
    )

    payload = json.dumps(VLMAdapter().build_request(context))

    assert "no_progress" in payload
    assert "candidate_ref" in payload
    assert "ABCDE1234F" not in payload
    assert "SuperSecretPass123!" not in payload
