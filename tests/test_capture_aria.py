from client.capture import _parse_aria_nodes


def test_parse_playwright_ai_snapshot_refs_and_boxes():
    snapshot = (
        "- generic [active] [ref=e1] [box=8,8,1264,704]:\n"
        '  - button "Continue" [ref=e2] [box=8,8,69,21]\n'
    )
    assert _parse_aria_nodes(snapshot) == [
        {"role": "generic", "name": "", "ref": "e1", "bbox": [8.0, 8.0, 1264.0, 704.0]},
        {"role": "button", "name": "Continue", "ref": "e2", "bbox": [8.0, 8.0, 69.0, 21.0]},
    ]
