# Baseline vs IFQ_v4: Evaluation Report

## 4 CORE METRICS + 2 EFFICIENCY METRICS

**Generated**: 2026-04-21 20:02:42

---

## Executive Summary

- **Baseline Wins**: 3/14 metrics
- **IFQ_v4 Wins**: 11/14 metrics

### Key Findings

**Baseline Strengths:**
- **Faithfulness**: 100.0% vs 100.0%
- **Statistical Significance**: 94.0% vs 91.7%
- **Insight Novelty**: 92.2% vs 97.9%
- **Insight Diversity (Semantic)**: 0.330 vs 0.468
- **Insight Diversity (Subspace Entropy)**: 1.508 vs 1.354
- **Insight Diversity (Value)**: 0.323 vs 1.000
- **Insight Diversity (Dedup Rate)**: 0.364 vs 0.000

---

### Subspace Insights Analysis

- **Baseline**: 31/77 insights have subspace filter (40.3%)
- **IFQ_v4**: 45/97 insights have subspace filter (46.4%)
- Subspace Faithfulness: Baseline=100.0%  IFQ_v4=100.0%
- Subspace Significance: Baseline=100.0%  IFQ_v4=97.7%
- Subspace Novelty: Baseline=100.0%  IFQ_v4=100.0%
- Subspace Diversity: Baseline=0.344  IFQ_v4=0.444
- Score Uplift from Subspace (Baseline): mean_with=0.0 mean_without=0.0 delta=0.0 ratio=None
- Score Uplift from Subspace (IFQ_v4): mean_with=4.599931540031812 mean_without=1.054861306323688 delta=3.545070233708124 ratio=4.360697953803139
- Direction Uplift (Baseline): flat
- Direction Uplift (IFQ_v4): up

---

## Detailed Metrics Comparison

| Metric                           | Baseline      | IFQ_v4           | Winner   | Category   | Description                                             |
|:---------------------------------|:--------------|:-----------------|:---------|:-----------|:--------------------------------------------------------|
| 1. Faithfulness                  | 100.0%        | 100.0%           | IFQ_v4   | Core       | Correctness - đúng dữ liệu                              |
| 2. Statistical Significance      | 94.0%         | 91.7%            | Baseline | Core       | Validity - không phải noise                             |
| 3. Insight Novelty               | 92.2%         | 97.9%            | IFQ_v4   | Core       | Usefulness - khác baseline                              |
| 4a. Diversity — Semantic         | 0.330         | 0.468            | IFQ_v4   | Core       | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy | 1.508         | 1.354            | Baseline | Core       | Entropy of subspace filter columns used                 |
| 4c. Diversity — Value            | 0.323         | 1.000            | IFQ_v4   | Core       | Unique (column, value) pairs in subspace / total        |
| 4d. Diversity — Dedup Rate       | 0.364         | 0                | IFQ_v4   | Core       | Duplicate rate — lower is better                        |
| 7. Subspace Rate                 | 31/77 (40.3%) | 45/97 (46.4%)    | IFQ_v4   | Subspace   | Insights with subspace filter / total                   |
| 7a. Subspace Faithfulness        | 100.0%        | 100.0%           | IFQ_v4   | Subspace   | Faithfulness restricted to subspace insights            |
| 7b. Subspace Significance        | 100.0%        | 97.7%            | Baseline | Subspace   | Significance restricted to subspace insights            |
| 7c. Subspace Novelty             | 100.0%        | 100.0%           | IFQ_v4   | Subspace   | Novelty restricted to subspace insights                 |
| 7d. Subspace Diversity           | 0.344         | 0.444            | IFQ_v4   | Subspace   | Semantic diversity restricted to subspace insights      |
| 8. Score Uplift from Subspace    | Δ=0.000       | Δ=3.545, x=4.361 | IFQ_v4   | Subspace   | Δ = mean(score|subspace) - mean(score|no-subspace)      |
| 9. Direction Uplift              | flat          | up               | IFQ_v4   | Subspace   | Direction of Δ score uplift: up/down/flat               |

---

## Conclusion

**Overall Winner**: IFQ_v4 (3 vs 11 metrics)

