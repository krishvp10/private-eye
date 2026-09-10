from client.candidates import generate_candidates
from shared.protocol import ActionType, ScreenGraph, ScreenNode


def test_candidate_generation_ranks_matching_safe_targets():
    graph = ScreenGraph(
        url="https://example.test",
        root=ScreenNode(
            role="WebArea",
            id="root",
            children=[
                ScreenNode(role="button", name="Cancel", id="cancel", ref="e1"),
                ScreenNode(role="button", name="Continue", id="continue", ref="e2"),
                ScreenNode(role="textbox", name="PAN Number", id="pan", ref="e3", sensitive=True),
            ],
        ),
    )

    candidates = generate_candidates(graph, task="click Continue", action=ActionType.CLICK)

    assert [candidate.ref for candidate in candidates] == ["e2", "e1"]
    assert all(candidate.sensitive is False for candidate in candidates)


def test_candidate_generation_keeps_sensitive_metadata_without_values():
    graph = ScreenGraph(
        url="https://example.test",
        root=ScreenNode(
            role="WebArea",
            id="root",
            children=[
                ScreenNode(
                    role="textbox",
                    name="PAN Number",
                    id="pan",
                    ref="e7",
                    sensitive=True,
                )
            ],
        ),
    )

    candidates = generate_candidates(graph, task="fill PAN Number", action=ActionType.FILL)
    serialized = candidates[0].model_dump_json()

    assert candidates[0].ref == "e7"
    assert candidates[0].sensitive is True
    assert candidates[0].name == "[REDACTED FIELD]"
    assert "value" not in serialized.lower()
    assert "ABCDE1234F" not in serialized
