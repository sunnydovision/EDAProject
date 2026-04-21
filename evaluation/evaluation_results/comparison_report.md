# IFQ vs Baseline: Evaluation Report

## 4 CORE METRICS + 2 EFFICIENCY METRICS

**Generated**: 2026-04-21 15:11:15

---

## Executive Summary

- **IFQ Wins**: 9/14 metrics
- **Baseline Wins**: 5/14 metrics

### Key Findings

**IFQ Strengths:**
- **Faithfulness**: 100.0% vs 100.0%
- **Statistical Significance**: 89.5% vs 94.0%
- **Insight Novelty**: 96.8% vs 92.2%
- **Insight Diversity (Semantic)**: 0.459 vs 0.330
- **Insight Diversity (Subspace Entropy)**: 1.959 vs 1.508
- **Insight Diversity (Value)**: 0.951 vs 0.323
- **Insight Diversity (Dedup Rate)**: 0.000 vs 0.364
- **Time to Insight**: 6.59s vs 7.72s per insight
- **Token Usage**: 832 vs 1518 tokens per insight

---

### Subspace Insights Analysis

- **IFQ**: 41/93 insights have subspace filter (44.1%)
- **Baseline**: 31/77 insights have subspace filter (40.3%)
- Subspace Faithfulness: IFQ=100.0%  Baseline=100.0%
- Subspace Significance: IFQ=97.6%  Baseline=100.0%
- Subspace Novelty: IFQ=100.0%  Baseline=100.0%
- Subspace Diversity: IFQ=0.439  Baseline=0.344

---

## Detailed Metrics Comparison

| Metric                           | IFQ           | Baseline      | Winner   | Category   | Description                                             |
|:---------------------------------|:--------------|:--------------|:---------|:-----------|:--------------------------------------------------------|
| 1. Faithfulness                  | 100.0%        | 100.0%        | Baseline | Core       | Correctness - đúng dữ liệu                              |
| 2. Statistical Significance      | 89.5%         | 94.0%         | Baseline | Core       | Validity - không phải noise                             |
| 3. Insight Novelty               | 96.8%         | 92.2%         | IFQ      | Core       | Usefulness - khác baseline                              |
| 4a. Diversity — Semantic         | 0.459         | 0.330         | IFQ      | Core       | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy | 1.959         | 1.508         | IFQ      | Core       | Entropy of subspace filter columns used                 |
| 4c. Diversity — Value            | 0.951         | 0.323         | IFQ      | Core       | Unique (column, value) pairs in subspace / total        |
| 4d. Diversity — Dedup Rate       | 0             | 0.364         | IFQ      | Core       | Duplicate rate — lower is better                        |
| 5. Time to Insight               | 6.59s         | 7.72s         | IFQ      | Efficiency | Speed - thời gian mỗi insight                           |
| 6. Token Usage                   | 832           | 1518          | IFQ      | Efficiency | Cost - tokens mỗi insight                               |
| 7. Subspace Rate                 | 41/93 (44.1%) | 31/77 (40.3%) | IFQ      | Subspace   | Insights with subspace filter / total                   |
| 7a. Subspace Faithfulness        | 100.0%        | 100.0%        | Baseline | Subspace   | Faithfulness restricted to subspace insights            |
| 7b. Subspace Significance        | 97.6%         | 100.0%        | Baseline | Subspace   | Significance restricted to subspace insights            |
| 7c. Subspace Novelty             | 100.0%        | 100.0%        | Baseline | Subspace   | Novelty restricted to subspace insights                 |
| 7d. Subspace Diversity           | 0.439         | 0.344         | IFQ      | Subspace   | Semantic diversity restricted to subspace insights      |

---

## Conclusion

**Overall Winner**: IFQ (9 vs 5 metrics)

