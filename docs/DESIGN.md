# DESIGN.md — UX/UI Specification

## Design principles
1. **Privacy is visible**: masking happens on screen *before the user's eyes* — animate it.
2. **The server is a guest**: show exactly what the guest can see ("server view" panel = sanitized image).
3. **Human on the loop**: destructive actions always pause for confirmation.
4. **Numbers on stage**: every rubric metric has a live number on the dashboard.

## Information architecture (dashboard — the primary UI)

```
┌────────────────────────────────────────────────────────────┐
│ PrivateEye  · task: "Complete KYC form"   [⏸ pause][■ stop]│
├───────────────┬───────────────────────┬────────────────────┤
│ LIVE SCREEN   │  SERVER VIEW          │  STEP WATERFALL    │
│ (raw, local)  │  (sanitized, outbound)│  capture   120ms   │
│               │                       │  detect    90ms    │
│               │                       │  redact    40ms    │
│               │                       │  network   35ms    │
│               │                       │  vlm       1900ms  │
│               │                       │  execute   60ms    │
├───────────────┴───────────────────────┴────────────────────┤
│ REDACTION FEED  ▣ face→blur ▣ password→blackout ▣ aadhaar→mask│
│ METRICS  PII-F1 0.91 · redact-IoU 0.97 · RAM 812MB · step 2.2s │
└────────────────────────────────────────────────────────────┘
```

## Screen inventory
- **S-1 Agent run (main)**: live screen vs server view side-by-side; redaction feed; waterfall; metrics strip.
  States: idle / running / waiting-user-confirm (modal) / done (report) / error (with diagnosis).
- **S-2 Confirmation modal**: shows exact action + resolved target; Approve / Edit / Abort. Keyboard-first (Enter=Approve is NOT default; Space focuses Approve explicitly).
- **S-3 Benchmark report**: confusion matrix, per-category P/R/F1, redaction IoU, latency percentiles, resource graphs. Exportable PNG for slides.
- **S-4 Settings (V1)**: redaction policy per category (blur/blackout/mask/off), vault editor.

## Design system (minimal, hackathon-appropriate)
- Monospace for protocol/redaction data (IBM Plex Mono), Inter for UI; 8-pt spacing grid; dark theme
  (projector-friendly). Status colors: green (sent-clean), amber (awaiting user), red (blocked/leak-check fail).
- Components: mask chips (category icon + method), waterfall bars, metric tiles, confirmation modal.
- Notifications: redaction feed entries animate in on detection; leak-check failure = hard red banner.

## Responsive
Dashboard is desktop-first (1280×800 min) — hackathon demo context. Client confirmation modal must work
at any viewport via Playwright-driven browser (it inherits page styles).

## Accessibility
WCAG 2.1 AA for dashboard: full keyboard nav, focus trap in modal, contrast ≥4.5:1, `aria-live` on
redaction feed and metrics. Reduced-motion respected (mask animations become instant).

## UX edge cases
Empty redaction feed ("nothing sensitive found — sent as-is, verified") · server timeout (show last
successful step + retry) · vault missing a value (ask_user: "Enter your PAN locally") · over-masking
flag in benchmark (IoU<1 on non-PII → tuning hint in report).
