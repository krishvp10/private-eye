"""
Local Credential Vault for PrivateEye.
Stores private user profile values on the client machine ONLY.
Resolves server-issued 'value_ref' identifiers locally during action execution.
Values stored here never leave the client device over the network.
"""

import json
from pathlib import Path

from shared.vault_registry import assert_valid_value_ref

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_profiles.json"


def _load_default_profile() -> dict[str, str]:
    if FIXTURE_PATH.exists():
        try:
            with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("default_profile", {})
        except Exception:
            pass
    return {}


class LocalVault:
    """In-memory client-side secret vault."""

    DEFAULT_PROFILE: dict[str, str] = _load_default_profile() or {
        "user_profile.name": "Rahul Sharma",
        "user_profile.full_name": "Rahul Sharma",
        "user_profile.email": "rahul.sharma@example.com",
        "user_profile.phone": "9876543210",
        "user_profile.aadhaar": "4839 2176 5201",
        "user_profile.pan": "ABCDE1234F",
        "user_profile.dob": "1990-05-15",
        "user_profile.password": "SuperSecretPass123!",
        "user_profile.pin": "889241",
        "user_profile.address": "42 Palm Grove Road, Indiranagar, Bengaluru 560038",
        # Banking & Financial
        "user_profile.card_number": "4532 1148 9201 8842",
        "user_profile.cardholder": "Rahul Sharma",
        "user_profile.expiry": "08/28",
        "user_profile.cvv": "842",
        "user_profile.otp": "948211",
        # Healthcare & Medical
        "user_profile.uhid": "ABHA-2026-98142-990",
        "user_profile.diagnosis": "Type 2 Diabetes Mellitus with Mild Hypertension",
        "user_profile.prescription": "Metformin 500mg BD, Telmisartan 40mg OD, Atorvastatin 10mg HS",
        "user_profile.doctor": "Dr. Ananya Roy, MD (Cardiology)",
        "user_profile.insurance_id": "MEDICLAIM-POL-8849102",
        "user_profile.fixture_key": "FIXTURE-SECRET-XYZ-9912",
    }

    def __init__(self, profile_data: dict[str, str] | None = None) -> None:
        self._store = profile_data or dict(self.DEFAULT_PROFILE)

    def resolve(self, value_ref: str) -> str:
        """Resolve a value_ref key into its local secret value."""
        assert_valid_value_ref(value_ref)
        if value_ref not in self._store:
            # Fallback check stripping 'user_profile.' or 'profile.'
            norm_key = value_ref.replace("profile.", "user_profile.")
            if norm_key in self._store:
                return self._store[norm_key]
            raise KeyError(f"Vault key '{value_ref}' not found in local credential store.")
        return self._store[value_ref]

    def has_ref(self, value_ref: str) -> bool:
        norm_key = value_ref.replace("profile.", "user_profile.")
        return value_ref in self._store or norm_key in self._store

    def get_all_raw_secrets(self) -> list[str]:
        """Used exclusively by the security interceptor to verify zero leaks."""
        return list(self._store.values())
