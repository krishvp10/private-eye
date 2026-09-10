# SECURITY.md — Threat Model & Controls

## Security model
The client is trusted (user's machine); the server is honest-but-curious (we minimize what it can learn);
the network is untrusted (TLS/ssh-tunnel); the VLM is untrusted output (whitelisted actions only);
web content is untrusted input (both to client parsers and, via screenshots, to the VLM).

## Threat model

| Threat | Likelihood | Impact | Mitigation | Residual |
|---|---|---|---|---|
| PII leaks in outbound image (redaction miss) | Medium | Critical | 3-channel detection + defense-in-depth re-scan of encoded bytes (`eval/leak_check.py` blocks send) + over-mask bias | Low-Med |
| Secret value reaches server via fill command | Low | Critical | Protocol has no `value` field; static check bans the key; runtime outbound interceptor scans for vault values | Low |
| Prompt injection via page content → harmful action | Medium | High | LLM01 controls: action enum whitelist, target must exist in screen_graph, destructive actions need user confirm, server never returns raw JS | Low |
| Malicious page probes local agent (drive-by) | Low | Medium | Agent only visits user-initiated URLs; demo sites are ours; `confirm` gates | Low |
| Rogue server impersonation / MITM | Low | High | TLS or ssh tunnel at demo; shared-secret header in prod profile; cert pinning optional | Low |
| Server logs retain PII | Medium | High | Logging decorator scans payloads; CI greps logs vs corpus patterns; DB schema has no free-text PII fields | Low |
| Malicious npm/pip dependency | Medium | High | Pinned lockfiles; pip-audit + npm audit in CI; vendor the 3 demo sites with no third-party JS | Low |
| VLM jailbreak exfiltrates RedactionMap patterns | Low | Medium | RedactionMap is *meant* to be known (it's the contract); it reveals categories+regions, not values — acceptable by design | Accepted |
| Face-detection model adversarial evasion | Low | Medium | Over-mask bias; user-visible redaction feed; documented limitation (RISKS R-07) | Accepted |

## OWASP mapping
- **LLM01 Prompt Injection**: action whitelist + screen_graph target validation + user confirmation (above).
- **LLM02 Sensitive Info Disclosure**: the entire architecture; NFR-001/002 tests.
- **A03 Injection (web)**: demo sites are static/self-built; client never evaluates page JS beyond Playwright actions.
- **A05 Misconfiguration**: strict pydantic schemas; no debug endpoints in prod profile.
- **A06 Vulnerable components**: pip-audit CI gate.
- **A09 Logging failures**: PII-free logging decorator + leak grep.

## Crypto & secrets
- Vault: values from env vars / local encrypted file (Fernet key in OS keychain; falls back to file-permission 600 at demo).
- In transit: TLS via Caddy (prod) or `ssh -L` (demo).
- At rest: vault file only; no server-side secrets beyond the shared API key.

## Privacy commitments (DPDP-aware)
Collect nothing raw; RedactionMap carries categories, not values; user can inspect the exact outbound
bytes from the dashboard; deletion = delete run log rows.
