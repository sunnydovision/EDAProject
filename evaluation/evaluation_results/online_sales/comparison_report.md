# ONLYSTATS vs QUIS: Evaluation Report

**Generated**: 2026-05-06 22:55:31

---

## Executive Summary

| | ONLYSTATS | QUIS |
|---|---|---|
| **Metrics Won** | 14 | 10 |
| **Overall Winner** | ✓ |  |

---

## Group 1 — Core Metrics & Efficiency

| Metric                                     | ONLYSTATS   | QUIS       | Winner    | Description                                             |
|:-------------------------------------------|:------------|:-----------|:----------|:--------------------------------------------------------|
| 0. Total insights                          | 72          | 106        | N/A       | Total insight cards generated                           |
| 1. Faithfulness                            | 100.0%      | 100.0%     | Tie       | Correctness - đúng dữ liệu                              |
| 2. Statistical Significance (Overall)      | 58.6%       | 35.9%      | ONLYSTATS | Validity - pattern-averaged (fair comparison)           |
| 2a. Significance — TREND                   | 66.7% (3)   | N/A        | ONLYSTATS | Validity - TREND pattern                                |
| 2a. Significance — OUTSTANDING_VALUE       | 52.0% (25)  | 34.4% (32) | ONLYSTATS | Validity - OUTSTANDING_VALUE pattern                    |
| 2a. Significance — ATTRIBUTION             | 60.0% (20)  | 53.3% (30) | ONLYSTATS | Validity - ATTRIBUTION pattern                          |
| 2a. Significance — DISTRIBUTION_DIFFERENCE | 55.6% (18)  | 56.0% (25) | QUIS      | Validity - DISTRIBUTION_DIFFERENCE pattern              |
| 3. Insight Novelty                         | 30.6%       | 47.2%      | QUIS      | Usefulness - khác baseline                              |
| 4a. Diversity — Semantic                   | 0.433       | 0.489      | QUIS      | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy           | 1.659       | 1.596      | ONLYSTATS | Entropy of subspace filter columns used                 |
| 4c. Diversity — Value                      | 0.463       | 0.440      | ONLYSTATS | Unique (column, value) pairs in subspace / total        |
| 4d. Diversity — Dedup Rate                 | 0           | 0          | Tie       | Duplicate rate — lower is better                        |

---

## Group 2 — Subspace Deep-dive

| Metric                                        | ONLYSTATS         | QUIS              | Winner    | Description                                                                                 |
|:----------------------------------------------|:------------------|:------------------|:----------|:--------------------------------------------------------------------------------------------|
| 7. Subspace Rate                              | 67/72 (93.1%)     | 84/106 (79.2%)    | ONLYSTATS | Insights with subspace filter / total                                                       |
| 7a. Subspace Faithfulness                     | 100.0%            | 100.0%            | Tie       | Faithfulness restricted to subspace insights                                                |
| 7b. Subspace Significance                     | 45.0%             | 44.4%             | ONLYSTATS | Significance restricted to subspace insights                                                |
| 7c. Subspace Novelty                          | 37.3%             | 41.7%             | QUIS      | Novelty restricted to subspace insights                                                     |
| 7d.1. Diversity — Semantic (Subspace)         | 0.430             | 0.464             | QUIS      | Semantic diversity restricted to subspace insights                                          |
| 7d.2. Diversity — Subspace Entropy (Subspace) | 1.659             | 1.596             | ONLYSTATS | Entropy of subspace filter columns used (subspace insights)                                 |
| 7d.3. Diversity — Value (Subspace)            | 0.463             | 0.440             | ONLYSTATS | Unique (column, value) pairs in subspace / total (subspace insights)                        |
| 7d.4. Diversity — Dedup Rate (Subspace)       | 0                 | 0                 | Tie       | Duplicate rate restricted to subspace insights - lower is better                            |
| 8. Score Uplift from Subspace                 | Δ=-0.386, x=0.511 | Δ=-0.137, x=0.742 | QUIS      | Δ = mean(score|subspace) - mean(score|no-subspace)                                          |
| 9. Simpson's Paradox Rate (SPR)               | 31.3% (1/21 sig)  | 32.1% (1/27 sig)  | QUIS      | Rate of statistically significant pattern reversals (p<0.05) — true Simpson's Paradox cases |

---

## Group 3 — Intent Layer Quality

> Đánh giá mô-đun *Question Generation (QuGen)* ở hai lớp: **(3.1) Target structure** — chất lượng cặp `(breakdown, measure)` mà QuGen chọn; **(3.2) Question text & reason** — chất lượng câu hỏi và lý do ở dạng ngôn ngữ tự nhiên.

### 3.1 Target structure — `(breakdown, measure)`

| Metric                          | ONLYSTATS   | QUIS   | Winner    | Description                                                                                |
|:--------------------------------|:------------|:-------|:----------|:-------------------------------------------------------------------------------------------|
| 10. Total (B,M) pairs evaluated | 24/24       | 24/26  | N/A       | Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness) |
| 10a. BM — NMI mean              | 0.228       | 0.179  | ONLYSTATS | Mean NMI over categorical-B pairs                                                          |
| 10b. BM — Interestingness       | 0.314       | 0.244  | ONLYSTATS | Mean Coverage×EffectSize over categorical-B pairs                                          |
| 10c. BM — Actionability         | 1.000       | 0.923  | ONLYSTATS | % pairs with categorical breakdown                                                         |
| 10d. BM — Diversity             | 0.333       | 0.245  | ONLYSTATS | Unique (B,M) pairs / total insights                                                        |

### 3.2 Question text & reason

| Metric                               | ONLYSTATS   | QUIS        | Winner   | Description                                                          |
|:-------------------------------------|:------------|:------------|:---------|:---------------------------------------------------------------------|
| 11a. Question Semantic Diversity     | 0           | 0.518       | QUIS     | 1 - mean cosine sim of question embeddings (within-system)           |
| 11b. Question Specificity            | 0.00 ± 0.00 | 9.99 ± 2.21 | QUIS     | Avg word count per question (mean ± std) — higher = more specific    |
| 11c. Question–Insight Alignment      | 0           | 0.543       | QUIS     | Mean cosine(Embed(question), Embed(insight)) — semantic faithfulness |
| 11d. Question Novelty (cross-system) | N/A         | 95.3%       | Tie      | % of questions with cross-system max cosine sim < 0.85               |
| 11e. Reason–Insight Coherence        | N/A         | 0.557       | Tie      | Mean cosine(Embed(reason), Embed(insight)) — reason grounding        |

---

## Conclusion

**Overall Winner**: ONLYSTATS (14 vs 10 metrics won)

