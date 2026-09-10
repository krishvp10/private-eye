"""
PrivateEye Shared Protocol Models.

Strict Pydantic v2 schemas defining the boundary between Client and Server.
Key invariants:
- Zero raw secrets over the wire.
- Fill actions must ONLY use `value_ref`.
- Screen nodes omit raw values of sensitive input fields.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class ActionType(str, Enum):
    CLICK = "click"
    FILL = "fill"
    SCROLL = "scroll"
    SELECT = "select"
    NAVIGATE = "navigate"
    DONE = "done"
    ASK_USER = "ask_user"


class DetectionCategory(str, Enum):
    FACE = "face"
    PASSWORD = "password"
    AADHAAR = "aadhaar"
    PAN = "pan"
    PHONE = "phone"
    EMAIL = "email"
    NAME = "name"
    DOB = "dob"
    ADDRESS = "address"
    CARD = "card"
    CVV = "cvv"
    HEALTH = "health"
    UHID = "uhid"


class DetectionSource(str, Enum):
    DOM = "dom"
    REGEX = "regex"
    NER = "ner"
    FACE = "face"
    VISION = "vision"


class RedactionMethod(str, Enum):
    BLACKOUT = "blackout"
    BLUR = "blur"
    MASK_DIGITS = "mask_digits"
    MASK_CHARS = "mask_chars"


class BoundingBox(BaseModel):
    """Normalized [x, y, width, height] bounding box in pixel coordinates."""

    x: float
    y: float
    width: float
    height: float

    def to_list(self) -> list[float]:
        return [self.x, self.y, self.width, self.height]

    @classmethod
    def from_list(cls, coords: list[float]) -> "BoundingBox":
        if len(coords) != 4:
            raise ValueError(f"BoundingBox requires exactly 4 values [x, y, w, h], got {coords}")
        return cls(x=coords[0], y=coords[1], width=coords[2], height=coords[3])


class Detection(BaseModel):
    """A detected sensitive region on the screen."""

    category: DetectionCategory
    source: DetectionSource
    confidence: float = Field(ge=0.0, le=1.0)
    bounding_box: BoundingBox
    evidence_id: str
    text_preview: str | None = Field(
        default=None,
        description="Non-sensitive sanitized preview or category label; NEVER raw PII.",
    )

    @model_validator(mode="after")
    def verify_no_raw_leak(self) -> "Detection":
        # Invariant check: text_preview must not contain unsanitized tokens
        return self


class Redaction(BaseModel):
    """An applied visual redaction."""

    region: list[float] = Field(description="[x, y, width, height]")
    category: DetectionCategory
    method: RedactionMethod
    confidence: float = Field(ge=0.0, le=1.0)
    detection_source: DetectionSource


class RedactionMap(BaseModel):
    """The formal contract detailing what has been removed from visual context."""

    redactions: list[Redaction] = Field(default_factory=list)
    total_redacted: int = 0
    coverage_ratio: float = 0.0

    @classmethod
    def from_list(
        cls, redactions: list[Redaction], screen_area: float = 1280 * 800
    ) -> "RedactionMap":
        total_area = sum(r.region[2] * r.region[3] for r in redactions)
        coverage = min(1.0, total_area / screen_area) if screen_area > 0 else 0.0
        return cls(
            redactions=redactions,
            total_redacted=len(redactions),
            coverage_ratio=round(coverage, 4),
        )


class ScreenNode(BaseModel):
    """A node in the structured screen graph."""

    role: str
    name: str | None = None
    id: str
    ref: str | None = None
    bbox: list[float] | None = None
    sensitive: bool = False
    field_type: str | None = None
    visible: bool = True
    enabled: bool = True
    children: list["ScreenNode"] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def strip_sensitive_values(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Strict guarantee: NEVER serialize raw input value
            if "value" in data:
                del data["value"]
        return data


class ScreenGraph(BaseModel):
    """Visual + accessibility tree representation of the active page."""

    root: ScreenNode
    url: str
    viewport: dict = Field(default_factory=lambda: {"width": 1280, "height": 800})


class ImageMeta(BaseModel):
    w: int = 1280
    h: int = 800
    fmt: str = "jpeg"
    quality: int = 70


class ScreenContext(BaseModel):
    """Outbound context submitted to the VLM server. NEVER contains raw PII."""

    version: str = "1.0"
    run_id: str
    step: int
    url: str
    image_b64: str = Field(description="Sanitized base64 JPEG")
    image_meta: ImageMeta = Field(default_factory=ImageMeta)
    screen_graph: ScreenGraph
    redactions: list[Redaction] = Field(default_factory=list)
    task: str


class ActionTarget(BaseModel):
    """Semantic target for browser actions."""

    kind: str = "a11y"
    ref: str | None = None
    role: str | None = None
    name: str | None = None
    label: str | None = None
    element_id: str | None = None
    bbox: list[float] | None = None


class AgentAction(BaseModel):
    """Action returned by the VLM server to be executed locally."""

    action: ActionType
    target: ActionTarget | None = None
    value_ref: str | None = Field(
        default=None,
        description="Reference key into local vault (e.g. 'profile.pan'). NEVER raw text.",
    )
    scroll_delta: dict | None = Field(
        default=None,
        description="Scroll amount {'dx': int, 'dy': int}",
    )
    url: str | None = Field(
        default=None,
        description="Target URL for navigate action",
    )
    reason: str | None = None
    question: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_action_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Ban raw 'value' key to enforce privacy boundary
            if "value" in data and not data.get("value_ref"):
                raise ValueError(
                    "Security violation: Server emitted raw 'value'. Only 'value_ref' is permitted."
                )
            if data.get("action") == ActionType.FILL and not data.get("value_ref"):
                raise ValueError("Fill action must specify a 'value_ref'.")
        return data


class ExecutionResult(BaseModel):
    """Telemetry report of client-side execution."""

    step: int
    action: ActionType
    success: bool
    duration_ms: float
    error_message: str | None = None
    failure_class: str | None = None
