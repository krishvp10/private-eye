"""Phase 15 Comprehensive Privacy Boundary Audit.
Audits the repaired privacy boundary against adversarial leakage paths:
1. Unicode obfuscation (zero-width spaces, joiners, formatting chars)
2. Character-separated / hyphenated identifiers (PAN, Aadhaar, Card)
3. Sensitive form placeholders and autocomplete attributes
4. Outbound wire payload verification (both text and decoded image_b64 bytes)
5. Visual pixel solid masking verification
"""

from __future__ import annotations

import base64
import io
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from client.vault import LocalVault
from eval.leak_check import OutboundLeakInterceptor
from privacy.detectors.dom import DOMDetector
from privacy.detectors.regex import RegexDetector, normalize_text_for_privacy
from privacy.pipeline import PrivacyPipeline
from privacy.redaction.masker import RedactionEngine
from shared.protocol import (
    ScreenGraph,
    ScreenNode,
)

REPORT_JSON = REPO_ROOT / "eval" / "reports" / "phase15_privacy_boundary.json"


def run_privacy_boundary_audit() -> dict[str, Any]:
    print("==============================================================")
    print("PHASE 15: PRIVACY BOUNDARY AUDIT & LEAK CLOSURE VERIFICATION")
    print("==============================================================")

    vault = LocalVault()
    pipeline = PrivacyPipeline()
    redactor = RedactionEngine()
    interceptor = OutboundLeakInterceptor(vault=vault)
    regex_det = RegexDetector()
    dom_det = DOMDetector()

    results: dict[str, Any] = {
        "benchmark": "Phase 15 Privacy Boundary Audit",
        "tested_vectors": [],
        "summary": {},
    }

    # -------------------------------------------------------------------------
    # Test 1: Unicode Obfuscated Secrets (Zero-width spaces & joiners)
    # -------------------------------------------------------------------------
    raw_pan = vault.resolve("user_profile.pan")
    zwsp_pan = "\u200b".join(list(raw_pan))
    zwj_pan = "\u200d".join(list(raw_pan))
    bom_pan = f"\ufeff{raw_pan}"

    for name, text in [("ZWSP_PAN", zwsp_pan), ("ZWJ_PAN", zwj_pan), ("BOM_PAN", bom_pan)]:
        norm = normalize_text_for_privacy(text)
        matches = regex_det.scan_raw_text(text)
        detected = len(matches) > 0
        results["tested_vectors"].append({
            "vector": f"Unicode_{name}",
            "raw_secret": f"{raw_pan[:2]}***{raw_pan[-2:]}",
            "normalized_clean": norm == raw_pan,
            "detected": detected,
            "category": "regex_unicode_normalization",
        })
        print(f"  [Test 1] {name}: detected={detected}, normalized={norm == raw_pan}")
        assert detected, f"Failed to detect {name}"

    # -------------------------------------------------------------------------
    # Test 2: Character-Separated Identifiers (Dashes, dots, spaces)
    # -------------------------------------------------------------------------
    hyphen_pan = "-".join([raw_pan[:5], raw_pan[5:9], raw_pan[9:]])
    dot_pan = ".".join([raw_pan[:5], raw_pan[5:9], raw_pan[9:]])
    space_pan = " ".join([raw_pan[:5], raw_pan[5:9], raw_pan[9:]])

    for name, text in [("Hyphen_PAN", hyphen_pan), ("Dot_PAN", dot_pan), ("Space_PAN", space_pan)]:
        matches = regex_det.scan_raw_text(f"Your ID is {text}")
        detected = len(matches) > 0
        results["tested_vectors"].append({
            "vector": f"Separated_{name}",
            "text": text,
            "detected": detected,
            "category": "regex_separators",
        })
        print(f"  [Test 2] {name}: detected={detected}")
        assert detected, f"Failed to detect {name}"

    # -------------------------------------------------------------------------
    # Test 3: Sensitive Placeholders & Autocomplete Attributes in DOM
    # -------------------------------------------------------------------------
    test_dom_elements = [
        {"id": "input_1", "tag": "input", "placeholder": "Enter your 10-digit PAN number", "bbox": [10, 10, 200, 30]},
        {"id": "input_2", "tag": "input", "autocomplete": "cc-number", "bbox": [10, 50, 200, 30]},
        {"id": "input_3", "tag": "input", "autocomplete": "current-password", "bbox": [10, 90, 200, 30]},
        {"id": "input_4", "tag": "input", "aria-label": "Patient Aadhaar Card", "bbox": [10, 130, 200, 30]},
    ]
    dom_detections = dom_det.detect(test_dom_elements)
    dom_detected_ids = {d.evidence_id.split(":")[1] for d in dom_detections}
    for el in test_dom_elements:
        is_det = el["id"] in dom_detected_ids
        results["tested_vectors"].append({
            "vector": f"DOM_Attribute_{el['id']}",
            "element": el,
            "detected": is_det,
            "category": "dom_heuristics",
        })
        print(f"  [Test 3] {el['id']} ({el.get('placeholder') or el.get('autocomplete')}): detected={is_det}")
        assert is_det, f"Failed to detect DOM element {el['id']}"

    # -------------------------------------------------------------------------
    # Test 4: End-to-End Solid Redaction Mask Verification
    # -------------------------------------------------------------------------
    img = Image.new("RGB", (400, 300), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_screenshot_bytes = buf.getvalue()

    screen_graph = ScreenGraph(
        url="http://localhost/kyc",
        root=ScreenNode(
            id="root",
            role="page",
            children=[
                ScreenNode(id="input_1", role="textbox", name="PAN Input", bbox=[10, 10, 200, 30]),
            ],
        ),
    )

    detections = pipeline.detect(test_dom_elements, raw_screenshot_bytes)
    redacted_result = redactor.redact(raw_screenshot_bytes, screen_graph, detections)

    redacted_img = Image.open(io.BytesIO(redacted_result.sanitized_bytes)).convert("RGB")
    # Verify the redacted region is masked (pixel value changed from 255 to dark mask < 70)
    sample_pixel = redacted_img.getpixel((20, 20))
    is_masked = sample_pixel != (255, 255, 255) and max(sample_pixel) < 70
    results["tested_vectors"].append({
        "vector": "Visual_Pixel_Masking",
        "sample_pixel_redacted_region": sample_pixel,
        "is_masked_dark": is_masked,
        "category": "pixel_redaction",
    })
    print(f"  [Test 4] Redaction pixel check at (20, 20): {sample_pixel} (dark masked={is_masked})")
    assert is_masked, f"Expected masked pixel, got {sample_pixel}"

    # -------------------------------------------------------------------------
    # Test 5: Outbound Wire Interceptor Traps Any Embedded Secret
    # -------------------------------------------------------------------------
    # Sub-case 5A: Clean sanitized payload passes
    clean_payload = json.dumps({
        "task": "Complete KYC",
        "image_b64": base64.b64encode(redacted_result.sanitized_bytes).decode("ascii"),
        "screen_graph": redacted_result.sanitized_graph.model_dump(),
    })
    clean_violations = interceptor.inspect_payload(clean_payload)
    print(f"  [Test 5A] Clean sanitized payload violations: {len(clean_violations)} (PASS)")
    assert len(clean_violations) == 0, f"Clean payload flagged: {clean_violations}"

    # Sub-case 5B: Payload with image containing raw secret is intercepted
    dirty_img_bytes = b"IMAGE_HEADER" + raw_pan.encode("utf-8") + b"IMAGE_FOOTER"
    dirty_payload = json.dumps({
        "task": "KYC",
        "image_b64": base64.b64encode(dirty_img_bytes).decode("ascii"),
    })
    dirty_violations = interceptor.inspect_payload(dirty_payload)
    dirty_blocked = len(dirty_violations) > 0
    print(f"  [Test 5B] Secret embedded in image_b64 trapped: {dirty_blocked} (PASS)")
    assert dirty_blocked, "Failed to trap secret inside image_b64"

    # Sub-case 5C: Unicode obfuscated secret in text is intercepted
    obfuscated_text_payload = json.dumps({
        "task": "KYC",
        "user_note": f"My ID is {zwsp_pan}",
    })
    obfuscated_violations = interceptor.inspect_payload(obfuscated_text_payload)
    obfuscated_blocked = len(obfuscated_violations) > 0
    print(f"  [Test 5C] Unicode obfuscated secret trapped in text: {obfuscated_blocked} (PASS)")
    assert obfuscated_blocked, "Failed to trap Unicode obfuscated secret in text"

    results["summary"] = {
        "total_tests": len(results["tested_vectors"]) + 3,
        "all_passed": True,
        "visual_pixel_escape_closed": True,
        "unicode_obfuscation_trapped": True,
        "image_b64_inspection_active": True,
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n[PASSED] Privacy boundary audit complete. Report saved to {REPORT_JSON}")
    return results


if __name__ == "__main__":
    run_privacy_boundary_audit()
