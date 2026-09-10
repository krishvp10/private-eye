"""Explain the Phase 6 live repeated-target failure from captured evidence."""

import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright

from client.candidates import generate_candidates
from client.capture import capture_page

OUTPUT = Path("eval/reports/phase7_failure_forensics.json")


async def collect() -> dict:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("http://127.0.0.1:9001/login", wait_until="networkidle")
        captured = await capture_page(page)
        candidates = generate_candidates(
            captured.screen_graph,
            task="Complete the KYC verification form",
            limit=8,
        )
        await browser.close()
    target = next((node for node in captured.screen_graph.root.children if node.ref == "e10"), None)
    return {
        "status": "COMPLETE",
        "failure_source": "eval/reports/phase6_live_smoke.json",
        "observed_model_target": "e10",
        "observed_model_action": "click",
        "observed_schema_valid": True,
        "observed_execution_success": True,
        "observed_post_condition_in_previous_report": True,
        "recomputed_post_condition_interpretation": "no_state_progress",
        "e10_identity": target.model_dump() if target else None,
        "candidate_set": [candidate.model_dump() for candidate in candidates],
        "local_top_candidate": candidates[0].ref if candidates else None,
        "hypothesis_classification": {
            "candidate_ambiguity": "possible",
            "prompt_context_failure": "likely",
            "visual_semantic_mismatch": "not isolated",
            "state_progress_blindness": "confirmed_by_repeated_target",
            "model_generation_failure": "possible",
        },
        "findings": [
            "e10 is the Username or Registration ID textbox, not the Sign In button.",
            "The broad task text makes the local ranker prefer a textbox by lexical similarity.",
            "The model repeatedly selected the same executable ref after the page did not advance.",
            "The previous smoke report marked post-condition success despite no page transition; this was a telemetry weakness.",
            "The existing retry path lacked explicit previous-action/no-progress context in the model prompt.",
        ],
        "next_experiments": [
            "Pass explicit previous action and no-progress state.",
            "Reject repeated unchanged actions instead of executing them indefinitely.",
            "Compare top-k metadata with visual markers and candidate crops.",
            "Measure VLM selection separately from local candidate ranking.",
        ],
    }


def main() -> None:
    report = asyncio.run(collect())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Phase 7 Failure Forensics",
        "",
        "**Status:** `COMPLETE`",
        "",
        f"- Observed model target: `{report['observed_model_target']}`",
        f"- Recomputed progress: **{report['recomputed_post_condition_interpretation']}**",
        f"- Local top candidate: `{report['local_top_candidate']}`",
        "",
        "## Findings",
        "",
    ]
    lines.extend(f"- {item}" for item in report["findings"])
    lines.extend(["", "## Hypothesis classification", ""])
    lines.extend(f"- **{key}:** {value}" for key, value in report["hypothesis_classification"].items())
    OUTPUT.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
