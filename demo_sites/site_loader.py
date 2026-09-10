"""
Dynamic Demo Site Loader and Template Renderer.
Loads declarative SiteConfig JSON files from demo_configs/ and renders
accessible, semantic HTML pages with zero copy-pasting.
"""

from pathlib import Path
from typing import Any

from shared.site_config import FieldConfig, RouteConfig, SiteConfig

CONFIGS_DIR = Path(__file__).resolve().parent.parent / "demo_configs"


class SiteRegistry:
    """In-memory registry of declarative demo site configurations."""

    def __init__(self, configs_dir: Path | None = None) -> None:
        self.configs_dir = configs_dir or CONFIGS_DIR
        self._sites: dict[str, SiteConfig] = {}
        self.reload()

    def reload(self) -> None:
        """Scan demo_configs/ directory and load all JSON site definitions."""
        self._sites.clear()
        if self.configs_dir.exists():
            for f in self.configs_dir.glob("*.json"):
                try:
                    site = SiteConfig.from_file(f)
                    self._sites[site.site_id] = site
                except Exception as e:
                    print(f"Warning: Failed to load config {f}: {e}")

    def get_site(self, site_id: str) -> SiteConfig | None:
        return self._sites.get(site_id)

    def get_all_sites(self) -> list[SiteConfig]:
        return list(self._sites.values())

    def find_route(self, path: str) -> tuple[SiteConfig, RouteConfig] | None:
        """Find the matching (SiteConfig, RouteConfig) for any given URL path or full URL."""
        from urllib.parse import urlparse
        parsed = urlparse(path)
        norm = (parsed.path if (parsed.netloc or path.startswith("http")) else path).split("?")[0].rstrip("/") or "/"
        for site in self._sites.values():
            for route in site.routes:
                if route.route.rstrip("/") == norm:
                    return site, route
        return None

    def export_combined_ground_truth(self) -> dict[str, Any]:
        """Aggregate ground-truth annotations across all active demo sites."""
        combined: dict[str, Any] = {"version": "2.0", "description": "Auto-generated from declarative demo_configs", "pages": {}}
        for site in self._sites.values():
            gt = site.to_ground_truth()
            combined["pages"].update(gt["pages"])
        return combined


registry = SiteRegistry()


def render_field_html(field: FieldConfig) -> str:
    """Render semantic form field HTML with accessibility and data attributes."""
    tag_badge = ""
    sensitive_attr = ""
    category_attr = ""
    autocomplete_attr = f'autocomplete="{field.autocomplete}"' if field.autocomplete else ""

    if field.sensitive:
        cat_name = field.category.value.upper() if field.category else "PII"
        tag_badge = f'<span class="field-sensitive-tag">[PROTECTED: {cat_name}]</span>'
        sensitive_attr = 'data-sensitive="true"'
        category_attr = f'data-category="{field.category.value if field.category else "password"}"'

    val = field.default_value or ""

    if field.field_type == "textarea":
        return f"""
        <div class="form-group form-full">
          <label for="{field.id}">{field.label} {tag_badge}</label>
          <textarea id="{field.id}" name="{field.id}" rows="3" required aria-label="{field.label}" {sensitive_attr} {category_attr} {autocomplete_attr}>{val}</textarea>
        </div>"""

    return f"""
        <div class="form-group">
          <label for="{field.id}">{field.label} {tag_badge}</label>
          <input type="{field.field_type}" id="{field.id}" name="{field.id}" value="{val}" required aria-label="{field.label}" {sensitive_attr} {category_attr} {autocomplete_attr}>
        </div>"""


def render_page_html(site: SiteConfig, route: RouteConfig) -> str:
    """Render a complete, responsive HTML page driven 100% by declarative configuration."""
    next_action = route.next_route or "/success"

    # Handle success page
    if route.template == "success":
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{route.title}</title>
  <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
  <div class="brand-header">
    <div class="brand-badge" style="{site.theme_badge_style}">
      {site.theme_badge}
    </div>
    <h1 class="portal-title">{site.portal_title}</h1>
    <p class="portal-subtitle">{site.portal_subtitle}</p>
  </div>
  <main class="card" role="main">
    <div style="text-align: center; padding: 2rem 1rem;">
      <div style="width: 64px; height: 64px; margin: 0 auto 1.5rem; background: rgba(16, 185, 129, 0.15); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #10b981; font-size: 2rem;">✓</div>
      <div class="brand-badge" style="background: rgba(16, 185, 129, 0.15); color: #10b981; margin-bottom: 0.75rem;">{route.badge_text or "SUCCESS CONFIRMED"}</div>
      <h2 id="success_heading" style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">{route.title}</h2>
      <p style="color: var(--text-dim); margin-bottom: 2rem;">All credentials verified locally. Zero raw personal data exposed on the wire.</p>
      <button id="btn_return" class="btn btn-primary" onclick="window.location.href='{site.entry_route}'">Return to Home</button>
    </div>
  </main>
  <script src="/static/js/debug.js"></script>
</body>
</html>"""

    # Form Fields & Avatar
    avatar_html = ""
    if route.has_face_avatar:
        avatar_html = """
        <div class="form-group form-full" style="display: flex; align-items: center; gap: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color);">
          <div id="field_face" class="face-avatar" data-sensitive="true" data-category="face" aria-label="Applicant Biometric Portrait" style="width: 72px; height: 72px; border-radius: 50%; background: linear-gradient(135deg, #0284c7, #2563eb); display: flex; align-items: center; justify-content: center; font-size: 2rem; border: 2px solid rgba(56, 189, 248, 0.5);">
            👤
          </div>
          <div>
            <div style="font-weight: 600; font-size: 0.95rem;">Applicant Biometric Portrait</div>
            <div style="font-size: 0.8rem; color: var(--text-dim);">Live capture verified • [BIOMETRIC PII: FACE BLUR]</div>
          </div>
        </div>"""

    fields_html = "\n".join(render_field_html(f) for f in route.fields)

    # Action buttons
    actions_html = ""
    for act in route.actions:
        if act.role == "checkbox":
            actions_html += f"""
            <label class="consent-row">
              <input type="checkbox" id="{act.id}" name="{act.id}" aria-label="{act.label}">
              <span>{act.label}</span>
            </label>
            """
            continue
        btn_class = "btn btn-primary" if act.is_submit else "btn btn-secondary"
        btn_type = "submit" if act.is_submit else "button"
        actions_html += f'<button type="{btn_type}" id="{act.id}" class="{btn_class}" role="button">{act.label}</button>\n'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{route.title}</title>
  <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
  <div class="brand-header">
    <div class="brand-badge" style="{site.theme_badge_style}">
      {site.theme_badge}
    </div>
    <h1 class="portal-title">{site.portal_title}</h1>
    <p class="portal-subtitle">{site.portal_subtitle}</p>
  </div>

  <main class="card" role="main">
    <form id="form_{site.site_id}" action="{route.route}" method="POST">
      <div class="form-grid">
        {avatar_html}
        {fields_html}
      </div>

      <div class="actions-row" style="margin-top: 1.5rem;">
        {actions_html}
      </div>
    </form>
  </main>

  <script src="/static/js/debug.js"></script>
</body>
</html>"""
