"""Freeze pre-Phase-6 evidence without overwriting historical artifacts."""

import json
from datetime import UTC, datetime
from pathlib import Path

REPORTS = Path("eval/reports")
OUTPUT = REPORTS / "phase6_baseline.json"


def read(name: str) -> dict:
    path = REPORTS / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> None:
    baseline = {
        "frozen_at": datetime.now(UTC).isoformat(),
        "test_count": 72,
        "real_vlm": {
            "qwen_3b_canaries": read("real_vlm_canaries.json"),
            "qwen_7b_canaries": read("real_vlm_canaries_7b.json"),
            "qwen_3b_workflows": read("real_vlm_report.json"),
            "qwen_7b_workflows": read("real_vlm_report_7b.json"),
            "model_comparison": read("model_comparison_real.json"),
        },
        "privacy": read("real_privacy_evidence.json"),
        "detector": read("detector_benchmark.json"),
        "phase5_report": read("phase5_real_validation.json"),
        "limitations": [
            "Baseline predates candidate-grounding changes.",
            "Previous context ablation lacked complete workflow denominators.",
            "Live measurements used Ollama rather than a validated vLLM deployment.",
        ],
    }
    OUTPUT.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
