"""Compact terminal dashboard for a completed PrivateEye run."""

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table


def render_dashboard(summary: dict[str, Any]) -> None:
    console = Console()
    console.print("[bold green]RAW DATA NEVER TRANSMITTED[/bold green]")
    console.print(f"Run: {summary.get('run_id', 'unknown')} | Success: {summary.get('success', False)}")
    table = Table(title="PrivateEye Run Metrics")
    table.add_column("Step")
    table.add_column("URL")
    table.add_column("Detections", justify="right")
    table.add_column("Redactions", justify="right")
    table.add_column("Network ms", justify="right")
    table.add_column("Total ms", justify="right")
    for row in summary.get("telemetry", []):
        table.add_row(
            str(row["step"]),
            str(row["url"]),
            str(row["detections"]),
            str(row["redactions"]),
            f"{row['network_ms']:.1f}",
            f"{row['total_ms']:.1f}",
        )
    console.print(table)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a PrivateEye run summary")
    parser.add_argument("summary", type=Path, help="JSON summary produced by client.agent")
    args = parser.parse_args()
    with args.summary.open("r", encoding="utf-8") as handle:
        render_dashboard(json.load(handle))


if __name__ == "__main__":
    main()
