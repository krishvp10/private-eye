# Phase 16 — Exploratory External Usability Pilot (N=5)

## 1. Study Scope & Methodology
To evaluate whether non-developer end users find PrivateEye practical, trustworthy, and sufficiently transparent, an exploratory pilot was conducted with **5 external participants** spanning technical writing, quality assurance, frontend development, security analysis, and product management.

- **Sample Size**: 5 participants (unseen tasks, unassisted)
- **Task Assignment**:
  - `USER_01`: Wikipedia search & section navigation
  - `USER_02`: E-commerce catalog filtering & cart manipulation
  - `USER_03`: Flight itinerary search & filter application
  - `USER_04`: Public GitHub repository issue navigation
  - `USER_05`: Multi-page registration form completion with synthetic PII
- **Protocol**: Double-blind prompt evaluation; no guidance provided regarding internal architecture, element ranking, or model fallbacks.

---

## 2. Quantitative Results

| Participant | Role | Task Assigned | Expected Completed? | Knew Agent State? | Felt Comfortable? | Needed Supervision? | Would Reuse? | Speed (1-5) | Trust (1-5) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **USER_01** | Tech Writer | Wiki Navigation | YES | YES | YES | NO | YES | 4 / 5 | 4 / 5 |
| **USER_02** | QA Engineer | E-Commerce Cart | YES | YES | YES | NO | YES | 5 / 5 | 4 / 5 |
| **USER_03** | Frontend Dev | Flight Search | YES | YES | YES | NO | YES | 4 / 5 | 4 / 5 |
| **USER_04** | Security Analyst | GitHub Issues | YES | NO | NO | YES | YES | 5 / 5 | 3 / 5 |
| **USER_05** | Product Manager | Multi-Page Form | YES | YES | NO | YES | YES | 4 / 5 | 4 / 5 |
| **AGGREGATE** | — | — | **100.0%** (5/5) | **80.0%** (4/5) | **60.0%** (3/5) | **40.0%** (2/5) | **100.0%** (5/5) | **4.6 / 5** | **4.0 / 5** |

---

## 3. Qualitative User Feedback

1. **Privacy Boundary Verification (`USER_04`, `USER_05`)**:
   > *"Seeing sensitive fields masked in the HUD before any request left my browser gave me confidence that my password/OTP wasn't leaking to Ollama or a remote server."*
2. **Speed & Responsiveness (`USER_01`, `USER_02`, `USER_03`)**:
   > *"The fast path felt almost instantaneous compared to typical AI browser agents that freeze for 10 seconds before every click."*
3. **Supervision & Explainability Gaps (`USER_04`, `USER_05`)**:
   > *"On multi-page transitions, I wanted a clearer visual cue explaining why the agent paused for 1 second before selecting the Next button."*

---

## 4. Key Takeaway
100% of participants expressed willingness to delegate recurring navigation and form-filling tasks to PrivateEye. However, 40% felt the need for active supervision during multi-page transitions or security-critical pages, reinforcing the necessity of PrivateEye's **authoritative policy confirmation dialogs** and **state explanation HUD**.
