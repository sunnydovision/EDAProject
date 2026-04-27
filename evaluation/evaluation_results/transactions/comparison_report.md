# QUIS vs Baseline: Evaluation Report

**Generated**: 2026-04-27 15:41:38

---

## Executive Summary

| | QUIS | Baseline |
|---|---|---|
| **Metrics Won** | 8 | 13 |
| **Overall Winner** |  | ✓ |

---

## Group 1 — Core Metrics & Efficiency

| Metric                                     | QUIS     | Baseline   | Winner   | Description                                             |
|:-------------------------------------------|:---------|:-----------|:---------|:--------------------------------------------------------|
| 0. Total insights                          | 12       | 21         | N/A      | Total insight cards generated                           |
| 1. Faithfulness                            | 100.0%   | 90.5%      | QUIS     | Correctness - đúng dữ liệu                              |
| 2. Statistical Significance (Overall)      | 0.0%     | 37.5%      | Baseline | Validity - pattern-averaged (fair comparison)           |
| 2a. Significance — TREND                   | N/A      | 50.0% (4)  | Baseline | Validity - TREND pattern                                |
| 2a. Significance — OUTSTANDING_VALUE       | 0.0% (1) | 100.0% (6) | Baseline | Validity - OUTSTANDING_VALUE pattern                    |
| 2a. Significance — ATTRIBUTION             | 0.0% (1) | N/A        | N/A      | Validity - ATTRIBUTION pattern                          |
| 2a. Significance — DISTRIBUTION_DIFFERENCE | 0.0% (1) | N/A        | N/A      | Validity - DISTRIBUTION_DIFFERENCE pattern              |
| 3. Insight Novelty                         | 100.0%   | 100.0%     | Tie      | Usefulness - khác baseline                              |
| 4a. Diversity — Semantic                   | 0.433    | 0.495      | Baseline | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy           | 1.748    | 1.040      | QUIS     | Entropy of subspace filter columns used                 |
| 4c. Diversity — Value                      | 0.917    | 0.750      | QUIS     | Unique (column, value) pairs in subspace / total        |
| 4d. Diversity — Dedup Rate                 | 0        | 0.095      | QUIS     | Duplicate rate — lower is better                        |

---

## Group 2 — Subspace Deep-dive

| Metric                                        | QUIS           | Baseline          | Winner   | Description                                                          |
|:----------------------------------------------|:---------------|:------------------|:---------|:---------------------------------------------------------------------|
| 7. Subspace Rate                              | 12/12 (100.0%) | 4/21 (19.0%)      | QUIS     | Insights with subspace filter / total                                |
| 7a. Subspace Faithfulness                     | 100.0%         | 100.0%            | Tie      | Faithfulness restricted to subspace insights                         |
| 7b. Subspace Significance                     | 0.0%           | 0.0%              | Tie      | Significance restricted to subspace insights                         |
| 7c. Subspace Novelty                          | 100.0%         | 100.0%            | Tie      | Novelty restricted to subspace insights                              |
| 7d.1. Diversity — Semantic (Subspace)         | 0.433          | 0.485             | Baseline | Semantic diversity restricted to subspace insights                   |
| 7d.2. Diversity — Subspace Entropy (Subspace) | 1.748          | 1.040             | QUIS     | Entropy of subspace filter columns used (subspace insights)          |
| 7d.3. Diversity — Value (Subspace)            | 0.917          | 0.750             | QUIS     | Unique (column, value) pairs in subspace / total (subspace insights) |
| 7d.4. Diversity — Dedup Rate (Subspace)       | 0              | 0                 | Tie      | Duplicate rate restricted to subspace insights - lower is better     |
| 8. Score Uplift from Subspace                 | N/A            | Δ=-0.486, x=0.145 | QUIS     | Δ = mean(score|subspace) - mean(score|no-subspace)                   |
| 9. Direction Uplift                           | N/A            | down              | Baseline | Direction of Δ score uplift: up/down/flat                            |

---

## Group 3 — Intent Layer Quality

> Đánh giá mô-đun *Question Generation (QuGen)* ở hai lớp: **(3.1) Target structure** — chất lượng cặp `(breakdown, measure)` mà QuGen chọn; **(3.2) Question text & reason** — chất lượng câu hỏi và lý do ở dạng ngôn ngữ tự nhiên.

### 3.1 Target structure — `(breakdown, measure)`

| Metric                          | QUIS   | Baseline   | Winner   | Description                                                                                |
|:--------------------------------|:-------|:-----------|:---------|:-------------------------------------------------------------------------------------------|
| 10. Total (B,M) pairs evaluated | 1/4    | 2/8        | N/A      | Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness) |
| 10a. BM — NMI mean              | 0.002  | 0.370      | Baseline | Mean NMI over categorical-B pairs                                                          |
| 10b. BM — Interestingness       | 0.001  | 1.000      | Baseline | Mean Coverage×EffectSize over categorical-B pairs                                          |
| 10c. BM — Actionability         | 0.250  | 0.250      | Tie      | % pairs with categorical breakdown                                                         |
| 10d. BM — Diversity             | 0.333  | 0.381      | Baseline | Unique (B,M) pairs / total insights                                                        |

### 3.2 Question text & reason

| Metric                               | QUIS        | Baseline     | Winner   | Description                                                          |
|:-------------------------------------|:------------|:-------------|:---------|:---------------------------------------------------------------------|
| 11a. Question Semantic Diversity     | 0.406       | 0.556        | Baseline | 1 - mean cosine sim of question embeddings (within-system)           |
| 11b. Question Specificity            | 9.50 ± 0.87 | 13.76 ± 8.22 | Baseline | Avg word count per question (mean ± std) — higher = more specific    |
| 11c. Question–Insight Alignment      | 0.262       | 0.506        | Baseline | Mean cosine(Embed(question), Embed(insight)) — semantic faithfulness |
| 11d. Question Novelty (cross-system) | 100.0%      | 100.0%       | Tie      | % of questions with cross-system max cosine sim < 0.85               |
| 11e. Reason–Insight Coherence        | 0.203       | 0.355        | Baseline | Mean cosine(Embed(reason), Embed(insight)) — reason grounding        |

---

## Conclusion

**Overall Winner**: Baseline (8 vs 13 metrics won)

