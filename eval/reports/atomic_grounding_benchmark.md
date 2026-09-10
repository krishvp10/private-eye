# Atomic Grounding Benchmark Report (150 Cases)

- **Total Cases:** 150
- **Target Accuracy (Top-1):** `88.7%`
- **Candidate Recall@3:** `100.0%`
- **Candidate Recall@5:** `100.0%`
- **Wrong Target Rate:** `11.3%`
- **Unknown Target Rate:** `0.0%`
- **Evaluation Latency:** `13.5 ms` (~`0.09 ms/case`)

## Performance by Category

| Category | Cases | Top-1 Accuracy | Top-3 Recall |
|---|---|---|---|
| duplicate_buttons | 20 | 55.0% | 100.0% |
| table_row_actions | 15 | 66.7% | 100.0% |
| form_field_distractors | 15 | 100.0% | 100.0% |
| icon_only_controls | 15 | 100.0% | 100.0% |
| small_controls | 15 | 100.0% | 100.0% |
| disabled_vs_enabled | 12 | 100.0% | 100.0% |
| nested_components | 14 | 85.7% | 100.0% |
| multilingual_labels | 12 | 91.7% | 100.0% |
| combobox_selectors | 12 | 100.0% | 100.0% |
| sensitive_pii_fields | 10 | 100.0% | 100.0% |
| mobile_responsive | 10 | 100.0% | 100.0% |

## Performance by Difficulty

| Difficulty | Cases | Top-1 Accuracy | Top-3 Recall |
|---|---|---|---|
| medium | 69 | 87.0% | 100.0% |
| hard | 66 | 87.9% | 100.0% |
| easy | 15 | 100.0% | 100.0% |
