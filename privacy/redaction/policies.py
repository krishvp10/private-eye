"""
Redaction Policies for PrivateEye.
Maps detected sensitive categories to specific visual redaction techniques.
Preserves layout, document boundaries, and button contexts while ensuring zero recoverable text.
"""

from shared.protocol import DetectionCategory, RedactionMethod

REDACTION_POLICIES = {
    DetectionCategory.PASSWORD: RedactionMethod.BLACKOUT,
    DetectionCategory.AADHAAR: RedactionMethod.MASK_DIGITS,
    DetectionCategory.PAN: RedactionMethod.MASK_CHARS,
    DetectionCategory.PHONE: RedactionMethod.MASK_DIGITS,
    DetectionCategory.EMAIL: RedactionMethod.MASK_CHARS,
    DetectionCategory.FACE: RedactionMethod.BLUR,
    DetectionCategory.NAME: RedactionMethod.MASK_CHARS,
    DetectionCategory.DOB: RedactionMethod.MASK_CHARS,
    DetectionCategory.ADDRESS: RedactionMethod.MASK_CHARS,
}


def get_redaction_method(category: DetectionCategory) -> RedactionMethod:
    """Return the designated redaction method for the specified sensitive category."""
    return REDACTION_POLICIES.get(category, RedactionMethod.BLACKOUT)
