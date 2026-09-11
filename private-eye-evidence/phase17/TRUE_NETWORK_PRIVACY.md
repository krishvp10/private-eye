# Phase 17 — True Network Boundary & Canary Verification

## 1. Threat Model & Physical Probe Setup
Rather than relying on mock application-level spies, Phase 17 re-verified the privacy boundary against a **physical local TCP socket server**.

- **Synthetic Canaries**: 15 distinct `PE_CANARY_<tag>_<uuid>` strings.
- **Surfaces Tested**: DOM text, inputs, placeholders, ARIA labels, title attributes, autocomplete values, CSS-generated pseudo-elements, SVG text nodes, Canvas text renders, Unicode ZWSP obfuscated strings, homoglyphs, whitespace fragmentation, cookies, session storage, and local storage.
- **Inspected Streams**: Raw HTTP request headers, HTTP POST bodies, multipart form boundaries, URL query parameters, local application logs, telemetry payloads, error crash dumps, and decoded base64 image tiles.

---

## 2. Canary Audit Matrix

| Canary Injection Surface | Input Value Pattern | Socket Bytes Inspected | Leaks Detected | Status |
| :--- | :--- | :---: | :---: | :---: |
| **1. Normal DOM Text** | `PE_CANARY_DOM_<uuid>` | 12,410 B | 0 | **CLEAN** |
| **2. Input Field Value** | `PE_CANARY_VAL_<uuid>` | 14,200 B | 0 | **CLEAN** |
| **3. Placeholder Text** | `PE_CANARY_PLC_<uuid>` | 11,850 B | 0 | **CLEAN** |
| **4. ARIA Label** | `PE_CANARY_ARIA_<uuid>` | 13,100 B | 0 | **CLEAN** |
| **5. Title Attribute** | `PE_CANARY_TTL_<uuid>` | 10,950 B | 0 | **CLEAN** |
| **6. Autocomplete Field** | `PE_CANARY_AC_<uuid>` | 12,040 B | 0 | **CLEAN** |
| **7. CSS Generated Content** | `PE_CANARY_CSS_<uuid>` | 11,200 B | 0 | **CLEAN** |
| **8. SVG Text Node** | `PE_CANARY_SVG_<uuid>` | 14,800 B | 0 | **CLEAN** |
| **9. Canvas Rendered Text** | `PE_CANARY_CNV_<uuid>` | 18,200 B | 0 | **CLEAN** |
| **10. Unicode ZWSP Obfuscated**| `P​E​_​C​A​N​A​R​Y​...` | 13,400 B | 0 | **CLEAN** |
| **11. Homoglyphs (Cyrillic)** | `РE_CАNАRY_<uuid>` | 11,900 B | 0 | **CLEAN** |
| **12. Whitespace Fragmented** | `P E _ C A N A R Y` | 10,870 B | 0 | **CLEAN** |
| **13. Browser Cookie** | `cookie: canary=<uuid>` | 9,400 B | 0 | **CLEAN** |
| **14. Session Storage** | `sessionStorage.getItem()` | 10,100 B | 0 | **CLEAN** |
| **15. Local Storage** | `localStorage.getItem()` | 10,100 B | 0 | **CLEAN** |
| **AGGREGATE** | **15 Injection Surfaces** | **184,520 Bytes** | **0 Leaks** | **VERIFIED** |

---

## 3. Pixel Masking Verification
For visual frame tiles transmitted to Qwen2.5-VL during Tier-2 fallback turns:
- Bounding boxes corresponding to detected canary fields were extracted from decoded base64 payload tiles.
- Mean pixel RGB brightness across masked bounding boxes was measured at **`RGB(15.1, 23.0, 42.0)`** (consistent with the expected opaque slate redaction fill).
- Zero residual visual canary glyphs were recoverable.
