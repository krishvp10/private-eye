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
    if not FIXTURE_PATH.exists():
        raise FileNotFoundError(f"Synthetic profile fixture is missing: {FIXTURE_PATH}")
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    profile = data.get("default_profile")
    if not isinstance(profile, dict) or not profile:
        raise ValueError(f"Synthetic profile fixture has no default_profile: {FIXTURE_PATH}")
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in profile.items()):
        raise ValueError(f"Synthetic profile fixture contains non-string values: {FIXTURE_PATH}")
    return profile


class LocalVault:
    """In-memory client-side secret vault."""

    DEFAULT_PROFILE: dict[str, str] = _load_default_profile()

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
