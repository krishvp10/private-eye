"""Unit tests for GPU and environment diagnostic utility."""

from scripts.check_gpu import diagnose_environment, get_gpu_details, get_wsl_details


def test_get_gpu_details_structure():
    gpu = get_gpu_details()
    assert "gpu_available" in gpu
    assert "vram_total_mb" in gpu
    assert "driver_version" in gpu
    assert isinstance(gpu["gpu_available"], bool)
    assert isinstance(gpu["vram_total_mb"], int)


def test_get_wsl_details_structure():
    wsl = get_wsl_details()
    assert "wsl_available" in wsl
    assert "distributions" in wsl
    assert isinstance(wsl["distributions"], list)


def test_diagnose_environment():
    diag = diagnose_environment()
    assert "os" in diag
    assert "gpu" in diag
    assert "model_fit" in diag
    assert "qwen_3b_instruct" in diag["model_fit"]
    assert "qwen_7b_instruct" in diag["model_fit"]
    assert "ready_for_real_inference" in diag
