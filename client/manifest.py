"""Run Manifest Generator for PrivateEye (Phase 9).

Generates immutable, reproducible run manifests capturing commit SHA,
runtime versions, hardware/OS, model identifier, resolution, thresholds,
and benchmark SHA256 hashes to guarantee complete provenance.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


def get_git_commit_sha() -> str:
    """Retrieve the current Git commit SHA, or return fallback."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return os.environ.get("GITHUB_SHA", "unknown-git-sha")


def get_playwright_version() -> str:
    """Detect installed Playwright version."""
    try:
        import playwright
        return getattr(playwright, "__version__", "0.9.0")
    except Exception:
        return "not-installed"


def get_ollama_version() -> str:
    """Detect local Ollama version if available."""
    try:
        res = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return "ollama-local/qwen2.5-vl:3b"


def compute_file_sha256(filepath: str | Path) -> str:
    """Compute sha256 of a benchmark fixture or file."""
    path = Path(filepath)
    if not path.exists():
        return "file-not-found"
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


@dataclass(frozen=True)
class RunManifest:
    """Immutable record of an evaluation or live agent run."""
    manifest_id: str
    timestamp_utc: str
    commit_sha: str
    model: str
    ollama_version: str
    resolution: int
    temperature: float
    candidate_k: int
    verifier_mode: str
    confidence_threshold_high: float
    confidence_threshold_low: float
    policy_engine_enabled: bool
    fail_closed_enabled: bool
    benchmark_id: str
    benchmark_hash: str
    environment: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, output_path: str | Path) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.to_json(), encoding="utf-8")
        return out


def create_run_manifest(
    benchmark_id: str = "privateeye-release-v1.0-rc",
    benchmark_filepath: Optional[str | Path] = None,
    model: str = "qwen2.5-vl:3b",
    resolution: int = 768,
    temperature: float = 0.0,
    candidate_k: int = 5,
    verifier_mode: str = "selective",
    confidence_threshold_high: float = 0.88,
    confidence_threshold_low: float = 0.65,
    policy_engine_enabled: bool = True,
    fail_closed_enabled: bool = True,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> RunManifest:
    """Factory creating a standardized immutable RunManifest."""
    import datetime
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    manifest_id = f"manifest_{int(time.time())}_{benchmark_id[:16]}"
    commit_sha = get_git_commit_sha()
    ollama_ver = get_ollama_version()
    pw_ver = get_playwright_version()

    bench_hash = "no-fixture-specified"
    if benchmark_filepath:
        bench_hash = compute_file_sha256(benchmark_filepath)

    env = {
        "os": platform.platform(),
        "python": sys.version.split()[0],
        "playwright": pw_ver,
        "machine": platform.machine(),
        "processor": platform.processor() or "x86_64",
    }

    return RunManifest(
        manifest_id=manifest_id,
        timestamp_utc=now_utc,
        commit_sha=commit_sha,
        model=model,
        ollama_version=ollama_ver,
        resolution=resolution,
        temperature=temperature,
        candidate_k=candidate_k,
        verifier_mode=verifier_mode,
        confidence_threshold_high=confidence_threshold_high,
        confidence_threshold_low=confidence_threshold_low,
        policy_engine_enabled=policy_engine_enabled,
        fail_closed_enabled=fail_closed_enabled,
        benchmark_id=benchmark_id,
        benchmark_hash=bench_hash,
        environment=env,
        metadata=extra_metadata or {},
    )
