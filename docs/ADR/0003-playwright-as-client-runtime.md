# ADR-0003: Playwright as the client runtime (vs MV3 extension or desktop capture)
Status: Accepted with hedge (2026-09-10)
Context: Problem asks for client-side component in Chrome/Firefox. Options: browser extension with
WebGPU models; OS screen capture; Playwright-driven browser.
Decision: Playwright-driven browser, headful. It delivers a11y trees (our grounding + PII signal),
reliable cross-browser execution (Chromium+Firefox), and is the same substrate SeeAct's official
harness uses. Extension (Transformers.js/WebGPU) becomes V1.
Alternatives: MV3 extension (rejected for MVP: WebGPU model pipeline + tabCapture redaction adds
untested risk days), OS capture + pyautogui (rejected: no DOM semantics → weaker metrics 1–3).
Consequences: Client = local Python process (justify in pitch as "local agent"; problem text allows
client-side JS/extension *components*, and browsers used are literally Chrome/Firefox).
Risks: judges may insist on literal extension → hedge: A-001 question asked early; extension shell
is scoped V1.
Migration: capture/execute modules abstract behind interfaces an MV3 extension can reimplement.
