# ONLYSTATS vs QUIS: Evaluation Report

**Generated**: 2026-04-28 09:27:57

---

## Executive Summary

| | ONLYSTATS | QUIS |
|---|---|---|
| **Metrics Won** | 2 | 15 |
| **Overall Winner** |  | ✓ |

---

## Group 1 — Core Metrics & Efficiency

| Metric                                     | ONLYSTATS   | QUIS       | Winner   | Description                                             |
|:-------------------------------------------|:------------|:-----------|:---------|:--------------------------------------------------------|
| 0. Total insights                          | 200         | 133        | N/A      | Total insight cards generated                           |
| 1. Faithfulness                            | 100.0%      | 100.0%     | Tie      | Correctness - đúng dữ liệu                              |
| 2. Statistical Significance (Overall)      | 1.8%        | 16.8%      | QUIS     | Validity - pattern-averaged (fair comparison)           |
| 2a. Significance — TREND                   | N/A         | N/A        | N/A      | Validity - TREND pattern                                |
| 2a. Significance — OUTSTANDING_VALUE       | 0.0% (52)   | 22.2% (27) | QUIS     | Validity - OUTSTANDING_VALUE pattern                    |
| 2a. Significance — ATTRIBUTION             | 7.1% (56)   | 26.9% (26) | QUIS     | Validity - ATTRIBUTION pattern                          |
| 2a. Significance — DISTRIBUTION_DIFFERENCE | N/A         | 18.2% (33) | QUIS     | Validity - DISTRIBUTION_DIFFERENCE pattern              |
| 3. Insight Novelty                         | 77.5%       | 84.2%      | QUIS     | Usefulness - khác baseline                              |
| 4a. Diversity — Semantic                   | 0.451       | 0.499      | QUIS     | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy           | N/A         | 2.938      | QUIS     | Entropy of subspace filter columns used                 |
| 4c. Diversity — Value                      | N/A         | 0.767      | QUIS     | Unique (column, value) pairs in subspace / total        |
| 4d. Diversity — Dedup Rate                 | 0           | 0          | Tie      | Duplicate rate — lower is better                        |

---

## Group 2 — Subspace Deep-dive

| Metric                        | ONLYSTATS    | QUIS             | Winner   | Description                                        |
|:------------------------------|:-------------|:-----------------|:---------|:---------------------------------------------------|
| 7. Subspace Rate              | 0/200 (0.0%) | 116/133 (87.2%)  | QUIS     | Insights with subspace filter / total              |
| 8. Score Uplift from Subspace | N/A          | Δ=0.029, x=1.133 | QUIS     | Δ = mean(score|subspace) - mean(score|no-subspace) |
| 9. Direction Uplift           | N/A          | up               | QUIS     | Direction of Δ score uplift: up/down/flat          |

---

## Group 3 — Intent Layer Quality

> Đánh giá mô-đun *Question Generation (QuGen)* ở hai lớp: **(3.1) Target structure** — chất lượng cặp `(breakdown, measure)` mà QuGen chọn; **(3.2) Question text & reason** — chất lượng câu hỏi và lý do ở dạng ngôn ngữ tự nhiên.

### 3.1 Target structure — `(breakdown, measure)`

| Metric                          | ONLYSTATS   | QUIS   | Winner    | Description                                                                                |
|:--------------------------------|:------------|:-------|:----------|:-------------------------------------------------------------------------------------------|
| 10. Total (B,M) pairs evaluated | 60/112      | 31/51  | N/A       | Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness) |
| 10a. BM — NMI mean              | nan         | 0.024  | Tie       | Mean NMI over categorical-B pairs                                                          |
| 10b. BM — Interestingness       | 0.005       | 0.040  | QUIS      | Mean Coverage×EffectSize over categorical-B pairs                                          |
| 10c. BM — Actionability         | 0.536       | 0.608  | QUIS      | % pairs with categorical breakdown                                                         |
| 10d. BM — Diversity             | 0.560       | 0.384  | ONLYSTATS | Unique (B,M) pairs / total insights                                                        |

### 3.2 Question text & reason

| Metric                               | ONLYSTATS   | QUIS         | Winner    | Description                                                          |
|:-------------------------------------|:------------|:-------------|:----------|:---------------------------------------------------------------------|
| 11a. Question Semantic Diversity     | 0.487       | 0.597        | QUIS      | 1 - mean cosine sim of question embeddings (within-system)           |
| 11b. Question Specificity            | 6.00 ± 0.00 | 10.25 ± 2.51 | QUIS      | Avg word count per question (mean ± std) — higher = more specific    |
| 11c. Question–Insight Alignment      | 0.778       | 0.493        | ONLYSTATS | Mean cosine(Embed(question), Embed(insight)) — semantic faithfulness |
| 11d. Question Novelty (cross-system) | N/A         | 100.0%       | Tie       | % of questions with cross-system max cosine sim < 0.85               |
| 11e. Reason–Insight Coherence        | N/A         | 0.468        | Tie       | Mean cosine(Embed(reason), Embed(insight)) — reason grounding        |

---

## Conclusion

**Overall Winner**: QUIS (2 vs 15 metrics won)

