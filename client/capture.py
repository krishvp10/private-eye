"""
Playwright Capture Engine for PrivateEye.
Extracts screenshot, visible text, DOM interactive elements, bounding boxes,
and structured ScreenGraph while strictly omitting sensitive values.
"""

import argparse
import asyncio
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from playwright.async_api import Page, async_playwright

from shared.protocol import ScreenGraph, ScreenNode


@dataclass
class CapturedContext:
    url: str
    viewport: dict[str, int]
    screenshot_bytes: bytes
    visible_text: str
    screen_graph: ScreenGraph
    raw_elements: list[dict[str, Any]]
    aria_snapshot: str | None = None


JS_DOM_EXTRACTOR = """
() => {
    const interactiveSelectors = [
        'button', 'input', 'select', 'textarea', 'a[href]',
        '[role="button"]', '[role="checkbox"]', '[role="textbox"]',
        '[data-sensitive="true"]', 'svg[data-category="face"]'
    ];
    
    const elements = Array.from(document.querySelectorAll(interactiveSelectors.join(', ')));
    const results = [];
    
    elements.forEach((el, index) => {
        const rect = el.getBoundingClientRect();
        // Skip hidden or zero-size elements
        if (rect.width === 0 || rect.height === 0 || window.getComputedStyle(el).visibility === 'hidden') {
            return;
        }
        
        const isSensitive = Boolean(
            el.getAttribute('data-sensitive') === 'true' || 
            el.type === 'password' || 
            (el.getAttribute('autocomplete') && el.getAttribute('autocomplete').includes('password'))
        );
        
        // Find accessible name / label
        let name = el.getAttribute('aria-label') || el.innerText || '';
        if (!name && el.id) {
            const label = document.querySelector(`label[for="${el.id}"]`);
            if (label) {
                name = label.innerText.split('\\n')[0].trim();
            }
        }
        if (!name && el.name) {
            name = el.name;
        }
        name = name.trim().slice(0, 100);
        
        // Determine role
        let role = el.getAttribute('role') || el.tagName.toLowerCase();
        if (el.tagName.toLowerCase() === 'input') {
            role = el.type === 'checkbox' ? 'checkbox' : 'textbox';
        }
        
        // Stable local identifier
        const localId = el.id || `el_${index}`;
        
        results.push({
            id: localId,
            role: role,
            name: name,
            field_type: el.type || el.tagName.toLowerCase(),
            sensitive: Boolean(isSensitive),
            visible: true,
            enabled: el.disabled !== true,
            category: el.getAttribute('data-category') || (isSensitive ? 'sensitive' : null),
            bbox: [
                Math.round(rect.left + window.scrollX),
                Math.round(rect.top + window.scrollY),
                Math.round(rect.width),
                Math.round(rect.height)
            ],
            // STRICT PRIVACY GUARANTEE: Never include input value
            value: undefined
        });
    });
    
    return results;
}
"""

ARIA_NODE_RE = re.compile(
    r"^\s*-\s+(?P<role>[^\s\[]+)"
    r"(?:\s+\"(?P<name>[^\"]*)\")?"
    r".*?\[ref=(?P<ref>e\d+)\]"
    r"(?:\s+\[box=(?P<box>[^\]]+)\])?"
)


def _parse_aria_nodes(snapshot: str) -> list[dict[str, Any]]:
    """Parse the stable AI-mode ref/box records from Playwright's ARIA text."""
    nodes: list[dict[str, Any]] = []
    for line in snapshot.splitlines():
        match = ARIA_NODE_RE.match(line)
        if not match:
            continue
        box = None
        if match.group("box"):
            try:
                box = [float(value) for value in match.group("box").split(",")]
            except ValueError:
                box = None
        nodes.append(
            {
                "role": match.group("role"),
                "name": (match.group("name") or "").strip(),
                "ref": match.group("ref"),
                "bbox": box,
            }
        )
    return nodes


async def capture_page(page: Page, quality: int = 70) -> CapturedContext:
    """
    Capture full visual and structural context of the given page.
    Guarantees no passwords, tokens, or raw sensitive input values are placed in the ScreenGraph.
    """
    url = page.url
    viewport = page.viewport_size or {"width": 1280, "height": 800}

    # 1. Capture viewport screenshot (JPEG compressed)
    screenshot_bytes = await page.screenshot(
        type="jpeg",
        quality=quality,
        full_page=False,
    )

    # 2. Extract visible body text
    visible_text = await page.evaluate("() => document.body.innerText || ''")

    # 3. Extract interactive DOM nodes and bounding boxes.
    elements_data: list[dict[str, Any]] = await page.evaluate(JS_DOM_EXTRACTOR)

    # Prefer Playwright's AI-oriented ARIA snapshot when available. Playwright
    # 1.62 exposes the text snapshot with refs and boxes; JSON snapshots are
    # version-gated and therefore remain a future enhancement.
    aria_snapshot: str | None = None
    aria_nodes: list[dict[str, Any]] = []
    aria_snapshot_method = getattr(page, "aria_snapshot", None)
    if aria_snapshot_method is not None:
        try:
            aria_snapshot = await aria_snapshot_method(mode="ai", boxes=True)
            aria_nodes = _parse_aria_nodes(aria_snapshot)
        except Exception:
            aria_snapshot = None

    # Merge ARIA refs/boxes into the privacy-filtered interactive DOM records.
    # Matching uses role/name, while the local id remains the locator identity.
    used_aria: set[int] = set()
    for item in elements_data:
        for index, aria_node in enumerate(aria_nodes):
            if index in used_aria:
                continue
            if (
                item["role"] == aria_node["role"]
                and item["name"].strip() == aria_node["name"].strip()
            ):
                item["aria_ref"] = aria_node["ref"]
                if aria_node["bbox"]:
                    item["bbox"] = [round(value) for value in aria_node["bbox"]]
                used_aria.add(index)
                break

    # 4. Build ScreenGraph
    child_nodes = [
        ScreenNode(
            role=item["role"],
            name=item["name"],
            id=item["id"],
            ref=item.get("aria_ref") or f"e{index + 1}",
            bbox=item["bbox"],
            sensitive=bool(item.get("sensitive", False)),
            field_type=item["field_type"],
            visible=bool(item.get("visible", True)),
            enabled=bool(item.get("enabled", True)),
            children=[],
        )
        for index, item in enumerate(elements_data)
    ]

    root_node = ScreenNode(
        role="WebArea",
        name=await page.title(),
        id="root_0",
        bbox=[0, 0, viewport["width"], viewport["height"]],
        sensitive=False,
        field_type="document",
        visible=True,
        enabled=True,
        children=child_nodes,
    )

    screen_graph = ScreenGraph(
        root=root_node,
        url=url,
        viewport=viewport,
    )

    return CapturedContext(
        url=url,
        viewport=viewport,
        screenshot_bytes=screenshot_bytes,
        visible_text=visible_text,
        screen_graph=screen_graph,
        raw_elements=elements_data,
        aria_snapshot=aria_snapshot,
    )


async def run_cli(url: str, out_dir: str):
    """CLI runner to capture a page and persist artifacts."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(url, wait_until="networkidle")

        captured = await capture_page(page)

        # Write screenshot
        img_file = out_path / "screenshot.jpg"
        with open(img_file, "wb") as f:
            f.write(captured.screenshot_bytes)

        # Write screen graph JSON
        graph_file = out_path / "screen_graph.json"
        with open(graph_file, "w", encoding="utf-8") as f:
            f.write(captured.screen_graph.model_dump_json(indent=2))

        # Write visible text JSON
        text_file = out_path / "visible_text.json"
        with open(text_file, "w", encoding="utf-8") as f:
            json.dump({"url": captured.url, "visible_text": captured.visible_text}, f, indent=2)

        print(f"Captured page: {captured.url}")
        print(f"Screenshot saved: {img_file} ({len(captured.screenshot_bytes)} bytes)")
        print(
            f"ScreenGraph saved: {graph_file} ({len(captured.raw_elements)} interactive elements)"
        )
        print(f"Visible text saved: {text_file}")

        await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PrivateEye Page Capture Engine")
    parser.add_argument("--url", default="http://127.0.0.1:9001/kyc", help="Target URL to capture")
    parser.add_argument(
        "--out-dir", default="scratch/capture", help="Output directory for captured files"
    )
    args = parser.parse_args()

    asyncio.run(run_cli(args.url, args.out_dir))
