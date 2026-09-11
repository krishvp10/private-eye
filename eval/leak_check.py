"""
Outbound Leak Interceptor and Security Gate.
Defense-in-depth security barrier that intercepts outbound HTTP requests
and scans them for raw PII strings or credentials from the local vault.
Blocks network transmission immediately if any leak is detected.
"""

import base64
import json
import re

from client.vault import LocalVault
from privacy.detectors.regex import PATTERNS


class SecurityLeakException(Exception):
    """Raised when an outbound payload contains raw sensitive user data."""


class OutboundLeakInterceptor:
    """Intercepts and verifies outbound JSON payloads before transmission."""

    def __init__(self, vault: LocalVault | None = None) -> None:
        self.vault = vault or LocalVault()

    def inspect_payload(self, payload_text: str) -> list[str]:
        """
        Scans outbound payload text for:
        1. Known local secrets from the vault (Aadhaar, PAN, Password, Phone, Email, etc.)
        2. High-confidence regex patterns (unredacted PAN or formatted Aadhaar)
        Returns a list of leak violations detected.
        """
        violations: list[str] = []

        # Check 1: Exact vault raw secrets (and Unicode-normalized secrets)
        norm_payload = re.sub(r"[\u200b\u200c\u200d\u200e\u200f\ufeff\u00ad\u2060-\u2064]", "", payload_text)
        norm_payload = re.sub(r"\\u(?:200[b-fB-F]|206[0-4]|feff|00ad)", "", norm_payload, flags=re.IGNORECASE)
        for secret in self.vault.get_all_raw_secrets():
            if len(secret) > 4 and (secret in payload_text or secret in norm_payload):
                violations.append(f"Direct raw secret exposed in payload: '{secret[:3]}***'")

        # Check 2: Decoded image bytes scan for literal embedded raw secrets
        img_b64_data: str | None = None
        try:
            parsed_json = json.loads(payload_text)
            if isinstance(parsed_json, dict) and isinstance(parsed_json.get("image_b64"), str):
                img_b64_data = parsed_json["image_b64"]
        except Exception:  # noqa: BLE001
            img_match = re.search(r'"image_b64"\s*:\s*"([^"]+)"', payload_text)
            if img_match:
                img_b64_data = img_match.group(1)

        if img_b64_data:
            try:
                decoded_img = base64.b64decode(img_b64_data)
                for secret in self.vault.get_all_raw_secrets():
                    if len(secret) > 4 and secret.encode("utf-8") in decoded_img:
                        violations.append(
                            f"Raw vault secret embedded in image_b64 pixels: '{secret[:3]}***'"
                        )
            except Exception:  # noqa: BLE001, S110
                pass

        # Check 3: High-confidence regex patterns in textual fields.
        # Exclude base64 image data to prevent false-positive collisions
        # between text patterns (such as DOB \d{2}/\d{2} or 12-digit Aadhaar) and random
        # characters in base64 binary image encoding.
        text_for_regex = re.sub(r'"image_b64"\s*:\s*"[^"]*"', '"image_b64": ""', payload_text)
        cleaned_text = re.sub(r"[\u200b\u200c\u200d\u200e\u200f\ufeff\u00ad]", "", text_for_regex)
        for cat, regex in PATTERNS.items():
            matches = regex.findall(text_for_regex) or regex.findall(cleaned_text)
            if matches:
                violations.append(
                    f"Unsanitized pattern '{cat.value}' detected in payload: {len(matches)} occurrence(s)"
                )

        return violations

    def assert_safe(self, payload_text: str) -> None:
        """Enforces zero-leak policy; raises SecurityLeakException on any violation."""
        violations = self.inspect_payload(payload_text)
        if violations:
            raise SecurityLeakException(
                f"CRITICAL SECURITY LEAK INTERCEPTED! Transmission aborted. Violations: {violations}"
            )

    def inspect_request(self, url: str, headers: dict, body: bytes) -> dict:
        """Return a privacy-safe, machine-readable inspection report."""
        components = {
            "url": url,
            "headers": str(headers),
            "body": body.decode("utf-8", errors="replace"),
        }
        violations: list[str] = []
        for name, value in components.items():
            found = self.inspect_payload(value)
            violations.extend(f"{name}: {violation}" for violation in found)
        return {
            "safe": not violations,
            "checked_components": list(components),
            "violation_count": len(violations),
            "violations": [
                violation.split("'", 1)[0] + "'***'" if "'" in violation else violation
                for violation in violations
            ],
        }
