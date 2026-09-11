# PrivateEye Frontend Design System Specification

**Document Version:** 1.0.0  
**Target Surface:** PrivateEye Privacy-Preserving Browser Agent Console & Landing Surface  
**Aesthetic Family:** Editorial Security Control Plane  
**Primary Canvas:** Strict Light Theme  

---

## 1. Design Philosophy: "Bounded Autonomy"

PrivateEye's core architectural thesis is:
> *PrivateEye does not try to make the model omnipotent. It makes the model bounded.*

The visual design directly manifests this philosophy:
- **Calm, High-Precision Light Canvas:** Unlike consumer AI chatbots or dark-themed hacker dashboards, PrivateEye is an authoritative, high-trust security tool. The design communicates discipline, mathematical precision, and absolute transparency.
- **Boundaries Over Shields:** Rather than clichéd locks, shields, or glowing AI gradients, the core visual grammar is built on **boundaries, coordinate markers, scanning frames, and redaction masks**.
- **Information Density with Hierarchy:** High data density (timings, hashes, candidate references) is rendered with editorial restraint. Visual noise is minimized; meaning is paramount.
- **Scientific Honesty:** No exaggerated security claims or simulated live telemetry disguised as reality. Empirical evaluations are labeled with their exact scope (Phase 10, Phase 11 Held-out, Synthetic Corpus, Controlled Dispatch Measurement).

---

## 2. Color Palette & Semantic Tokens

### Canvas & Neutral Surfaces
| Token | Hex Value | Usage |
|---|---|---|
| `--canvas-bg` | `#fbfbfa` | Base application background (warm neutral off-white) |
| `--surface-card` | `#ffffff` | Content panels, cards, data tables, and modal backgrounds |
| `--surface-subtle` | `#f4f4f2` | Table headers, secondary toolbars, chip backgrounds |
| `--surface-inset` | `#ebebe8` | Code blocks, input backgrounds, active timeline segments |
| `--border-subtle` | `#e5e7eb` | Primary hair-line grid and card borders |
| `--border-strong` | `#d1d5db` | Interactive focus boundaries, selected tabs |

### Typography Colors
| Token | Hex Value | Contrast Ratio (on `#ffffff`) | Usage |
|---|---|---|---|
| `--text-primary` | `#0f172a` | 15.6:1 (AAA) | Primary headings, table values, active states |
| `--text-secondary` | `#475569` | 6.8:1 (AAA) | Descriptive text, labels, secondary metadata |
| `--text-muted` | `#64748b` | 4.6:1 (AA) | Timestamps, micro-labels, disabled cues |
| `--text-faint` | `#94a3b8` | 2.9:1 | Decorative frame lines and watermarks only |

### Semantic Accent & Status Colors
| Category | Token | Hex Value | Background Tint | Usage |
|---|---|---|---|---|
| **Primary Interactive** | `--accent-cobalt` | `#1d4ed8` | `#eff6ff` | Active navigation, primary buttons, system links |
| **Protected / Success** | `--status-emerald` | `#059669` | `#ecfdf5` | Zero leak confirmation, postcondition pass, safe state |
| **Gated / Warning** | `--status-amber` | `#d97706` | `#fffbeb` | Human confirmation required, medium risk, spinner delay |
| **Blocked / Danger** | `--status-coral` | `#dc2626` | `#fef2f2` | Prompt injection blocked, fail-closed halt, kill switch |
| **Local Vault Marker** | `--status-violet` | `#7c3aed` | `#f5f3ff` | Local sensitive vault references (`$VAULT:REF`) |

---

## 3. Typography Hierarchy

### Typefaces
- **Primary Interface (Sans):** `'Instrument Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
  - Selected for crisp geometric letterforms, open counters, and high editorial legibility.
- **Technical & Forensic (Mono):** `'IBM Plex Mono', 'Geist Mono', 'SF Mono', Consolas, monospace`
  - Selected for tabular figures, uniform alignment of coordinates, hashes, and timing metrics.

### Scale & Rhythm
- **Display 1 (Hero Title):** `2.75rem (44px)` / Line-height `1.15` / Weight `700` / Tracking `-0.03em`
- **Heading 1 (Page Title):** `1.5rem (24px)` / Line-height `1.25` / Weight `600` / Tracking `-0.02em`
- **Heading 2 (Section Title):** `1.125rem (18px)` / Line-height `1.35` / Weight `600` / Tracking `-0.01em`
- **Body Regular:** `0.875rem (14px)` / Line-height `1.5` / Weight `400`
- **Body Medium:** `0.875rem (14px)` / Line-height `1.5` / Weight `500`
- **Caption / Metadata:** `0.75rem (12px)` / Line-height `1.4` / Weight `500` / Monospace
- **Micro Badge:** `0.6875rem (11px)` / Line-height `1` / Weight `600` / Monospace / Tracking `+0.04em`

---

## 4. Spacing, Borders & Shadows

- **Grid Base:** 4px baseline rhythm (`4px`, `8px`, `12px`, `16px`, `24px`, `32px`, `48px`, `64px`).
- **Border Radius:**
  - Badges / Chips: `4px` or `9999px` (pills)
  - Cards / Panels: `6px` or `8px` (restrained, never oversized)
  - Interactive Buttons: `6px`
  - Modal Dialogs: `8px`
- **Shadows:** Extremely soft, tactile elevation without diffuse dark blobs.
  - Subcard: `0 1px 2px rgba(0, 0, 0, 0.04)`
  - Elevated / Flyout: `0 4px 12px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04)`
  - Modal: `0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04)`

---

## 5. Interaction & Motion Rules

- **Motion Intensity:** Low to Medium (`duration: 150ms` to `250ms`, easing `cubic-bezier(0.16, 1, 0.3, 1)`).
- **Purpose-Driven Animation:**
  - Viewport transitions (subtle 8px fade-slide)
  - Tab state transitions
  - Bounding box overlay drawing on step progression
  - Scrubber timeline indicator movement
  - Latency waterfall bar extension
- **Accessibility:** Mandatory `@media (prefers-reduced-motion: reduce)` disabling all transitions.

---

## 6. Iconography Policy

- **SVG Only:** Strict ban on unicode emoji glyphs in interface chrome.
- All icons rendered as precise 16px or 20px vector paths with consistent `1.5px` or `1.75px` stroke weight.

---

## 7. Responsive Breakpoints

1. **Desktop Large / Ultrawide (≥1440px):**
   - 3-column live inspector view, persistent navigation sidebar (240px), expansive data tables with all forensic columns visible.
2. **Standard Desktop (1024px – 1439px):**
   - Balanced 2-column or stacked inspector view, persistent rail, full table horizontal scrolling with frozen ID columns.
3. **Tablet (768px – 1023px):**
   - Collapsed icon-rail navigation (64px) with tooltip labels, responsive card reflow, stacked screen views.
4. **Mobile (320px – 767px):**
   - Mobile top-bar with slide-out drawer navigation, tabbed screen toggle (Raw vs. Wire view), card-based record expansion instead of wide tables, full-width touch targets (minimum 44px hit area).
