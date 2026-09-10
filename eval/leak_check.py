"""
Outbound Leak Interceptor and Security Gate.
Defense-in-depth security barrier that intercepts outbound HTTP requests
and scans them for raw PII strings or credentials from the local vault.
Blocks network transmission immediately if any leak is detected.
"""

from typing import List, Optional
from client.vault import LocalVault
from privacy.detectors.regex import PATTERNS


class SecurityLeakException(Exception):
    """Raised when an outbound payload contains raw sensitive user data."""
    pass


class OutboundLeakInterceptor:
    """Intercepts and verifies outbound JSON payloads before transmission."""

    def __init__(self, vault: Optional[LocalVault] = None) -> None:
        self.vault = vault or LocalVault()

    def inspect_payload(self, payload_text: str) -> List[str]:
        """
        Scans outbound payload text for:
        1. Known local secrets from the vault (Aadhaar, PAN, Password, Phone, Email, etc.)
        2. High-confidence regex patterns (unredacted PAN or formatted Aadhaar)
        Returns a list of leak violations detected.
        """
        violations: List[str] = []

        # Check 1: Exact vault raw secrets
        for secret in self.vault.get_all_raw_secrets():
            if len(secret) > 4 and secret in payload_text:
                violations.append(f"Direct raw secret exposed in payload: '{secret[:3]}***'")

        # Check 2: Formatted Aadhaar match in payload
        aadhaar_matches = PATTERNS[PATTERNS.keys().__iter__().__next__()].findall(payload_text)
        for cat, regex in PATTERNS.items():
            matches = regex.findall(payload_text)
            if matches:
                violations.append(f"Unsanitized pattern '{cat.value}' detected in payload: {len(matches)} occurrence(s)")

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
        violations = []
        for name, value in components.items():
            found = self.inspect_payload(value)
            violations.extend(f"{name}: {violation}" for violation in found)
        return {
            "safe": not violations,
            "checked_components": list(components),
            "violation_count": len(violations),
            "violations": [
                violation.split("'", 1)[0] + "'***'"
                if "'" in violation
                else violation
                for violation in violations
            ],
        }
