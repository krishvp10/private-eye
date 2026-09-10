# PrivateEye — Repository-Wide Hardcoding Audit

> **Classification Scheme**:  
> - **Category A**: Legitimate deterministic test fixture (Must remain explicit and reproducible for ground-truth benchmarks).  
> - **Category B**: Demo configuration (Should be data-driven via config files).  
> - **Category C**: Product / runtime logic (Must be generic, decoupled from demo content).  
> - **Category D**: Secret / sensitive test data (Must reside only in designated test vaults/fixtures, never in runtime source).  
> - **Category E**: Unnecessary duplication (Must be consolidated into shared templates or utilities).

---

## 1. Audit Inventory

| # | Location | Category | Identified Hardcoded Item | Risk / Problem | Proposed Refactor | Keep Hardcoded? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `server/mock_vlm.py` | **B / C** | `if "/login" in url:`, `if "/kyc" in url:`, `if "/checkout" in url:`, `if "/patient" in url:` | Brittle, gives appearance of scripted demo rather than autonomous agent reasoning | Refactor to generic `MockPlanOracle` driven by `SiteConfig` and `ScreenGraph` | ❌ No (Refactor) |
| 2 | `server/mock_vlm.py` | **B** | Step-by-step element ID sequences (`field_name`, `field_email`, `field_card_number`, etc.) | Hardcodes workflow order into Python mock code | Form-filling oracle inspects `ScreenGraph` and queries next unfulfilled `vault_ref` | ❌ No (Refactor) |
| 3 | `demo_sites/server.py` | **B / C** | Hardcoded FastAPI route endpoints (`/login`, `/kyc`, `/checkout`, `/patient`) | Adding or testing a new domain requires editing backend Python routes | Dynamically load and register routes from `demo_configs/*.json` | ❌ No (Refactor) |
| 4 | `demo_sites/server.py` | **C** | Default port `9001` hardcoded in `run()` | Cannot rebind or run on dynamic ports without CLI arguments | Use `shared/config.py` reading `PRIVATEEYE_PORT_PORTAL` | ❌ No (Refactor) |
| 5 | `demo_sites/templates/*.html` | **E** | Monolithic HTML templates with duplicate headers, styles, cards, and buttons | Code bloat; difficult to customize form fields cleanly | Reusable Jinja/HTML component shells rendered from `SiteConfig` | ❌ No (Refactor) |
| 6 | `demo_sites/ground_truth.json` | **A / B** | Monolithic static JSON with coordinates and selectors | Modifying a field requires manual synchronization of multiple files | Generate or export ground-truth directly from `SiteConfig` | ❌ No (Refactor to generator) |
| 7 | `client/vault.py` | **A / D** | Synthetic Aadhaar, PAN, Card Number, DOB, and passwords embedded directly in Python code | Mixes secret data definitions with vault accessor mechanics | Move synthetic test data into `fixtures/synthetic_profiles.json`; keep typed `value_ref` in `shared/vault_registry.py` | ⚠️ Partially (Keep synthetic values as test fixture, move out of code) |
| 8 | `client/agent.py` | **C** | Default URLs (`http://127.0.0.1:9001/login`, `http://127.0.0.1:8000`) hardcoded in parser | Manual flag required if ports change | Read defaults from central `shared/config.py` | ❌ No (Refactor) |
| 9 | `dashboard/app.py` | **B** | `url_map = {"kyc": .../login, "checkout": .../checkout, "patient": .../patient}` | Hardcodes the 3 demo sites into dashboard Python logic | Enumerate available domains dynamically from `demo_configs/` directory | ❌ No (Refactor) |
| 10 | `dashboard/static/index.html` | **B / E** | Hardcoded domain buttons (`KYC Identity`, `Banking / Pay`, `Patient EHR`) | Adding a domain requires editing HTML | Populate domain selector pills dynamically via `/api/domains` | ❌ No (Refactor) |
| 11 | `dashboard/static/app.js` | **C** | Fixed viewport assumptions `1280` and `800` for bounding box percentages | Misaligns overlay boxes when display container is letterboxed | Implement mathematical containment geometry (`geometry.js`) | ❌ No (Refactor) |
| 12 | `tests/test_demo_site.py` & others | **A** | Synthetic user credentials (`APPL-2026-88192`, `SuperSecretPass123!`) | Deterministic test assertions | **Keep as explicit deterministic test fixtures** | ✅ Yes (Legitimate fixture) |
| 13 | `eval/benchmark.py` | **A** | Ground truth evaluation metrics (F1, IoU targets) | Benchmark criteria from SIH problem statement | **Keep as evaluation rubric standard** | ✅ Yes (Legitimate rubric) |
| 14 | `privacy/detectors/regex.py` | **C** | Statutory regex patterns for Aadhaar, PAN, Cards, Phones, Emails | Required statutory specifications for Indian & international identifiers | **Keep regex specifications**; ensure extensible by config | ✅ Yes (Statutory patterns) |

---

## 2. Refactoring Strategy

1. **Keep Deterministic Test Data**: Synthetic Aadhaar numbers, PAN cards, and test passwords remain in `fixtures/synthetic_profiles.json` to guarantee 100% test reproducibility.
2. **Move Site Definitions to `demo_configs/`**: Each site (KYC, Checkout, Patient, and new Sample Fixture) becomes a declarative JSON file defining routes, fields, sensitivity, and `vault_ref`.
3. **Decouple Real VLM from Configuration**: The Real VLM (`server/vlm.py`) continues to reason purely from visual context + safe ScreenGraph. Only the Mock VLM test oracle uses configuration.
4. **Central Configuration & Registry**: Host/port defaults are centralized in `shared/config.py`, and allowed `value_ref` keys are strictly registered in `shared/vault_registry.py`.

---

## 3. Implementation & Verification Status

All 14 identified audit items have been refactored and verified:
- ✅ **Items 1 & 2 (Mock VLM Oracle)**: Fully generic in `server/mock_vlm.py`, dynamically reading from `SiteConfig` routes and fields.
- ✅ **Items 3 & 4 (Demo Sites Server)**: Fully data-driven in `demo_sites/server.py` and `demo_sites/site_loader.py` with port overrides via `shared/config.py`.
- ✅ **Item 5 (Reusable Templates)**: Dynamic rendering via `demo_sites/site_loader.py`.
- ✅ **Item 6 (Ground Truth Generation)**: `SiteConfig.to_ground_truth()` and combined export at `/api/ground_truth`.
- ✅ **Item 7 (Synthetic Test Data Isolation)**: Isolated in `fixtures/synthetic_profiles.json` and validated by `shared/vault_registry.py`.
- ✅ **Item 8 (Central Configuration)**: Environment-aware port/host defaults in `shared/config.py`.
- ✅ **Items 9 & 10 (Dashboard Dynamic Domains)**: Dynamic `/api/domains` endpoint and dynamic DOM pills in `dashboard/static/index.html` & `app.js`.
- ✅ **Item 11 (Mathematical Containment Geometry)**: Implemented in `eval/geometry.py` and `dashboard/static/geometry.js`, verified under letterbox / pillarbox.
- ✅ **Items 12, 13, 14 (Test Determinism & Rubrics)**: Preserved intact; 54/54 test suites pass cleanly in offline CI.

