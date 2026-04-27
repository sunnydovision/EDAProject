# ONLYSTATS vs QUIS: Evaluation Report

**Generated**: 2026-04-27 18:46:45

---

## Executive Summary

| | ONLYSTATS | QUIS |
|---|---|---|
| **Metrics Won** | 6 | 18 |
| **Overall Winner** |  | ✓ |

---

## Group 1 — Core Metrics & Efficiency

| Metric                                     | ONLYSTATS   | QUIS       | Winner    | Description                                             |
|:-------------------------------------------|:------------|:-----------|:----------|:--------------------------------------------------------|
| 0. Total insights                          | 62          | 98         | N/A       | Total insight cards generated                           |
| 1. Faithfulness                            | 67.7%       | 90.8%      | QUIS      | Correctness - đúng dữ liệu                              |
| 2. Statistical Significance (Overall)      | 71.1%       | 71.5%      | QUIS      | Validity - pattern-averaged (fair comparison)           |
| 2a. Significance — TREND                   | 100.0% (10) | 50.0% (2)  | ONLYSTATS | Validity - TREND pattern                                |
| 2a. Significance — OUTSTANDING_VALUE       | 40.0% (25)  | 42.4% (33) | QUIS      | Validity - OUTSTANDING_VALUE pattern                    |
| 2a. Significance — ATTRIBUTION             | 100.0% (18) | 96.4% (28) | ONLYSTATS | Validity - ATTRIBUTION pattern                          |
| 2a. Significance — DISTRIBUTION_DIFFERENCE | 44.4% (9)   | 97.0% (33) | QUIS      | Validity - DISTRIBUTION_DIFFERENCE pattern              |
| 3. Insight Novelty                         | 67.7%       | 84.7%      | QUIS      | Usefulness - khác baseline                              |
| 4a. Diversity — Semantic                   | 0.451       | 0.480      | QUIS      | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy           | 2.101       | 2.176      | QUIS      | Entropy of subspace filter columns used                 |
| 4c. Diversity — Value                      | 0.822       | 0.897      | QUIS      | Unique (column, value) pairs in subspace / total        |
| 4d. Diversity — Dedup Rate                 | 0           | 0          | Tie       | Duplicate rate — lower is better                        |

---

## Group 2 — Subspace Deep-dive

| Metric                                        | ONLYSTATS         | QUIS              | Winner   | Description                                                          |
|:----------------------------------------------|:------------------|:------------------|:---------|:---------------------------------------------------------------------|
| 7. Subspace Rate                              | 45/62 (72.6%)     | 87/98 (88.8%)     | QUIS     | Insights with subspace filter / total                                |
| 7a. Subspace Faithfulness                     | 71.1%             | 94.3%             | QUIS     | Faithfulness restricted to subspace insights                         |
| 7b. Subspace Significance                     | 47.4%             | 48.3%             | QUIS     | Significance restricted to subspace insights                         |
| 7c. Subspace Novelty                          | 71.1%             | 86.2%             | QUIS     | Novelty restricted to subspace insights                              |
| 7d.1. Diversity — Semantic (Subspace)         | 0.439             | 0.463             | QUIS     | Semantic diversity restricted to subspace insights                   |
| 7d.2. Diversity — Subspace Entropy (Subspace) | 2.101             | 2.176             | QUIS     | Entropy of subspace filter columns used (subspace insights)          |
| 7d.3. Diversity — Value (Subspace)            | 0.822             | 0.897             | QUIS     | Unique (column, value) pairs in subspace / total (subspace insights) |
| 7d.4. Diversity — Dedup Rate (Subspace)       | 0                 | 0                 | Tie      | Duplicate rate restricted to subspace insights - lower is better     |
| 8. Score Uplift from Subspace                 | Δ=-0.051, x=0.885 | Δ=-0.012, x=0.966 | QUIS     | Δ = mean(score|subspace) - mean(score|no-subspace)                   |
| 9. Direction Uplift                           | down              | down              | Tie      | Direction of Δ score uplift: up/down/flat                            |

---

## Group 3 — Intent Layer Quality

> Đánh giá mô-đun *Question Generation (QuGen)* ở hai lớp: **(3.1) Target structure** — chất lượng cặp `(breakdown, measure)` mà QuGen chọn; **(3.2) Question text & reason** — chất lượng câu hỏi và lý do ở dạng ngôn ngữ tự nhiên.

### 3.1 Target structure — `(breakdown, measure)`

| Metric                          | ONLYSTATS   | QUIS   | Winner    | Description                                                                                |
|:--------------------------------|:------------|:-------|:----------|:-------------------------------------------------------------------------------------------|
| 10. Total (B,M) pairs evaluated | 32/32       | 25/25  | N/A       | Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness) |
| 10a. BM — NMI mean              | 0.112       | 0.081  | ONLYSTATS | Mean NMI over categorical-B pairs                                                          |
| 10b. BM — Interestingness       | 0.102       | 0.080  | ONLYSTATS | Mean Coverage×EffectSize over categorical-B pairs                                          |
| 10c. BM — Actionability         | 1.000       | 1.000  | Tie       | % pairs with categorical breakdown                                                         |
| 10d. BM — Diversity             | 0.516       | 0.255  | ONLYSTATS | Unique (B,M) pairs / total insights                                                        |

### 3.2 Question text & reason

| Metric                               | ONLYSTATS   | QUIS        | Winner    | Description                                                          |
|:-------------------------------------|:------------|:------------|:----------|:---------------------------------------------------------------------|
| 11a. Question Semantic Diversity     | 0.371       | 0.501       | QUIS      | 1 - mean cosine sim of question embeddings (within-system)           |
| 11b. Question Specificity            | 7.71 ± 0.63 | 9.11 ± 1.41 | QUIS      | Avg word count per question (mean ± std) — higher = more specific    |
| 11c. Question–Insight Alignment      | 0.714       | 0.575       | ONLYSTATS | Mean cosine(Embed(question), Embed(insight)) — semantic faithfulness |
| 11d. Question Novelty (cross-system) | N/A         | 86.7%       | Tie       | % of questions with cross-system max cosine sim < 0.85               |
| 11e. Reason–Insight Coherence        | N/A         | 0.557       | Tie       | Mean cosine(Embed(reason), Embed(insight)) — reason grounding        |

---

## Conclusion

**Overall Winner**: QUIS (6 vs 18 metrics won)

