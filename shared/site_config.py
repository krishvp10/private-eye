"""
Declarative Site Configuration Schema for PrivateEye.
Enables 100% data-driven demo portals, generic ground-truth generation,
and decoupled test oracles without hardcoding routes or form fields in Python code.
"""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from shared.protocol import DetectionCategory


class FieldConfig(BaseModel):
    id: str
    label: str
    field_type: str = "text"
    sensitive: bool = False
    category: DetectionCategory | None = None
    vault_ref: str | None = None
    autocomplete: str | None = None
    ground_truth_pattern: str | None = None
    default_value: str | None = None


class ActionConfig(BaseModel):
    id: str
    label: str
    role: str = "button"
    is_submit: bool = False


class RouteConfig(BaseModel):
    route: str
    title: str
    template: str = "form"  # "login", "form", "success"
    next_route: str | None = None
    has_face_avatar: bool = False
    badge_text: str | None = None
    fields: list[FieldConfig] = Field(default_factory=list)
    actions: list[ActionConfig] = Field(default_factory=list)


class SiteConfig(BaseModel):
    site_id: str
    display_name: str
    portal_title: str
    portal_subtitle: str
    theme_badge: str
    theme_badge_style: str = "color: #38bdf8; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.3);"
    task: str
    entry_route: str
    routes: list[RouteConfig] = Field(default_factory=list)

    def get_route(self, path: str) -> RouteConfig | None:
        """Find RouteConfig matching a specific path."""
        norm_path = path.split("?")[0].rstrip("/") or "/"
        for r in self.routes:
            if r.route.rstrip("/") == norm_path:
                return r
        return None

    def to_ground_truth(self) -> dict[str, Any]:
        """Generate ground-truth annotation dictionary for evaluation."""
        pages: dict[str, Any] = {}
        for r in self.routes:
            elements: list[dict[str, Any]] = []
            if r.has_face_avatar:
                elements.append(
                    {
                        "id": "field_face",
                        "category": "face",
                        "selector": "#field_face",
                        "type": "svg/image",
                        "sensitive": True,
                        "description": "Applicant biometric avatar",
                    }
                )
            for f in r.fields:
                if f.sensitive:
                    elements.append(
                        {
                            "id": f.id,
                            "category": f.category.value if f.category else "password",
                            "selector": f"#{f.id}",
                            "type": f.field_type,
                            "sensitive": True,
                            "ground_truth_pattern": f.ground_truth_pattern or f.default_value or "",
                        }
                    )
            if elements:
                pages[r.route] = {"elements": elements}
        return {"version": "2.0", "pages": pages}

    @classmethod
    def from_file(cls, path: str | Path) -> "SiteConfig":
        """Load SiteConfig from JSON or YAML file."""
        p = Path(path)
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)
