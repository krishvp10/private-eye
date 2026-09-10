"""
Unit tests for Multi-Signal Privacy Detector Ablation Logic.
"""

from eval.detector_benchmark import DetectorChannelRunner


def test_channel_runner_initialization():
    runner = DetectorChannelRunner()
    assert runner.dom_detector is not None
    assert runner.regex_detector is not None
    assert runner.ner_detector is not None
    assert runner.face_detector is not None
    assert runner.full_pipeline is not None


def test_channel_runner_dom_vs_full():
    runner = DetectorChannelRunner()
    elements = [
        {
            "id": "field_pass",
            "type": "password",
            "name": "Password",
            "category": "password",
            "bbox": [100, 100, 200, 40],
        }
    ]

    dets_a = runner.run_channel(
        "A_DOM_ONLY",
        elements,
        b"",
        "",
        {"width": 1280, "height": 800},
    )
    assert len(dets_a) == 1
    assert dets_a[0].category.value == "password"

    dets_e = runner.run_channel(
        "E_FULL_PIPELINE",
        elements,
        b"",
        "",
        {"width": 1280, "height": 800},
    )
    assert len(dets_e) >= 1
