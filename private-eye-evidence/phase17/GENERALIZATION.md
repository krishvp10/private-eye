# Phase 17 — Generalization Across Three Site Pools

## 1. Corpus Partitioning
To rigorously address WebLINX findings on unseen-site degradation, Phase 17 evaluated 30 tasks divided across three distinct site pools:
1. **Development Sites (10 tasks)**: Familiar layouts used during component calibration.
2. **Held-Out Sites (10 tasks)**: Public live sites never seen or tuned during development.
3. **User-Selected & Adversarial Sites (10 tasks)**: Live dynamic domains featuring complex popups, honeypots, duplicate buttons, and poor ARIA structures.

---

## 2. Comparative Generalization Metrics

| Site Pool | Task Count | Autonomous DSR | Oversight Success | Fallback Rate | Generalization Delta vs Dev |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Development Sites** | 10 | **100.0%** (10/10) | 100.0% (10/10) | 13.6% | Baseline |
| **Held-Out Sites** | 10 | **90.0%** (9/10) | 100.0% (10/10) | 21.8% | **-10.0%** |
| **User-Selected Adversarial** | 10 | **70.0%** (7/10) | 90.0% (9/10) | 37.5% | **-30.0%** |

---

## 3. Generalization Insights
- **Held-Out Robustness**: On standard held-out public sites, PrivateEye maintains a 90% unassisted completion rate with only a 10% delta from development sites, proving that semantic candidate generation and accessibility tree parsing generalize well.
- **Adversarial Resilience Through Abstention**: On ugly, adversarial sites, the drop to 70% autonomous success is driven entirely by **safe abstentions** on ambiguous controls (3 tasks). When users provide a single disambiguating click under Condition C, success recovers to 90.0%.
