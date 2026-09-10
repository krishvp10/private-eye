"""Unit tests for Image Resolution Sweep evaluation."""

from eval.image_resolution_sweep import RESOLUTIONS, run_resolution_sweep


def test_resolutions_defined():
    assert "LOW" in RESOLUTIONS
    assert "MEDIUM" in RESOLUTIONS
    assert "HIGH" in RESOLUTIONS

    for cfg in RESOLUTIONS.values():
        assert cfg["min_pixels"] > 0
        assert cfg["max_pixels"] >= cfg["min_pixels"]
        assert "target_dimension" in cfg


def test_run_resolution_sweep_offline():
    sweep = run_resolution_sweep(server_url="http://127.0.0.1:9999/v1")
    assert sweep["selected_configuration"] == "MEDIUM"
    assert "configurations" in sweep
    assert len(sweep["configurations"]) == 3

    for cfg in sweep["configurations"].values():
        assert cfg["status"] == "SKIPPED"
