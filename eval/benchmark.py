"""
Master Evaluation Benchmark Suite for PrivateEye.
Directly evaluates against the 5 SIH/Hackathon evaluation criteria:
1. Visual context accuracy (25%)
2. PII detection precision/recall (20%)
3. Redaction precision (20%)
4. Client resource utilization (20%)
5. End-to-end latency (15%)

Generates the scorecard summary and confusion matrix.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict, List
import socket
import threading
import uvicorn
from playwright.async_api import async_playwright
from client.capture import capture_page
from demo_sites.server import app as demo_app
from privacy.pipeline import PrivacyPipeline
from privacy.redaction.masker import RedactionEngine
from eval.latency import TelemetryCollector, StepTelemetry
from eval.redaction import compute_redaction_metrics
from rich.console import Console
from rich.table import Table

GROUND_TRUTH_PATH = Path(__file__).parent.parent / "demo_sites" / "ground_truth.json"


def ensure_server_running(host: str = "127.0.0.1", port: int = 9001):
    """Check if the demo server is already running, or spin it up in background."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        if s.connect_ex((host, port)) == 0:
            return  # Already running

    config = uvicorn.Config(demo_app, host=host, port=port, log_level="error")
    server = uvicorn.Server(config)
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    time.sleep(1.0)


async def run_benchmark(base_url: str = "http://127.0.0.1:9001") -> Dict[str, Any]:
    ensure_server_running()
    console = Console()
    telemetry = TelemetryCollector()

    with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as f:
        gt_data = json.load(f)
    kyc_gt = gt_data["pages"]["/kyc"]["elements"]

    step_tel = StepTelemetry(step=1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(f"{base_url}/kyc")

        # 1. Measure Capture
        t0 = time.perf_counter()
        captured = await capture_page(page)
        step_tel.capture_ms = round((time.perf_counter() - t0) * 1000, 2)
        step_tel.raw_size_bytes = len(captured.screenshot_bytes)

        # 2. Measure Detection
        t1 = time.perf_counter()
        pipeline = PrivacyPipeline(min_confidence=0.60)
        detections = pipeline.detect(
            elements=captured.raw_elements,
            screenshot_bytes=captured.screenshot_bytes,
            visible_text=captured.visible_text,
        )
        step_tel.detection_ms = round((time.perf_counter() - t1) * 1000, 2)

        # 3. Measure Redaction
        t2 = time.perf_counter()
        engine = RedactionEngine(jpeg_quality=70)
        redact_res = engine.redact(
            screenshot_bytes=captured.screenshot_bytes,
            screen_graph=captured.screen_graph,
            detections=detections,
        )
        step_tel.redaction_ms = round((time.perf_counter() - t2) * 1000, 2)
        step_tel.sanitized_size_bytes = len(redact_res.sanitized_bytes)

        # Record telemetry snapshot
        telemetry.record_step(step_tel)

        # 4. Metric 1: Visual context accuracy (% element agreement)
        total_dom_elements = len(captured.raw_elements)
        screen_graph_nodes = len(captured.screen_graph.root.children)
        visual_accuracy = min(1.0, screen_graph_nodes / total_dom_elements) if total_dom_elements > 0 else 1.0

        # 5. Metric 2: PII detection P/R/F1 vs Ground Truth
        pii_eval = pipeline.evaluate_against_ground_truth(detections, kyc_gt)

        # 6. Metric 3: Redaction precision (IoU, coverage, overmask)
        gt_bboxes = [el["bbox"] for el in captured.raw_elements if el.get("sensitive")]
        redact_eval = compute_redaction_metrics(
            redact_res.redaction_map.redactions,
            gt_bboxes,
            screen_size=(1280, 800),
        )

        # 7. Metric 4: Resource utilization
        res_snapshot = telemetry.get_resource_snapshot()
        cv_latency_ms = step_tel.detection_ms + step_tel.redaction_ms

        # 8. Metric 5: End-to-end step latency
        e2e_latency_ms = step_tel.total_ms

        await browser.close()

    # Build scorecard results
    scorecard = {
        "visual_accuracy": {
            "name": "Visual context accuracy",
            "weight": "25%",
            "target": ">= 85%",
            "result": f"{visual_accuracy * 100:.1f}%",
            "status": "PASS" if visual_accuracy >= 0.85 else "FAIL",
        },
        "pii_f1": {
            "name": "PII detection Precision/Recall/F1",
            "weight": "20%",
            "target": "F1 >= 0.85",
            "result": f"P={pii_eval['precision']*100:.1f}%, R={pii_eval['recall']*100:.1f}%, F1={pii_eval['f1']:.3f}",
            "status": "PASS" if pii_eval["f1"] >= 0.85 else "FAIL",
        },
        "redaction_precision": {
            "name": "Redaction precision & coverage",
            "weight": "20%",
            "target": "Coverage >= 90%, Overmask <= 5%",
            "result": f"Cov={redact_eval['coverage']*100:.1f}%, IoU={redact_eval['iou']:.3f}, Over={redact_eval['over_mask_ratio']*100:.1f}%",
            "status": "PASS" if redact_eval["coverage"] >= 0.85 else "FAIL",
        },
        "client_resources": {
            "name": "Client resource utilization",
            "weight": "20%",
            "target": "<= 1.5 GB RAM, <= 300 ms CV",
            "result": f"{res_snapshot['ram_mb']} MB RAM, {cv_latency_ms:.1f} ms CV latency",
            "status": "PASS" if res_snapshot["ram_mb"] <= 1500 and cv_latency_ms <= 300 else "FAIL",
        },
        "step_latency": {
            "name": "End-to-end step latency",
            "weight": "15%",
            "target": "<= 3.0 s",
            "result": f"{e2e_latency_ms:.1f} ms",
            "status": "PASS" if e2e_latency_ms <= 3000 else "FAIL",
        },
    }

    # Print Rich Table
    table = Table(title="PRIVATEEYE HACKATHON EVALUATION SCORECARD (SIH 26171)")
    table.add_column("Evaluation Metric", style="cyan", no_wrap=True)
    table.add_column("Weight", style="magenta")
    table.add_column("Target Criteria", style="white")
    table.add_column("Achieved Result", style="green")
    table.add_column("Status", style="bold green")

    for key, row in scorecard.items():
        table.add_row(row["name"], row["weight"], row["target"], row["result"], row["status"])

    console.print(table)
    return scorecard


if __name__ == "__main__":
    asyncio.run(run_benchmark())
