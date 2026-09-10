"""
Privacy Detection False-Negative Diagnostic Tool for PrivateEye.
Performs an exhaustive entity-by-entity comparison between realistic corpus ground truth
and actual detector output to diagnose the exact root causes of missed recall.
Generates eval/reports/privacy_false_negatives.json and .md.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from playwright.async_api import ViewportSize, async_playwright

from client.capture import capture_page
from privacy.detectors.dom import DOMDetector
from privacy.detectors.face import FaceDetector
from privacy.detectors.ner import LightweightNERDetector
from privacy.detectors.regex import RegexDetector
from privacy.pipeline import PrivacyPipeline

CORPUS_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "realistic_privacy_corpus"
GROUND_TRUTH_PATH = CORPUS_DIR / "ground_truth.json"


def bbox_iou(box_a: list[float], box_b: list[float]) -> float:
    """Calculate IoU of two [x, y, w, h] bounding boxes."""
    xa1, ya1, wa, ha = box_a
    xa2, ya2 = xa1 + wa, ya1 + ha

    xb1, yb1, wb, hb = box_b
    xb2, yb2 = xb1 + wb, yb1 + hb

    xi1 = max(xa1, xb1)
    yi1 = max(ya1, yb1)
    xi2 = min(xa2, xb2)
    yi2 = min(ya2, yb2)

    inter_w = max(0.0, xi2 - xi1)
    inter_h = max(0.0, yi2 - yi1)
    inter_area = inter_w * inter_h

    area_a = wa * ha
    area_b = wb * hb
    union_area = area_a + area_b - inter_area
    if union_area <= 0:
        return 0.0
    return inter_area / union_area


def load_ground_truth() -> dict[str, Any]:
    with open(GROUND_TRUTH_PATH, encoding="utf-8") as f:
        return json.load(f)


async def run_diagnostic() -> dict[str, Any]:
    """Run entity-level false-negative audit across all realistic corpus fixtures."""
    gt_data = load_ground_truth()

    fixtures = gt_data.get("fixtures", {})
    pipeline = PrivacyPipeline()

    dom_detector = DOMDetector()
    regex_detector = RegexDetector()
    ner_detector = LightweightNERDetector()
    face_cascade = FaceDetector()

    missed_cases: list[dict[str, Any]] = []
    detected_cases: list[dict[str, Any]] = []

    total_expected = 0
    total_detected = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for fix_id, fix_meta in fixtures.items():
            html_path = (CORPUS_DIR / fix_meta["file"]).resolve()
            viewport: ViewportSize = {"width": 375, "height": 812} if "mobile" in fix_id else {"width": 1280, "height": 800}
            page = await browser.new_page(viewport=viewport)
            await page.goto(html_path.as_uri(), wait_until="load")

            captured = await capture_page(page)
            pipe_detections = pipeline.detect(
                captured.raw_elements,
                captured.screenshot_bytes,
                captured.visible_text,
                captured.viewport,
            )

            # Detect with individual detectors for attribution
            dom_dets = dom_detector.detect(captured.raw_elements)
            regex_dets = regex_detector.detect_in_elements(captured.raw_elements)
            ner_dets = ner_detector.detect_in_elements(captured.raw_elements)
            face_dets = face_cascade.detect(captured.raw_elements, captured.screenshot_bytes)

            expected_elements = [el for el in fix_meta.get("elements", []) if el.get("expected_masked", True)]

            for expected in expected_elements:
                total_expected += 1
                exp_cat = expected.get("category", "").lower()
                exp_elem_id = expected.get("id", "")
                exp_text = expected.get("text_snippet", "")
                exp_bbox = expected.get("bbox")

                # Match against pipeline detections
                matched = False
                best_match = None
                best_iou = 0.0

                for det in pipe_detections:
                    det_cat = det.category.value.lower()
                    cat_match = (
                        det_cat == exp_cat
                        or (exp_cat in {"aadhaar", "pan", "phone", "email", "address"} and det_cat in {"pii", exp_cat})
                        or (exp_cat == "password" and det_cat in {"credential", "password"})
                    )
                    if not cat_match:
                        continue

                    # Check evidence_id match
                    if exp_elem_id and (det.evidence_id == exp_elem_id or exp_elem_id in det.evidence_id):
                        matched = True
                        best_match = det
                        break

                    # Check bounding box IoU if both have boxes
                    if exp_bbox and det.bounding_box:
                        det_box = [det.bounding_box.x, det.bounding_box.y, det.bounding_box.width, det.bounding_box.height]
                        iou = bbox_iou(exp_bbox, det_box)
                        if iou > best_iou:
                            best_iou = iou
                            best_match = det
                        if iou >= 0.2:
                            matched = True
                            break

                if matched and best_match:
                    total_detected += 1
                    detected_cases.append({
                        "fixture": fix_id,
                        "category": exp_cat,
                        "element_id": exp_elem_id,
                        "text": exp_text,
                        "source": best_match.source.value,
                    })
                else:
                    # Diagnose exact root cause
                    root_cause = "unknown"
                    if exp_cat == "face":
                        if "small" in exp_text.lower() or "avatar" in exp_text.lower() or "badge" in exp_text.lower():
                            root_cause = "tiny_face_below_haar_min_size"
                        else:
                            root_cause = "face_visual_detection_miss"
                    elif exp_cat in {"pan", "aadhaar"}:
                        if "." in exp_text or "-" in exp_text:
                            root_cause = "unusual_separator_not_normalized"
                        elif "paragraph" in fix_id or "inline" in exp_text.lower():
                            root_cause = "unstructured_paragraph_context"
                        else:
                            root_cause = "regex_pattern_miss"
                    elif exp_cat == "address":
                        root_cause = "multiline_address_break"
                    elif exp_cat == "phone":
                        if "." in exp_text or "-" in exp_text or "+" in exp_text:
                            root_cause = "phone_separator_format_miss"
                        else:
                            root_cause = "phone_regex_miss"
                    elif exp_cat == "name":
                        root_cause = "unstructured_name_ner_boundary"

                    # Attribution: which detector saw it?
                    dom_saw = any(exp_elem_id in d.evidence_id for d in dom_dets if exp_elem_id)
                    regex_saw = any(d.category.value.lower() == exp_cat for d in regex_dets)
                    ner_saw = any(d.category.value.lower() == exp_cat for d in ner_dets)
                    face_saw = any(d.category.value.lower() == "face" for d in face_dets) if exp_cat == "face" else False

                    missed_cases.append({
                        "fixture": fix_id,
                        "category": exp_cat,
                        "element_id": exp_elem_id,
                        "ground_truth_bbox": exp_bbox,
                        "predicted_bbox_if_any": (
                            [best_match.bounding_box.x, best_match.bounding_box.y, best_match.bounding_box.width, best_match.bounding_box.height]
                            if (best_match and best_match.bounding_box)
                            else None
                        ),
                        "text_snippet": exp_text,
                        "root_cause": root_cause,
                        "channel_attribution": {
                            "dom_detected": dom_saw,
                            "regex_detected": regex_saw,
                            "ner_detected": ner_saw,
                            "face_detected": face_saw,
                        },
                    })
            await page.close()
        await browser.close()

    # Aggregate by root cause
    cause_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    for m in missed_cases:
        c = m["root_cause"]
        cause_counts[c] = cause_counts.get(c, 0) + 1
        cat = m["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    recall = (total_detected / total_expected) if total_expected > 0 else 0.0

    return {
        "summary": {
            "total_expected_entities": total_expected,
            "total_detected_entities": total_detected,
            "total_false_negatives": len(missed_cases),
            "recall": round(recall, 3),
            "missed_percentage": round((1.0 - recall) * 100, 1),
        },
        "breakdown_by_root_cause": [
            {
                "root_cause": cause,
                "miss_count": count,
                "percentage_of_misses": round((count / len(missed_cases)) * 100, 1) if missed_cases else 0.0,
            }
            for cause, count in sorted(cause_counts.items(), key=lambda x: x[1], reverse=True)
        ],
        "breakdown_by_category": [
            {
                "category": cat,
                "miss_count": count,
                "percentage_of_misses": round((count / len(missed_cases)) * 100, 1) if missed_cases else 0.0,
            }
            for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        ],
        "missed_cases": missed_cases,
    }


def write_diagnostic_reports(diag: dict[str, Any], output_dir: Path = Path("eval/reports")) -> None:
    """Generate JSON and Markdown diagnostic reports."""
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "privacy_false_negatives.json"
    md_path = output_dir / "privacy_false_negatives.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)

    s = diag["summary"]
    md_lines = [
        "# PrivateEye Privacy False-Negative Diagnostic Analysis",
        "",
        "## Executive Summary",
        "",
        f"- **Total Expected Sensitive Entities**: `{s['total_expected_entities']}`",
        f"- **Correctly Detected Entities**: `{s['total_detected_entities']}`",
        f"- **Total False Negatives (Misses)**: `{s['total_false_negatives']}`",
        f"- **Benchmark Recall**: `{s['recall'] * 100:.1f}%` (Miss Rate: `{s['missed_percentage']}%`)",
        "",
        "---",
        "",
        "## Root-Cause Breakdown",
        "",
        "| Root Cause | Miss Count | Share of Misses | Primary Remediation Vector |",
        "| :--- | :---: | :---: | :--- |",
    ]

    remediation_map = {
        "unusual_separator_not_normalized": "Normalize punctuation (dots, hyphens) in RegexDetector prior to PAN/Aadhaar matching",
        "phone_separator_format_miss": "Expand phone regex patterns to support dot-separated and grouped formats",
        "multiline_address_break": "Add multi-line lookahead and Indian PIN code anchor scanning",
        "tiny_face_below_haar_min_size": "Lower Haar cascade minSize to (24, 24) and enhance DOM avatar badge heuristic",
        "unstructured_paragraph_context": "Add conversational sentence tokenization for inline entity extraction",
        "unstructured_name_ner_boundary": "Expand offline NER gazetteer for Indian honorifics and multi-token names",
    }

    for item in diag["breakdown_by_root_cause"]:
        rc = item["root_cause"]
        rem = remediation_map.get(rc, "Targeted detector refinement")
        md_lines.append(f"| `{rc}` | {item['miss_count']} | {item['percentage_of_misses']}% | {rem} |")

    md_lines.extend([
        "",
        "---",
        "",
        "## Breakdown by Sensitive Category",
        "",
        "| Category | Miss Count | Share of Misses |",
        "| :--- | :---: | :---: |",
    ])
    for item in diag["breakdown_by_category"]:
        md_lines.append(f"| **{item['category'].upper()}** | {item['miss_count']} | {item['percentage_of_misses']}% |")

    md_lines.extend([
        "",
        "---",
        "",
        "## Detailed False-Negative Records",
        "",
        "| Fixture | Category | Element ID / Snippet | Diagnosed Root Cause | DOM | Regex | NER | Face |",
        "| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |",
    ])

    for m in diag["missed_cases"]:
        snippet = m["element_id"] or m["text_snippet"] or "N/A"
        if len(snippet) > 30:
            snippet = snippet[:27] + "..."
        attrs = m["channel_attribution"]
        dom_s = "Y" if attrs["dom_detected"] else "N"
        reg_s = "Y" if attrs["regex_detected"] else "N"
        ner_s = "Y" if attrs["ner_detected"] else "N"
        fc_s = "Y" if attrs["face_detected"] else "N"

        md_lines.append(
            f"| `{m['fixture']}` | `{m['category']}` | `{snippet}` | `{m['root_cause']}` | {dom_s} | {reg_s} | {ner_s} | {fc_s} |"
        )

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"Diagnostic reports written to:\n  {json_path}\n  {md_path}")


def main() -> None:
    diag = asyncio.run(run_diagnostic())
    write_diagnostic_reports(diag)
    print(f"Diagnostic complete: {diag['summary']['total_false_negatives']} false negatives identified.")


if __name__ == "__main__":
    main()
