# IFQ vs Baseline: Evaluation Report

**Generated**: 2026-04-22 01:41:19

---

## Executive Summary

| | IFQ | Baseline |
|---|---|---|
| **Metrics Won** | 11 | 10 |
| **Overall Winner** | ✓ |  |

---

## Group 1 — Core Metrics & Efficiency

| Metric                                     | IFQ        | Baseline   | Winner   | Description                                             |
|:-------------------------------------------|:-----------|:-----------|:---------|:--------------------------------------------------------|
| 0. Total insights                          | 97         | 86         | N/A      | Total insight cards generated                           |
| 1. Faithfulness                            | 100.0%     | 100.0%     | Tie      | Correctness - đúng dữ liệu                              |
| 2. Statistical Significance (Overall)      | 74.7%      | 60.3%      | IFQ      | Validity - pattern-averaged (fair comparison)           |
| 2a. Significance — TREND                   | 50.0% (2)  | 93.3% (15) | Baseline | Validity - TREND pattern                                |
| 2a. Significance — OUTSTANDING_VALUE       | 53.0% (66) | 81.2% (16) | Baseline | Validity - OUTSTANDING_VALUE pattern                    |
| 2a. Significance — ATTRIBUTION             | 95.8% (24) | N/A        | IFQ      | Validity - ATTRIBUTION pattern                          |
| 2a. Significance — DISTRIBUTION_DIFFERENCE | 100.0% (4) | 66.7% (9)  | IFQ      | Validity - DISTRIBUTION_DIFFERENCE pattern              |
| 3. Insight Novelty                         | 83.5%      | 84.9%      | Baseline | Usefulness - khác baseline                              |
| 4a. Diversity — Semantic                   | 0.468      | 0.451      | IFQ      | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy           | 1.354      | 1.516      | Baseline | Entropy of subspace filter columns used                 |
| 4c. Diversity — Value                      | 1.000      | 0.375      | IFQ      | Unique (column, value) pairs in subspace / total        |
| 4d. Diversity — Dedup Rate                 | 0          | 0.012      | IFQ      | Duplicate rate — lower is better                        |

---

## Group 2 — Subspace Deep-dive

| Metric                                        | IFQ               | Baseline          | Winner   | Description                                                          |
|:----------------------------------------------|:------------------|:------------------|:---------|:---------------------------------------------------------------------|
| 7. Subspace Rate                              | 45/97 (46.4%)     | 32/86 (37.2%)     | IFQ      | Insights with subspace filter / total                                |
| 7a. Subspace Faithfulness                     | 100.0%            | 100.0%            | Tie      | Faithfulness restricted to subspace insights                         |
| 7b. Subspace Significance                     | 55.6%             | 66.7%             | Baseline | Significance restricted to subspace insights                         |
| 7c. Subspace Novelty                          | 91.1%             | 96.9%             | Baseline | Novelty restricted to subspace insights                              |
| 7d.1. Diversity — Semantic (Subspace)         | 0.444             | 0.457             | Baseline | Semantic diversity restricted to subspace insights                   |
| 7d.2. Diversity — Subspace Entropy (Subspace) | 1.354             | 1.516             | Baseline | Entropy of subspace filter columns used (subspace insights)          |
| 7d.3. Diversity — Value (Subspace)            | 1.000             | 0.375             | IFQ      | Unique (column, value) pairs in subspace / total (subspace insights) |
| 7d.4. Diversity — Dedup Rate (Subspace)       | 0                 | 0                 | Tie      | Duplicate rate restricted to subspace insights - lower is better     |
| 8. Score Uplift from Subspace                 | Δ=-0.091, x=0.832 | Δ=-0.112, x=0.812 | IFQ      | Δ = mean(score|subspace) - mean(score|no-subspace)                   |
| 9. Direction Uplift                           | down              | down              | Tie      | Direction of Δ score uplift: up/down/flat                            |

---

## Group 3 — Breakdown|Measure Deep-dive

| Metric                          | IFQ   | Baseline   | Winner   | Description                                                                                |
|:--------------------------------|:------|:-----------|:---------|:-------------------------------------------------------------------------------------------|
| 10. Total (B,M) pairs evaluated | 44/44 | 21/31      | N/A      | Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness) |
| 10a. BM — NMI mean              | 0.075 | 0.121      | Baseline | Mean NMI over categorical-B pairs                                                          |
| 10b. BM — Interestingness       | 0.085 | 0.131      | Baseline | Mean Coverage×EffectSize over categorical-B pairs                                          |
| 10c. BM — Actionability         | 1.000 | 0.677      | IFQ      | % pairs with categorical breakdown                                                         |
| 10d. BM — Diversity             | 0.454 | 0.360      | IFQ      | Unique (B,M) pairs / total insights                                                        |

---

## Conclusion

**Overall Winner**: IFQ (11 vs 10 metrics won)

