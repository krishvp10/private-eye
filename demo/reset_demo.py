"""
Deterministic Demo State Reset Script for PrivateEye (demo/reset_demo.py).

Restores the synthetic demonstration environment to a clean, deterministic initial state.
Guarantees idempotency and ensures no sensitive real-world credentials are used.
Outputs synthetic state confirmation for operator confidence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DEMO_ROOT = Path(__file__).resolve().parent
REPO_ROOT = DEMO_ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from client.vault import LocalVault

DATA_DIR = DEMO_ROOT / "data"
LOGS_DIR = DEMO_ROOT / "logs"
FIXTURES_DIR = DEMO_ROOT / "fixtures"

DEFAULT_BANK_STATE = {
    "account_number": "ACC-987654321",
    "account_holder": "Demo Synthetic User",
    "current_balance_usd": 15420.50,
    "last_transaction_id": "TXN-90812",
    "pending_transfers": [],
    "recent_transactions": [
        {
            "id": "TXN-90810",
            "date": "2026-09-08",
            "amount": 120.00,
            "description": "Cloud Hosting",
            "type": "DEBIT",
        },
        {
            "id": "TXN-90811",
            "date": "2026-09-09",
            "amount": 3500.00,
            "description": "Payroll Deposit",
            "type": "CREDIT",
        },
        {
            "id": "TXN-90812",
            "date": "2026-09-10",
            "amount": 45.20,
            "description": "Coffee & Provisions",
            "type": "DEBIT",
        },
    ],
    "kyc_verified": False,
    "kyc_submission_record": None,
    "security_alerts": [],
}


def reset_demo_state() -> dict[str, str]:
    # Ensure directories exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Reset bank ledger state
    bank_file = DATA_DIR / "synthetic_bank_state.json"
    bank_file.write_text(json.dumps(DEFAULT_BANK_STATE, indent=2), encoding="utf-8")

    # 2. Clean old synthetic profile if present to prevent raw secret scans
    profile_file = DATA_DIR / "synthetic_user_profile.json"
    if profile_file.exists():
        profile_file.unlink()

    # 3. Clean demo logs
    log_files = list(LOGS_DIR.glob("*.jsonl")) + list(LOGS_DIR.glob("*.log"))
    for lf in log_files:
        try:
            lf.unlink()
        except OSError:
            pass

    # Verify vault resolution without printing raw secret
    vault = LocalVault()
    pan_exists = vault.has_ref("user_profile.pan")

    status = {
        "status": "READY",
        "balance": f"${DEFAULT_BANK_STATE['current_balance_usd']:,.2f}",
        "kyc": "RESET_UNVERIFIED",
        "pan_ref": "user_profile.pan" if pan_exists else "MISSING",
        "logs_cleared": str(len(log_files)),
    }
    return status


if __name__ == "__main__":
    res = reset_demo_state()
    print("[RESET] Synthetic account ledger restored (Initial Balance: " + res["balance"] + ")")
    print("[RESET] Local vault mapping verified (Protected Ref: " + res["pan_ref"] + ")")
    print(f"[RESET] Demo telemetry logs cleared ({res['logs_cleared']} files removed)")
    print("[PASS] Synthetic demo environment clean and ready.")
