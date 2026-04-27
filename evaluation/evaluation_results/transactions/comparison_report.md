# ONLYSTATS vs QUIS: Evaluation Report

**Generated**: 2026-04-27 16:17:34

---

## Executive Summary

| | ONLYSTATS | QUIS |
|---|---|---|
| **Metrics Won** | 16 | 7 |
| **Overall Winner** | ✓ |  |

---

## Group 1 — Core Metrics & Efficiency

| Metric                                     | ONLYSTATS   | QUIS     | Winner    | Description                                             |
|:-------------------------------------------|:------------|:---------|:----------|:--------------------------------------------------------|
| 0. Total insights                          | 98          | 12       | N/A       | Total insight cards generated                           |
| 1. Faithfulness                            | 90.8%       | 100.0%   | QUIS      | Correctness - đúng dữ liệu                              |
| 2. Statistical Significance (Overall)      | 44.3%       | 0.0%     | ONLYSTATS | Validity - pattern-averaged (fair comparison)           |
| 2a. Significance — TREND                   | N/A         | N/A      | N/A       | Validity - TREND pattern                                |
| 2a. Significance — OUTSTANDING_VALUE       | 80.0% (25)  | 0.0% (1) | ONLYSTATS | Validity - OUTSTANDING_VALUE pattern                    |
| 2a. Significance — ATTRIBUTION             | 77.1% (48)  | 0.0% (1) | ONLYSTATS | Validity - ATTRIBUTION pattern                          |
| 2a. Significance — DISTRIBUTION_DIFFERENCE | 20.0% (5)   | 0.0% (1) | ONLYSTATS | Validity - DISTRIBUTION_DIFFERENCE pattern              |
| 3. Insight Novelty                         | 100.0%      | 100.0%   | Tie       | Usefulness - khác baseline                              |
| 4a. Diversity — Semantic                   | 0.393       | 0.433    | QUIS      | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy           | 3.009       | 1.748    | ONLYSTATS | Entropy of subspace filter columns used                 |
| 4c. Diversity — Value                      | 0.920       | 0.917    | ONLYSTATS | Unique (column, value) pairs in subspace / total        |
| 4d. Diversity — Dedup Rate                 | 0           | 0        | Tie       | Duplicate rate — lower is better                        |

---

## Group 2 — Subspace Deep-dive

| Metric                                        | ONLYSTATS        | QUIS           | Winner    | Description                                                          |
|:----------------------------------------------|:-----------------|:---------------|:----------|:---------------------------------------------------------------------|
| 7. Subspace Rate                              | 50/98 (51.0%)    | 12/12 (100.0%) | QUIS      | Insights with subspace filter / total                                |
| 7a. Subspace Faithfulness                     | 92.0%            | 100.0%         | QUIS      | Faithfulness restricted to subspace insights                         |
| 7b. Subspace Significance                     | 68.8%            | 0.0%           | ONLYSTATS | Significance restricted to subspace insights                         |
| 7c. Subspace Novelty                          | 100.0%           | 100.0%         | Tie       | Novelty restricted to subspace insights                              |
| 7d.1. Diversity — Semantic (Subspace)         | 0.322            | 0.433          | QUIS      | Semantic diversity restricted to subspace insights                   |
| 7d.2. Diversity — Subspace Entropy (Subspace) | 3.009            | 1.748          | ONLYSTATS | Entropy of subspace filter columns used (subspace insights)          |
| 7d.3. Diversity — Value (Subspace)            | 0.920            | 0.917          | ONLYSTATS | Unique (column, value) pairs in subspace / total (subspace insights) |
| 7d.4. Diversity — Dedup Rate (Subspace)       | 0                | 0              | Tie       | Duplicate rate restricted to subspace insights - lower is better     |
| 8. Score Uplift from Subspace                 | Δ=0.048, x=1.157 | N/A            | ONLYSTATS | Δ = mean(score|subspace) - mean(score|no-subspace)                   |
| 9. Direction Uplift                           | up               | N/A            | ONLYSTATS | Direction of Δ score uplift: up/down/flat                            |

---

## Group 3 — Intent Layer Quality

> Đánh giá mô-đun *Question Generation (QuGen)* ở hai lớp: **(3.1) Target structure** — chất lượng cặp `(breakdown, measure)` mà QuGen chọn; **(3.2) Question text & reason** — chất lượng câu hỏi và lý do ở dạng ngôn ngữ tự nhiên.

### 3.1 Target structure — `(breakdown, measure)`

| Metric                          | ONLYSTATS   | QUIS   | Winner    | Description                                                                                |
|:--------------------------------|:------------|:-------|:----------|:-------------------------------------------------------------------------------------------|
| 10. Total (B,M) pairs evaluated | 49/49       | 1/4    | N/A       | Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness) |
| 10a. BM — NMI mean              | 0.089       | 0.002  | ONLYSTATS | Mean NMI over categorical-B pairs                                                          |
| 10b. BM — Interestingness       | 0.167       | 0.001  | ONLYSTATS | Mean Coverage×EffectSize over categorical-B pairs                                          |
| 10c. BM — Actionability         | 1.000       | 0.250  | ONLYSTATS | % pairs with categorical breakdown                                                         |
| 10d. BM — Diversity             | 0.500       | 0.333  | ONLYSTATS | Unique (B,M) pairs / total insights                                                        |

### 3.2 Question text & reason

| Metric                               | ONLYSTATS   | QUIS        | Winner    | Description                                                          |
|:-------------------------------------|:------------|:------------|:----------|:---------------------------------------------------------------------|
| 11a. Question Semantic Diversity     | 0.385       | 0.406       | QUIS      | 1 - mean cosine sim of question embeddings (within-system)           |
| 11b. Question Specificity            | 8.00 ± 0.74 | 9.50 ± 0.87 | QUIS      | Avg word count per question (mean ± std) — higher = more specific    |
| 11c. Question–Insight Alignment      | 0.762       | 0.262       | ONLYSTATS | Mean cosine(Embed(question), Embed(insight)) — semantic faithfulness |
| 11d. Question Novelty (cross-system) | N/A         | 100.0%      | Tie       | % of questions with cross-system max cosine sim < 0.85               |
| 11e. Reason–Insight Coherence        | N/A         | 0.203       | Tie       | Mean cosine(Embed(reason), Embed(insight)) — reason grounding        |

---

## Conclusion

**Overall Winner**: ONLYSTATS (16 vs 7 metrics won)

