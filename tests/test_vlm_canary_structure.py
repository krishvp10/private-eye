"""
Unit tests for Real-VLM Canary Structure and Prompt Injection Defense.
"""

from eval.real_vlm_canary import CANARIES
from scripts.check_vlm import check_endpoint


def test_canary_task_specifications():
    canary_names = [name for name, *_ in CANARIES]
    assert "continue_button" in canary_names
    assert "pan_field" in canary_names
    assert "submit_button" in canary_names
    assert "value_ref_only" in canary_names
    assert "redacted_content" in canary_names
    assert "prompt_injection" in canary_names

    # Ensure value_ref_only specifies vault_ref and never a raw value
    val_ref_canary = next(c for c in CANARIES if c[0] == "value_ref_only")
    assert val_ref_canary[4] == "user_profile.pan"

    # Ensure prompt injection canary focuses on allowed action only
    inj_canary = next(c for c in CANARIES if c[0] == "prompt_injection")
    assert inj_canary[2] == "click"
    assert inj_canary[3] == "Submit Application"


def test_check_vlm_endpoint_blocked_when_offline():
    # When no server is listening on port 59999, it must return BLOCKED fail-closed
    result = check_endpoint("http://127.0.0.1:59999/v1", target_model="Qwen/Qwen2.5-VL-3B-Instruct")
    assert result["status"] == "BLOCKED"
    assert "Connection refused" in result["reason"] or "refused" in result["reason"].lower()
