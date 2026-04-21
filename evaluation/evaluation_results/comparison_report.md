# IFQ vs Baseline: Evaluation Report

## 4 CORE METRICS + 2 EFFICIENCY METRICS

**Generated**: 2026-04-21 13:38:58

---

## Executive Summary

- **IFQ Wins**: 4/6 metrics
- **Baseline Wins**: 2/6 metrics

### Key Findings

**IFQ Strengths:**
- **Faithfulness**: 100.0% vs 100.0%
- **Statistical Significance**: 89.5% vs 94.0%
- **Insight Novelty**: 96.8% vs 92.2%
- **Insight Diversity**: 0.497 vs 0.272
- **Time to Insight**: 6.59s vs 7.72s per insight
- **Token Usage**: 832 vs 1518 tokens per insight

---

## Detailed Metrics Comparison

| Metric                      | IFQ    | Baseline   | Winner   | Category   | Description                      |
|:----------------------------|:-------|:-----------|:---------|:-----------|:---------------------------------|
| 1. Faithfulness             | 100.0% | 100.0%     | Baseline | Core       | Correctness - đúng dữ liệu       |
| 2. Statistical Significance | 89.5%  | 94.0%      | Baseline | Core       | Validity - không phải noise      |
| 3. Insight Novelty          | 96.8%  | 92.2%      | IFQ      | Core       | Usefulness - khác baseline       |
| 4. Insight Diversity        | 0.497  | 0.272      | IFQ      | Core       | Non-redundancy - không trùng lặp |
| 5. Time to Insight          | 6.59s  | 7.72s      | IFQ      | Efficiency | Speed - thời gian mỗi insight    |
| 6. Token Usage              | 832    | 1518       | IFQ      | Efficiency | Cost - tokens mỗi insight        |

---

## Conclusion

**Overall Winner**: IFQ (4 vs 2 metrics)

