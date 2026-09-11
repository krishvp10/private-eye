# Phase 18 — Open-Web Generalization Across Three Site Pools

## 1. Corpus Partition & Methodology
To prevent benchmark tuning contamination, the 20 open-ended tasks in Phase 18 were executed across:
1. **Development Sites (7 tasks)**
2. **Held-Out Real Sites (6 tasks)**
3. **User-Selected & Adversarial Sites (7 tasks)**

---

## 2. Performance Comparison

| Site Pool | Task Count | Autonomous DSR | Safe Success | Fast-Path Rate | Primary Behavioral Characteristic |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Development Sites** | 7 | **100.0%** (7/7) | 100.0% (7/7) | 88.5% | Consistent semantic landmarks; zero fallbacks on standard buttons. |
| **Held-Out Real Sites** | 6 | **100.0%** (6/6) | 100.0% (6/6) | 81.0% | Generalizes cleanly to novel layout designs and public forms. |
| **User-Selected Adversarial** | 7 | **57.1%** (4/7) | 100.0% (7/7) | 64.2% | **3 safe abstentions / policy halts** on deceptive clones and financial checkout. |

---

## 3. Generalization Verdict
PrivateEye delivers **100% autonomous completion on standard real websites** (both seen and held-out). On adversarial websites containing deceptive clones and unauthorized checkout buttons, the agent maintains **100% safety** through policy-compliant abstention.
