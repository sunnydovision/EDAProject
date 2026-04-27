# ONLYSTATS vs QUIS: Evaluation Report

**Generated**: 2026-04-27 12:15:05

---

## Executive Summary

| | ONLYSTATS | QUIS |
|---|---|---|
| **Metrics Won** | 11 | 10 |
| **Overall Winner** | ✓ |  |

---

## Group 1 — Core Metrics & Efficiency

| Metric                                     | ONLYSTATS   | QUIS       | Winner    | Description                                             |
|:-------------------------------------------|:------------|:-----------|:----------|:--------------------------------------------------------|
| 0. Total insights                          | 93          | 97         | N/A       | Total insight cards generated                           |
| 1. Faithfulness                            | 100.0%      | 100.0%     | Tie       | Correctness - đúng dữ liệu                              |
| 2. Statistical Significance (Overall)      | 92.0%       | 74.7%      | ONLYSTATS | Validity - pattern-averaged (fair comparison)           |
| 2a. Significance — TREND                   | 100.0% (10) | 50.0% (2)  | ONLYSTATS | Validity - TREND pattern                                |
| 2a. Significance — OUTSTANDING_VALUE       | 68.2% (66)  | 53.0% (66) | ONLYSTATS | Validity - OUTSTANDING_VALUE pattern                    |
| 2a. Significance — ATTRIBUTION             | 100.0% (15) | 95.8% (24) | ONLYSTATS | Validity - ATTRIBUTION pattern                          |
| 2a. Significance — DISTRIBUTION_DIFFERENCE | 100.0% (2)  | 100.0% (4) | N/A       | Validity - DISTRIBUTION_DIFFERENCE pattern              |
| 3. Insight Novelty                         | 33.3%       | 61.9%      | QUIS      | Usefulness - khác baseline                              |
| 4a. Diversity — Semantic                   | 0.405       | 0.468      | QUIS      | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy           | 1.563       | 1.354      | ONLYSTATS | Entropy of subspace filter columns used                 |
| 4c. Diversity — Value                      | 0.788       | 1.000      | QUIS      | Unique (column, value) pairs in subspace / total        |
| 4d. Diversity — Dedup Rate                 | 0           | 0          | Tie       | Duplicate rate — lower is better                        |

---

## Group 2 — Subspace Deep-dive

| Metric                                        | ONLYSTATS         | QUIS              | Winner    | Description                                                          |
|:----------------------------------------------|:------------------|:------------------|:----------|:---------------------------------------------------------------------|
| 7. Subspace Rate                              | 33/93 (35.5%)     | 45/97 (46.4%)     | QUIS      | Insights with subspace filter / total                                |
| 7a. Subspace Faithfulness                     | 100.0%            | 100.0%            | Tie       | Faithfulness restricted to subspace insights                         |
| 7b. Subspace Significance                     | 60.0%             | 55.6%             | ONLYSTATS | Significance restricted to subspace insights                         |
| 7c. Subspace Novelty                          | 72.7%             | 77.8%             | QUIS      | Novelty restricted to subspace insights                              |
| 7d.1. Diversity — Semantic (Subspace)         | 0.401             | 0.444             | QUIS      | Semantic diversity restricted to subspace insights                   |
| 7d.2. Diversity — Subspace Entropy (Subspace) | 1.563             | 1.354             | ONLYSTATS | Entropy of subspace filter columns used (subspace insights)          |
| 7d.3. Diversity — Value (Subspace)            | 0.788             | 1.000             | QUIS      | Unique (column, value) pairs in subspace / total (subspace insights) |
| 7d.4. Diversity — Dedup Rate (Subspace)       | 0                 | 0                 | Tie       | Duplicate rate restricted to subspace insights - lower is better     |
| 8. Score Uplift from Subspace                 | Δ=-0.128, x=0.785 | Δ=-0.091, x=0.832 | QUIS      | Δ = mean(score|subspace) - mean(score|no-subspace)                   |
| 9. Direction Uplift                           | down              | down              | Tie       | Direction of Δ score uplift: up/down/flat                            |

---

## Group 3 — Intent Layer Quality

> Đánh giá mô-đun *Question Generation (QuGen)* ở hai lớp: **(3.1) Target structure** — chất lượng cặp `(breakdown, measure)` mà QuGen chọn; **(3.2) Question text & reason** — chất lượng câu hỏi và lý do ở dạng ngôn ngữ tự nhiên.

### 3.1 Target structure — `(breakdown, measure)`

| Metric                          | ONLYSTATS   | QUIS   | Winner    | Description                                                                                |
|:--------------------------------|:------------|:-------|:----------|:-------------------------------------------------------------------------------------------|
| 10. Total (B,M) pairs evaluated | 66/66       | 44/44  | N/A       | Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness) |
| 10a. BM — NMI mean              | 0.096       | 0.075  | ONLYSTATS | Mean NMI over categorical-B pairs                                                          |
| 10b. BM — Interestingness       | 0.105       | 0.085  | ONLYSTATS | Mean Coverage×EffectSize over categorical-B pairs                                          |
| 10c. BM — Actionability         | 1.000       | 1.000  | Tie       | % pairs with categorical breakdown                                                         |
| 10d. BM — Diversity             | 0.710       | 0.454  | ONLYSTATS | Unique (B,M) pairs / total insights                                                        |

### 3.2 Question text & reason

| Metric                               | ONLYSTATS   | QUIS        | Winner    | Description                                                          |
|:-------------------------------------|:------------|:------------|:----------|:---------------------------------------------------------------------|
| 11a. Question Semantic Diversity     | 0.405       | 0.521       | QUIS      | 1 - mean cosine sim of question embeddings (within-system)           |
| 11b. Question Specificity            | 7.57 ± 0.65 | 9.53 ± 1.76 | QUIS      | Avg word count per question (mean ± std) — higher = more specific    |
| 11c. Question–Insight Alignment      | 0.726       | 0.563       | ONLYSTATS | Mean cosine(Embed(question), Embed(insight)) — semantic faithfulness |
| 11d. Question Novelty (cross-system) | N/A         | 89.7%       | Tie       | % of questions with cross-system max cosine sim < 0.85               |
| 11e. Reason–Insight Coherence        | N/A         | 0.571       | Tie       | Mean cosine(Embed(reason), Embed(insight)) — reason grounding        |

---

## Conclusion

**Overall Winner**: ONLYSTATS (11 vs 10 metrics won)

