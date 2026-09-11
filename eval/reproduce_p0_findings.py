"""Independent reproduction of Phase 14 P0 findings.
Tests:
1. Finding A: Visual secret false-negative leakage (Unicode obfuscation bypassing regex)
2. Finding B: LocalPolicyEngine decoupling from client/agent.py execution path
3. Finding C: OutboundLeakInterceptor skips image_b64, allowing visual pixel leakage
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from client.agent import PrivateEyeAgent
from client.vault import LocalVault
from eval.leak_check import OutboundLeakInterceptor, SecurityLeakException
from privacy.detectors.regex import RegexDetector


def test_reproduce_finding_a() -> dict:
    """Finding A: Regex detector misses Unicode obfuscated PII strings."""
    detector = RegexDetector()
    vault = LocalVault()
    raw_pan = vault.resolve("user_profile.pan")
    obfuscated_pan = "\u200b".join(list(raw_pan))

    clean_matches = detector.scan_raw_text(f"PAN: {raw_pan}")
    obfuscated_matches = detector.scan_raw_text(f"PAN: {obfuscated_pan}")

    reproduced = (len(clean_matches) > 0) and (len(obfuscated_matches) == 0)
    return {
        "reproduced": reproduced,
        "clean_matches": len(clean_matches),
        "obfuscated_matches": len(obfuscated_matches),
        "obfuscated_string_preview": f"{raw_pan[:2]}[ZWSP]...{raw_pan[-2:]}",
        "severity": "HIGH",
    }


def test_reproduce_finding_b() -> dict:
    """Finding B: LocalPolicyEngine is decoupled from client/agent.py."""
    # Check imports in client/agent.py
    agent_code = (REPO_ROOT / "client" / "agent.py").read_text(encoding="utf-8")
    policy_engine_imported = "LocalPolicyEngine" in agent_code

    # Check whether PrivateEyeAgent instantiates policy_engine
    agent = PrivateEyeAgent()
    has_policy_engine_attr = hasattr(agent, "policy_engine")

    reproduced = (not policy_engine_imported) and (not has_policy_engine_attr)
    return {
        "reproduced": reproduced,
        "policy_engine_imported_in_agent": policy_engine_imported,
        "agent_has_policy_engine_attr": has_policy_engine_attr,
        "severity": "HIGH",
    }


def test_reproduce_finding_c() -> dict:
    """Finding C: OutboundLeakInterceptor explicitly disregards image_b64."""
    vault = LocalVault()
    interceptor = OutboundLeakInterceptor(vault=vault)
    raw_pan = vault.resolve("user_profile.pan")

    # Construct payload with raw secret inside image_b64
    raw_fake_png = b"\x89PNG\r\n\x1a\n" + raw_pan.encode("ascii") + b"\x00\x00IEND"
    b64_pixels = base64.b64encode(raw_fake_png).decode("ascii")

    payload_with_image_secret = json.dumps(
        {
            "task": "Perform KYC check",
            "image_b64": b64_pixels,
            "screen_graph": {"root": {"id": "1", "role": "page", "children": []}},
        }
    )

    leak_detected = False
    try:
        interceptor.assert_safe(payload_with_image_secret)
    except SecurityLeakException:
        leak_detected = True

    reproduced = not leak_detected
    return {
        "reproduced": reproduced,
        "leak_detected_in_image_b64": leak_detected,
        "severity": "HIGH",
    }


def run_all_reproductions() -> dict:
    print("==============================================================")
    print("PHASE 15: INDEPENDENT REPRODUCTION OF P0 FINDINGS")
    print("==============================================================")

    res_a = test_reproduce_finding_a()
    print(f"Finding A (Visual FN / Unicode Obfuscation Leak): Reproduced = {res_a['reproduced']}")

    res_b = test_reproduce_finding_b()
    print(f"Finding B (LocalPolicyEngine Decoupled from Agent): Reproduced = {res_b['reproduced']}")

    res_c = test_reproduce_finding_c()
    print(
        f"Finding C (OutboundLeakInterceptor Skips image_b64): Reproduced = {res_c['reproduced']}"
    )

    results = {
        "finding_a_visual_false_negative": res_a,
        "finding_b_policy_engine_decoupling": res_b,
        "finding_c_outbound_screenshot_bypass": res_c,
        "all_p0_findings_reproduced": res_a["reproduced"]
        and res_b["reproduced"]
        and res_c["reproduced"],
    }

    out_path = REPO_ROOT / "eval" / "reports" / "phase15_p0_reproduction.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved reproduction results to {out_path}")
    return results


if __name__ == "__main__":
    run_all_reproductions()
