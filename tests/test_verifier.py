import io
from PIL import Image

from client.verifier import CandidateVerifier
from shared.protocol import SafeCandidate


def test_verifier_extract_crop_safety():
    verifier = CandidateVerifier()
    # Create a synthetic 100x100 sanitized image
    img = Image.new("RGB", (100, 100), color=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_bytes = buf.getvalue()

    crop = verifier.extract_crop(raw_bytes, [10, 10, 30, 30])
    assert crop is not None
    cropped_img = Image.open(io.BytesIO(crop))
    assert cropped_img.size[0] > 0
    assert cropped_img.size[1] > 0

    # Invalid bboxes fail safely
    assert verifier.extract_crop(raw_bytes, []) is None
    assert verifier.extract_crop(raw_bytes, [10, 10, 0, 0]) is None


def test_verifier_disambiguates_ordinal_second():
    verifier = CandidateVerifier()
    c1 = SafeCandidate(ref="e1", role="button", name="Edit", bbox=[100, 50, 50, 20], rank_score=0.8)
    c2 = SafeCandidate(
        ref="e2", role="button", name="Edit", bbox=[100, 150, 50, 20], rank_score=0.8
    )

    # Task asks for the second edit button
    result = verifier.disambiguate_candidates("Click Edit beside the second user", [c1, c2])
    assert result.verified is True
    assert result.selected_candidate is not None
    assert result.selected_candidate.ref == "e2"
    assert result.reason == "verified_ordinal_second"


def test_verifier_disambiguates_spatial_bottom():
    verifier = CandidateVerifier()
    c_top = SafeCandidate(
        ref="e1", role="button", name="Continue", bbox=[500, 40, 80, 30], rank_score=0.75
    )
    c_bottom = SafeCandidate(
        ref="e2", role="button", name="Continue", bbox=[500, 600, 80, 30], rank_score=0.75
    )

    result = verifier.disambiguate_candidates(
        "Click the secondary Continue button at bottom", [c_top, c_bottom]
    )
    assert result.verified is True
    assert result.selected_candidate is not None
    assert result.selected_candidate.ref == "e2"
    assert result.reason == "verified_spatial_bottom"


def test_verifier_flags_ambiguous_near_tie():
    verifier = CandidateVerifier()
    c1 = SafeCandidate(
        ref="e1", role="button", name="Submit", bbox=[100, 100, 50, 20], rank_score=0.55
    )
    c2 = SafeCandidate(
        ref="e2", role="button", name="Submit Now", bbox=[200, 100, 50, 20], rank_score=0.54
    )

    # Without spatial or ordinal cues, near-tie cannot be assumed
    result = verifier.disambiguate_candidates("Click Submit", [c1, c2])
    assert result.verified is False
    assert result.reason == "ambiguous_candidates_unresolved"
