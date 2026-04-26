# QUIS vs Baseline: Evaluation Report

**Generated**: 2026-04-26 09:43:02

---

## Executive Summary

| | QUIS | Baseline |
|---|---|---|
| **Metrics Won** | 18 | 13 |
| **Overall Winner** | ✓ |  |

---

## Group 1 — Core Metrics & Efficiency

| Metric                                     | QUIS        | Baseline    | Winner   | Description                                                    |
|:-------------------------------------------|:-----------|:------------|:---------|:---------------------------------------------------------------|
| 0. Total insights                          | 97         | 86          | N/A      | Total insight cards generated                                  |
| 1. Faithfulness                            | 100.0%     | 100.0%      | Tie      | Correctness - đúng dữ liệu                                     |
| 2. Statistical Significance (Overall)      | 74.7%      | 60.3%       | QUIS      | Validity - pattern-averaged (fair comparison)                  |
| 2a. Significance — TREND                   | 50.0% (2)  | 93.3% (15)  | Baseline | Validity - TREND pattern                                       |
| 2a. Significance — OUTSTANDING_VALUE       | 53.0% (66) | 81.2% (16)  | Baseline | Validity - OUTSTANDING_VALUE pattern                           |
| 2a. Significance — ATTRIBUTION             | 95.8% (24) | N/A         | QUIS      | Validity - ATTRIBUTION pattern                                 |
| 2a. Significance — DISTRIBUTION_DIFFERENCE | 100.0% (4) | 66.7% (9)   | QUIS      | Validity - DISTRIBUTION_DIFFERENCE pattern                     |
| 2b. Pattern Coverage                       | 4/4 (100%) | 3/4 (75%)   | QUIS      | Patterns with ≥1 structurally valid insight / 4 total patterns |
| 2b1. Uncovered Patterns                    | —          | ATTRIBUTION | N/A      | Patterns with 0 valid insights (breakdown type mismatch)       |
| 3. Insight Novelty                         | 83.5%      | 84.9%       | Baseline | Usefulness - khác baseline                                     |
| 4a. Diversity — Semantic                   | 0.468      | 0.451       | QUIS      | Semantic diversity (breakdown|measure|pattern|subspace)        |
| 4b. Diversity — Subspace Entropy           | 1.354      | 1.516       | Baseline | Entropy of subspace filter columns used                        |
| 4c. Diversity — Value                      | 1.000      | 0.375       | QUIS      | Unique (column, value) pairs in subspace / total               |
| 4d. Diversity — Dedup Rate                 | 0          | 0.012       | QUIS      | Duplicate rate — lower is better                               |

---

## Group 2 — Subspace Deep-dive

| Metric                                        | QUIS               | Baseline          | Winner   | Description                                                          |
|:----------------------------------------------|:------------------|:------------------|:---------|:---------------------------------------------------------------------|
| 7. Subspace Rate                              | 45/97 (46.4%)     | 32/86 (37.2%)     | QUIS      | Insights with subspace filter / total                                |
| 7a. Subspace Faithfulness                     | 100.0%            | 100.0%            | Tie      | Faithfulness restricted to subspace insights                         |
| 7b. Subspace Significance                     | 73.3%             | 90.5%             | Baseline | Significance restricted to subspace insights                         |
| 7c. Subspace Novelty                          | 91.1%             | 96.9%             | Baseline | Novelty restricted to subspace insights                              |
| 7d.1. Diversity — Semantic (Subspace)         | 0.444             | 0.457             | Baseline | Semantic diversity restricted to subspace insights                   |
| 7d.2. Diversity — Subspace Entropy (Subspace) | 1.354             | 1.516             | Baseline | Entropy of subspace filter columns used (subspace insights)          |
| 7d.3. Diversity — Value (Subspace)            | 1.000             | 0.375             | QUIS      | Unique (column, value) pairs in subspace / total (subspace insights) |
| 7d.4. Diversity — Dedup Rate (Subspace)       | 0                 | 0                 | Tie      | Duplicate rate restricted to subspace insights - lower is better     |
| 8. Score Uplift from Subspace                 | Δ=-0.091, x=0.832 | Δ=-0.112, x=0.812 | QUIS      | Δ = mean(score|subspace) - mean(score|no-subspace)                   |
| 9. Direction Uplift                           | down              | down              | Tie      | Direction of Δ score uplift: up/down/flat                            |

---

## Group 3 — Intent Layer Quality

> Đánh giá mô-đun *QUGEN* ở hai lớp: **(3.1) Target structure** — chất lượng cặp `(breakdown, measure)` mà QUGEN chọn; **(3.2) Question text & reason** — chất lượng câu hỏi và lý do ở dạng ngôn ngữ tự nhiên.

### 3.1 Target structure — `(breakdown, measure)`

| Metric                          | QUIS   | Baseline   | Winner   | Description                                                                                |
|:--------------------------------|:------|:-----------|:---------|:-------------------------------------------------------------------------------------------|
| 10. Total (B,M) pairs evaluated | 44/44 | 21/31      | N/A      | Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness) |
| 10a. BM — NMI mean              | 0.075 | 0.121      | Baseline | Mean NMI over categorical-B pairs                                                          |
| 10b. BM — Interestingness       | 0.085 | 0.131      | Baseline | Mean Coverage×EffectSize over categorical-B pairs                                          |
| 10c. BM — Actionability         | 1.000 | 0.677      | QUIS      | % pairs with categorical breakdown                                                         |
| 10d. BM — Diversity             | 0.454 | 0.360      | QUIS      | Unique (B,M) pairs / total insights                                                        |

### 3.2 Question text & reason

| Metric                               | QUIS         | Baseline     | Winner   | Description                                                                                   |
|:-------------------------------------|:------------|:-------------|:---------|:----------------------------------------------------------------------------------------------|
| 11a. Question Semantic Diversity     | 0.521       | 0.596        | Baseline | 1 - mean cosine sim of question embeddings (within-system)                                    |
| 11b. Question Specificity            | 9.53 ± 1.76 | 12.78 ± 5.24 | Baseline | Avg word count per question (mean ± std) — higher = more specific                             |
| 11c. Question–Insight Alignment      | 0.563       | 0.576        | Baseline | Mean cosine(Embed(question), Embed(insight)) — control metric (Tie = both execute faithfully) |
| 11d. Question Novelty (cross-system) | 97.9%       | 95.3%        | QUIS      | % of questions with cross-system max cosine sim < 0.85                                        |
| 11e. Reason–Insight Coherence        | 0.571       | 0.510        | QUIS      | Mean cosine(Embed(reason), Embed(insight)) — reason grounding                                 |

### 3.3 Structural Validity Rate

| Metric                             | QUIS            | Baseline      | Winner   | Description                                                                                      |
|:-----------------------------------|:---------------|:--------------|:---------|:-------------------------------------------------------------------------------------------------|
| 12. Structural Validity Rate       | 100.0% (97/97) | 43.0% (37/86) | QUIS      | % insights with breakdown type valid for their pattern — measures QUGEN structural understanding |
| 12a. SVR — OUTSTANDING_VALUE       | 100% (66/66)   | 100% (16/16)  | Tie      | Structural validity for OUTSTANDING_VALUE pattern                                                |
| 12a. SVR — TREND                   | 100% (3/3)     | 38% (15/39)   | QUIS      | Structural validity for TREND pattern                                                            |
| 12a. SVR — ATTRIBUTION             | 100% (24/24)   | 0% (0/11)     | QUIS      | Structural validity for ATTRIBUTION pattern                                                      |
| 12a. SVR — DISTRIBUTION_DIFFERENCE | 100% (4/4)     | 30% (6/20)    | QUIS      | Structural validity for DISTRIBUTION_DIFFERENCE pattern                                          |

---

## Conclusion

**Overall Winner**: QUIS (18 vs 13 metrics won)

