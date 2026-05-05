# ONLYSTATS vs QUIS: Evaluation Report

**Generated**: 2026-05-05 20:28:35

---

## Executive Summary

| | ONLYSTATS | QUIS |
|---|---|---|
| **Metrics Won** | 8 | 14 |
| **Overall Winner** |  | ✓ |

---

## Group 1 — Core Metrics & Efficiency

| Metric                                     | ONLYSTATS   | QUIS       | Winner    | Description                                             |
|:-------------------------------------------|:------------|:-----------|:----------|:--------------------------------------------------------|
| 0. Total insights                          | 132         | 133        | N/A       | Total insight cards generated                           |
| 1. Faithfulness                            | 100.0%      | 100.0%     | Tie       | Correctness - đúng dữ liệu                              |
| 2. Statistical Significance (Overall)      | 20.2%       | 20.0%      | ONLYSTATS | Validity - pattern-averaged (fair comparison)           |
| 2a. Significance — TREND                   | N/A         | N/A        | N/A       | Validity - TREND pattern                                |
| 2a. Significance — OUTSTANDING_VALUE       | 0.0% (19)   | 22.2% (27) | QUIS      | Validity - OUTSTANDING_VALUE pattern                    |
| 2a. Significance — ATTRIBUTION             | 47.3% (55)  | 36.7% (49) | ONLYSTATS | Validity - ATTRIBUTION pattern                          |
| 2a. Significance — DISTRIBUTION_DIFFERENCE | 33.3% (9)   | 20.9% (43) | ONLYSTATS | Validity - DISTRIBUTION_DIFFERENCE pattern              |
| 3. Insight Novelty                         | 81.8%       | 90.2%      | QUIS      | Usefulness - khác baseline                              |
| 4a. Diversity — Semantic                   | 0.432       | 0.499      | QUIS      | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy           | 2.948       | 2.938      | ONLYSTATS | Entropy of subspace filter columns used                 |
| 4c. Diversity — Value                      | 0.756       | 0.767      | QUIS      | Unique (column, value) pairs in subspace / total        |
| 4d. Diversity — Dedup Rate                 | 0           | 0          | Tie       | Duplicate rate — lower is better                        |

---

## Group 2 — Subspace Deep-dive

| Metric                                        | ONLYSTATS         | QUIS             | Winner    | Description                                                                                 |
|:----------------------------------------------|:------------------|:-----------------|:----------|:--------------------------------------------------------------------------------------------|
| 7. Subspace Rate                              | 78/132 (59.1%)    | 116/133 (87.2%)  | QUIS      | Insights with subspace filter / total                                                       |
| 7a. Subspace Faithfulness                     | 100.0%            | 100.0%           | Tie       | Faithfulness restricted to subspace insights                                                |
| 7b. Subspace Significance                     | 0.0%              | 24.0%            | QUIS      | Significance restricted to subspace insights                                                |
| 7c. Subspace Novelty                          | 91.0%             | 95.7%            | QUIS      | Novelty restricted to subspace insights                                                     |
| 7d.1. Diversity — Semantic (Subspace)         | 0.396             | 0.478            | QUIS      | Semantic diversity restricted to subspace insights                                          |
| 7d.2. Diversity — Subspace Entropy (Subspace) | 2.948             | 2.938            | ONLYSTATS | Entropy of subspace filter columns used (subspace insights)                                 |
| 7d.3. Diversity — Value (Subspace)            | 0.756             | 0.767            | QUIS      | Unique (column, value) pairs in subspace / total (subspace insights)                        |
| 7d.4. Diversity — Dedup Rate (Subspace)       | 0                 | 0                | Tie       | Duplicate rate restricted to subspace insights - lower is better                            |
| 8. Score Uplift from Subspace                 | Δ=-0.188, x=0.346 | Δ=0.083, x=1.574 | QUIS      | Δ = mean(score|subspace) - mean(score|no-subspace)                                          |
| 9. Simpson's Paradox Rate (SPR)               | 7.7% (0/6 sig)    | 26.7% (7/31 sig) | QUIS      | Rate of statistically significant pattern reversals (p<0.05) — true Simpson's Paradox cases |

---

## Group 3 — Intent Layer Quality

> Đánh giá mô-đun *Question Generation (QuGen)* ở hai lớp: **(3.1) Target structure** — chất lượng cặp `(breakdown, measure)` mà QuGen chọn; **(3.2) Question text & reason** — chất lượng câu hỏi và lý do ở dạng ngôn ngữ tự nhiên.

### 3.1 Target structure — `(breakdown, measure)`

| Metric                          | ONLYSTATS   | QUIS   | Winner    | Description                                                                                |
|:--------------------------------|:------------|:-------|:----------|:-------------------------------------------------------------------------------------------|
| 10. Total (B,M) pairs evaluated | 53/53       | 49/51  | N/A       | Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness) |
| 10a. BM — NMI mean              | nan         | 0.035  | Tie       | Mean NMI over categorical-B pairs                                                          |
| 10b. BM — Interestingness       | 0.102       | 0.090  | ONLYSTATS | Mean Coverage×EffectSize over categorical-B pairs                                          |
| 10c. BM — Actionability         | 1.000       | 0.961  | ONLYSTATS | % pairs with categorical breakdown                                                         |
| 10d. BM — Diversity             | 0.402       | 0.384  | ONLYSTATS | Unique (B,M) pairs / total insights                                                        |

### 3.2 Question text & reason

| Metric                               | ONLYSTATS   | QUIS         | Winner   | Description                                                          |
|:-------------------------------------|:------------|:-------------|:---------|:---------------------------------------------------------------------|
| 11a. Question Semantic Diversity     | 0           | 0.597        | QUIS     | 1 - mean cosine sim of question embeddings (within-system)           |
| 11b. Question Specificity            | 0.00 ± 0.00 | 10.25 ± 2.51 | QUIS     | Avg word count per question (mean ± std) — higher = more specific    |
| 11c. Question–Insight Alignment      | 0           | 0.493        | QUIS     | Mean cosine(Embed(question), Embed(insight)) — semantic faithfulness |
| 11d. Question Novelty (cross-system) | N/A         | 100.0%       | Tie      | % of questions with cross-system max cosine sim < 0.85               |
| 11e. Reason–Insight Coherence        | N/A         | 0.468        | Tie      | Mean cosine(Embed(reason), Embed(insight)) — reason grounding        |

---

## Conclusion

**Overall Winner**: QUIS (8 vs 14 metrics won)

