# ADR-0004: Redaction via DOM/a11y boxes + text detection + face model (not pure vision)
Status: Accepted (2026-09-10)
Context: Rubric grades recall/precision of PII detection AND redaction precision. Pure-vision redaction
(SOTA detectors) alone risks recall gaps and bbox jitter.
Decision: Three channels — (1) DOM heuristics (password/autocomplete/inputmode) with exact Playwright
bounding boxes; (2) visible-text regex+NER with element boxes; (3) BlazeFace for faces. Mask styles by
category. RedactionMap ships to server.
Alternatives: Single YOLO "PII detector" (rejected: no such labeled model; AGPL tooling), server-side
redaction (rejected: violates privacy premise), Presidio full adoption (rejected: adds deps; we borrow
its RecognizerResult shape only).
Consequences: Pixel-exact masks on DOM-sourced PII (redaction-precision story); face channel carries
documented recall risk (R-07).
Migration: add OmniParser-v3 channel in V1 for canvas-only apps (A-006 fallback).
