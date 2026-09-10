# PRIVATEEYE EXTERNAL DIAGNOSTIC SUBSET — OSWORLD

> **METHODOLOGICAL COMPLIANCE & DISCLOSURE NOTICE:**
> This report evaluates PrivateEye against an **adapted diagnostic subset of 20 tasks**
> drawn from the **OSWorld Web benchmark taxonomy** (browser settings, webmail, ecommerce, issue trackers, data tables).
> It is **NOT** an official OSWorld leaderboard submission.
> Official OSWorld evaluation runs against a 369-task full OS desktop virtual machine with system-level filesystem evaluators.
> PrivateEye evaluates browser-level execution post-conditions and deterministic accessibility candidate grounding.

## 1. Benchmark Diagnostic Results

- **Evaluated Tasks:** **20**
- **Target Grounding Accuracy:** **20/20 (100.0%)**
- **Post-Condition Success Rate:** **20/20 (100.0%)**
- **Local Candidate Grounding Latency (p50):** `0.200 ms`
- **Local Candidate Grounding Latency (p95):** `0.260 ms`

## 2. Protocol & Environment Disclosures

| Factor | OSWorld Official Protocol | PrivateEye Adapted Diagnostic |
|---|---|---|
| **Environment** | Full Ubuntu OS Docker Container (XFCE Desktop) | Local Playwright Chromium browser sandbox |
| **Observation** | Full desktop screenshot & OS accessibility bus | Sanitized local ScreenGraph + 768px redacted screenshot |
| **Candidates** | Open-loop pixel coordinate prediction $(x, y)$ | Top-k local ARIA candidates with selective crop verification |
| **Evaluator** | OS bash script inspection & SQLite database diffs | Action post-condition evaluation (DOM transition verification) |
| **Privacy Layer** | None (agent has full OS access) | Fail-closed privacy gate, local redaction, vault `value_ref` fills |

## 3. Diagnostic Task Evaluation Matrix

| ID | Domain Category | Task Prompt | Target Control | Role | Post-Condition | Status |
|---|---|---|---|---|---|---|
| `osworld_web_01` | `browser_settings` | Clear browsing history for the last 24 hours in Chrome settings | `Clear browsing data` | `button` | **PASS** | **PASS** |
| `osworld_web_02` | `browser_settings` | Toggle dark mode theme in browser preferences | `Theme toggle switch` | `switch` | **PASS** | **PASS** |
| `osworld_web_03` | `browser_settings` | Manage search engine default to DuckDuckGo | `Default search engine dropdown` | `combobox` | **PASS** | **PASS** |
| `osworld_web_04` | `browser_settings` | Disable third-party cookies in privacy section | `Block third-party cookies radio` | `radio` | **PASS** | **PASS** |
| `osworld_web_05` | `web_mail` | Compose new email message in webmail client | `Compose` | `button` | **PASS** | **PASS** |
| `osworld_web_06` | `web_mail` | Search for emails from 'billing@service.com' | `Search mail input` | `searchbox` | **PASS** | **PASS** |
| `osworld_web_07` | `web_mail` | Mark selected message as unread | `Mark unread` | `button` | **PASS** | **PASS** |
| `osworld_web_08` | `ecommerce` | Filter product catalog by price under $50 | `Price < $50 checkbox` | `checkbox` | **PASS** | **PASS** |
| `osworld_web_09` | `ecommerce` | Add second item in grid to shopping cart | `Add to Cart (Item 2)` | `button` | **PASS** | **PASS** |
| `osworld_web_10` | `ecommerce` | Enter promo code 'DISCOUNT20' in checkout summary | `Promo code textfield` | `textbox` | **PASS** | **PASS** |
| `osworld_web_11` | `issue_tracker` | Filter issues by label 'bug' in repository tracker | `Label: bug filter` | `button` | **PASS** | **PASS** |
| `osworld_web_12` | `issue_tracker` | Assign issue #104 to user 'alice' | `Assignee dropdown` | `combobox` | **PASS** | **PASS** |
| `osworld_web_13` | `issue_tracker` | Close issue with reason 'completed' | `Close issue button` | `button` | **PASS** | **PASS** |
| `osworld_web_14` | `data_table` | Sort customer table by column 'Registration Date' descending | `Sort Registration Date header` | `columnheader` | **PASS** | **PASS** |
| `osworld_web_15` | `data_table` | Export visible rows to CSV format | `Export CSV button` | `button` | **PASS** | **PASS** |
| `osworld_web_16` | `data_table` | Paginate table to page 3 | `Page 3 pagination link` | `link` | **PASS** | **PASS** |
| `osworld_web_17` | `wiki` | Edit document heading in markdown editor | `Edit page button` | `button` | **PASS** | **PASS** |
| `osworld_web_18` | `wiki` | Search wiki knowledge base for 'OAuth2 config' | `Wiki search input` | `searchbox` | **PASS** | **PASS** |
| `osworld_web_19` | `form_wizard` | Advance from Step 2 (Address) to Step 3 (Review) | `Continue to Review` | `button` | **PASS** | **PASS** |
| `osworld_web_20` | `form_wizard` | Submit completed multi-page registration form | `Submit Registration` | `button` | **PASS** | **PASS** |

## 4. Conclusion
Within the tested 20-task browser diagnostic subset, PrivateEye's candidate-constrained grounding engine successfully localized and executed 100% of targets without coordinate drifting or invalid click events. The adaptation differences are explicitly disclosed above.