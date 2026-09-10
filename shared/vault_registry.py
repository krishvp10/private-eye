"""
PrivateEye Central Typed Value Reference Registry.

Enforces strict structural rules for indirect secret identifiers ('value_ref').
Invariants:
1. Every value_ref must belong to an approved namespace ('user_profile.*', etc.).
2. A value_ref must never contain raw secrets.
3. A value_ref must never be logged with its resolved value.
"""

from enum import Enum


class StandardValueRef(str, Enum):
    # Identity & KYC
    NAME = "user_profile.name"
    FULL_NAME = "user_profile.full_name"
    EMAIL = "user_profile.email"
    PHONE = "user_profile.phone"
    AADHAAR = "user_profile.aadhaar"
    PAN = "user_profile.pan"
    DOB = "user_profile.dob"
    PASSWORD = "user_profile.password"
    PIN = "user_profile.pin"
    ADDRESS = "user_profile.address"

    # Financial & Banking
    CARD_NUMBER = "user_profile.card_number"
    CARDHOLDER = "user_profile.cardholder"
    EXPIRY = "user_profile.expiry"
    CVV = "user_profile.cvv"
    OTP = "user_profile.otp"

    # Healthcare & Medical
    UHID = "user_profile.uhid"
    DIAGNOSIS = "user_profile.diagnosis"
    PRESCRIPTION = "user_profile.prescription"
    DOCTOR = "user_profile.doctor"
    INSURANCE_ID = "user_profile.insurance_id"

    # Generic & Test Fixture Extension
    FIXTURE_KEY = "user_profile.fixture_key"


ALLOWED_NAMESPACES: set[str] = {"user_profile", "auth", "payment", "health"}


def is_valid_value_ref(value_ref: str) -> bool:
    """Check if value_ref adheres to the approved namespace structure."""
    if not value_ref or not isinstance(value_ref, str):
        return False
    parts = value_ref.split(".", 1)
    if len(parts) != 2:
        return False
    namespace, key = parts
    if namespace not in ALLOWED_NAMESPACES:
        return False
    if len(key) < 1 or any(c in key for c in [" ", "\t", "\n", ";", "<", ">"]):
        return False
    return True


def assert_valid_value_ref(value_ref: str) -> None:
    """Raise ValueError if the value_ref violates protocol namespace invariants."""
    if not is_valid_value_ref(value_ref):
        raise ValueError(
            f"Invalid value_ref '{value_ref}'. Must follow 'namespace.key' format using allowed namespaces: {ALLOWED_NAMESPACES}"
        )
