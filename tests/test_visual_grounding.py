import io

from PIL import Image

from client.visual_grounding import mark_candidates
from shared.protocol import SafeCandidate


def test_mark_candidates_uses_sanitized_input_and_returns_mapping():
    image = Image.new("RGB", (100, 80), color="black")
    source = io.BytesIO()
    image.save(source, format="PNG")
    candidate = SafeCandidate(
        ref="e17",
        role="button",
        name="Continue",
        bbox=[10, 12, 30, 20],
    )

    result = mark_candidates(source.getvalue(), [candidate])

    assert result.labels == {"C1": "e17"}
    marked = Image.open(io.BytesIO(result.image_bytes))
    assert marked.size == (100, 80)
    assert result.image_bytes != source.getvalue()
