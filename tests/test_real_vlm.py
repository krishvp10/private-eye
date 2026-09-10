import json

import pytest

from server.vlm import VLMAdapter
from shared.protocol import (
    ActionType,
    ImageMeta,
    ScreenContext,
    ScreenGraph,
    ScreenNode,
)


def context() -> ScreenContext:
    return ScreenContext(
        run_id="real-vlm-test",
        step=1,
        url="https://example.test/kyc",
        image_b64="SANITIZED_IMAGE",
        screen_graph=ScreenGraph(
            url="https://example.test/kyc",
            root=ScreenNode(
                role="WebArea",
                id="root",
                children=[
                    ScreenNode(role="button", name="Continue", id="continue", ref="e1"),
                    ScreenNode(role="textbox", name="PAN", id="pan", ref="e2", sensitive=True),
                ],
            ),
        ),
        task="Continue",
    )


def test_real_request_contains_only_sanitized_multimodal_context(monkeypatch):
    monkeypatch.setenv("PRIVATEEYE_VLM_MODE", "real")
    adapter = VLMAdapter()
    request = adapter.build_request(context())
    serialized = json.dumps(request)
    assert "SANITIZED_IMAGE" in serialized
    assert "e1" in serialized
    assert "SANITIZED_IMAGE" in serialized
    assert "Rahul Sharma" not in serialized
    assert "ABCDE1234F" not in serialized
    assert request["response_format"]["type"] == "json_schema"
    assert request["response_format"]["json_schema"]["strict"] is True
    assert "Authorization" not in serialized


def test_real_response_parses_ref_target_and_value_ref():
    action = VLMAdapter.parse_response({
        "choices": [{"message": {"content": json.dumps({
            "action": "fill",
            "target": {"ref": "e2"},
            "value_ref": "user_profile.pan",
        })}}],
    })
    assert action.action == ActionType.FILL
    assert action.target is not None and action.target.ref == "e2"
    assert action.value_ref == "user_profile.pan"


def test_real_response_rejects_unknown_value_namespace():
    with pytest.raises(ValueError):
        VLMAdapter.parse_response({
            "choices": [{"message": {"content": json.dumps({
                "action": "fill",
                "target": {"ref": "e2"},
                "value_ref": "admin.password",
            })}}],
        })


@pytest.mark.parametrize("content", ["", "not json", '{"action":"eval"}'])
def test_real_response_fails_closed(content):
    with pytest.raises(ValueError):
        VLMAdapter.parse_response({
            "choices": [{"message": {"content": content}}],
        })
