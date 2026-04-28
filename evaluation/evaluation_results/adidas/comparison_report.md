# ONLYSTATS vs QUIS: Evaluation Report

**Generated**: 2026-04-28 18:53:13

---

## Executive Summary

| | ONLYSTATS | QUIS |
|---|---|---|
| **Metrics Won** | 5 | 16 |
| **Overall Winner** |  | ✓ |

---

## Group 1 — Core Metrics & Efficiency

| Metric                                     | ONLYSTATS   | QUIS       | Winner    | Description                                             |
|:-------------------------------------------|:------------|:-----------|:----------|:--------------------------------------------------------|
| 0. Total insights                          | 85          | 99         | N/A       | Total insight cards generated                           |
| 1. Faithfulness                            | 100.0%      | 100.0%     | Tie       | Correctness - đúng dữ liệu                              |
| 2. Statistical Significance (Overall)      | 76.2%       | 83.4%      | QUIS      | Validity - pattern-averaged (fair comparison)           |
| 2a. Significance — TREND                   | 100.0% (10) | 100.0% (2) | N/A       | Validity - TREND pattern                                |
| 2a. Significance — OUTSTANDING_VALUE       | 41.7% (24)  | 40.0% (30) | ONLYSTATS | Validity - OUTSTANDING_VALUE pattern                    |
| 2a. Significance — ATTRIBUTION             | 100.0% (24) | 96.0% (25) | ONLYSTATS | Validity - ATTRIBUTION pattern                          |
| 2a. Significance — DISTRIBUTION_DIFFERENCE | 63.0% (27)  | 97.4% (39) | QUIS      | Validity - DISTRIBUTION_DIFFERENCE pattern              |
| 3. Insight Novelty                         | 72.9%       | 79.8%      | QUIS      | Usefulness - khác baseline                              |
| 4a. Diversity — Semantic                   | 0.439       | 0.479      | QUIS      | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy           | 2.027       | 2.259      | QUIS      | Entropy of subspace filter columns used                 |
| 4c. Diversity — Value                      | 0.866       | 0.872      | QUIS      | Unique (column, value) pairs in subspace / total        |
| 4d. Diversity — Dedup Rate                 | 0           | 0          | Tie       | Duplicate rate — lower is better                        |

---

## Group 2 — Subspace Deep-dive

| Metric                                        | ONLYSTATS         | QUIS              | Winner    | Description                                                          |
|:----------------------------------------------|:------------------|:------------------|:----------|:---------------------------------------------------------------------|
| 7. Subspace Rate                              | 67/85 (78.8%)     | 86/99 (86.9%)     | QUIS      | Insights with subspace filter / total                                |
| 7a. Subspace Faithfulness                     | 100.0%            | 100.0%            | Tie       | Faithfulness restricted to subspace insights                         |
| 7b. Subspace Significance                     | 50.0%             | 44.0%             | ONLYSTATS | Significance restricted to subspace insights                         |
| 7c. Subspace Novelty                          | 76.1%             | 81.4%             | QUIS      | Novelty restricted to subspace insights                              |
| 7d.1. Diversity — Semantic (Subspace)         | 0.424             | 0.459             | QUIS      | Semantic diversity restricted to subspace insights                   |
| 7d.2. Diversity — Subspace Entropy (Subspace) | 2.027             | 2.259             | QUIS      | Entropy of subspace filter columns used (subspace insights)          |
| 7d.3. Diversity — Value (Subspace)            | 0.866             | 0.872             | QUIS      | Unique (column, value) pairs in subspace / total (subspace insights) |
| 7d.4. Diversity — Dedup Rate (Subspace)       | 0                 | 0                 | Tie       | Duplicate rate restricted to subspace insights - lower is better     |
| 8. Score Uplift from Subspace                 | Δ=-0.126, x=0.726 | Δ=-0.043, x=0.885 | QUIS      | Δ = mean(score|subspace) - mean(score|no-subspace)                   |
| 9. Direction Uplift                           | down              | down              | Tie       | Direction of Δ score uplift: up/down/flat                            |

---

## Group 3 — Intent Layer Quality

> Đánh giá mô-đun *Question Generation (QuGen)* ở hai lớp: **(3.1) Target structure** — chất lượng cặp `(breakdown, measure)` mà QuGen chọn; **(3.2) Question text & reason** — chất lượng câu hỏi và lý do ở dạng ngôn ngữ tự nhiên.

### 3.1 Target structure — `(breakdown, measure)`

| Metric                          | ONLYSTATS   | QUIS   | Winner    | Description                                                                                |
|:--------------------------------|:------------|:-------|:----------|:-------------------------------------------------------------------------------------------|
| 10. Total (B,M) pairs evaluated | 31/31       | 26/26  | N/A       | Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness) |
| 10a. BM — NMI mean              | 0.217       | 0.094  | ONLYSTATS | Mean NMI over categorical-B pairs                                                          |
| 10b. BM — Interestingness       | 0.068       | 0.077  | QUIS      | Mean Coverage×EffectSize over categorical-B pairs                                          |
| 10c. BM — Actionability         | 1.000       | 1.000  | Tie       | % pairs with categorical breakdown                                                         |
| 10d. BM — Diversity             | 0.365       | 0.263  | ONLYSTATS | Unique (B,M) pairs / total insights                                                        |

### 3.2 Question text & reason

| Metric                               | ONLYSTATS   | QUIS        | Winner   | Description                                                          |
|:-------------------------------------|:------------|:------------|:---------|:---------------------------------------------------------------------|
| 11a. Question Semantic Diversity     | 0           | 0.493       | QUIS     | 1 - mean cosine sim of question embeddings (within-system)           |
| 11b. Question Specificity            | 0.00 ± 0.00 | 9.15 ± 1.40 | QUIS     | Avg word count per question (mean ± std) — higher = more specific    |
| 11c. Question–Insight Alignment      | 0           | 0.583       | QUIS     | Mean cosine(Embed(question), Embed(insight)) — semantic faithfulness |
| 11d. Question Novelty (cross-system) | N/A         | 84.8%       | Tie      | % of questions with cross-system max cosine sim < 0.85               |
| 11e. Reason–Insight Coherence        | N/A         | 0.553       | Tie      | Mean cosine(Embed(reason), Embed(insight)) — reason grounding        |

---

## Conclusion

**Overall Winner**: QUIS (5 vs 16 metrics won)

