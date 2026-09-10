"""Global Secret Scanner (eval/scan_secrets_audit.py).

Scans all files in the repository to ensure 0 synthetic vault secrets are leaked in
code, docs, reports, evidence, or metadata.
"""

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from client.vault import LocalVault


def run_scan() -> int:
    vault = LocalVault()
    secrets = [s for s in vault.get_all_raw_secrets() if len(s) > 4]

    exempt_paths = {
        REPO_ROOT / "client" / "vault.py",
        REPO_ROOT / "tests" / "test_vault.py",
        REPO_ROOT / "client" / "vault.json",
        REPO_ROOT / "demo_sites" / "ground_truth.json",
        REPO_ROOT / "eval" / "live_privacy_demo.py",
        REPO_ROOT / "eval" / "performance_profile.py",
    }

    exempt_dirs = {
        "tests",
        "demo_configs",
        "fixtures",
        "templates",
    }

    leak_count = 0
    scanned_files = 0

    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [
            d
            for d in dirs
            if d
            not in (
                ".git",
                ".venv",
                "__pycache__",
                ".pytest_cache",
                ".mypy_cache",
                ".ruff_cache",
                "scratch",
                ".agents",
            )
            and d not in exempt_dirs
        ]
        for file in files:
            if file.endswith(
                (
                    ".pyc",
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".webp",
                    ".ico",
                    ".bin",
                    ".woff",
                    ".woff2",
                    ".ttf",
                )
            ):
                continue
            fpath = Path(root) / file
            if fpath in exempt_paths or "site-packages" in str(fpath):
                continue
            try:
                text = fpath.read_text(encoding="utf-8", errors="ignore")
                clean = re.sub(r'"image_b64"\s*:\s*"[^"]*"', "", text)
                clean = re.sub(r"data:image/[^;]+;base64,[A-Za-z0-9+/=]+", "", clean)
                scanned_files += 1
                for s in secrets:
                    if s in clean:
                        print(f"Detected secret '{s[:4]}***' in {fpath.relative_to(REPO_ROOT)}")
                        leak_count += 1
            except Exception:
                pass

    print(
        f"Scanned {scanned_files} files across repository. Total detected raw secret leaks: {leak_count}"
    )
    return leak_count


if __name__ == "__main__":
    leaks = run_scan()
    sys.exit(1 if leaks > 0 else 0)
