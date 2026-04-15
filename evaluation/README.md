# Evaluation v2 - 4 CORE METRICS + 2 EFFICIENCY METRICS

Comprehensive evaluation comparing IFQ and Baseline EDA systems using **4 CORE METRICS** for defense and **2 EFFICIENCY METRICS** for performance analysis.

## Quick Start

```bash
# Run full evaluation
python evaluation_v2/run_evaluation.py \
  --data data/Adidas_cleaned.csv \
  --system_a IFQ \
  --path_a insights_summary_adidas_2.json \
  --system_b Baseline \
  --path_b baseline/auto_eda_agent/output/quis_format/insights_summary.json \
  --output evaluation_results
```

## Output

The evaluation generates:

```
evaluation_results/
├── ifq_results.json              # IFQ metrics
├── baseline_results.json          # Baseline metrics
├── comparison_table.csv           # Side-by-side comparison
├── comparison_report.md           # Full markdown report
```

---

# 1. METRICS

## 4 CORE METRICS (for Defense)

### 1. Faithfulness (Correctness - đúng dữ liệu)

**Formula**:
```
Faithfulness = (1/N) * Σ 1(Δ_i < ε)
```

**Where**:
- Δ_i = |v_i^{reported} - v_i^{recomputed}|
- ε = 1e-6 (numeric) or relative error < 1%

**Meaning**: Measures whether insights are grounded in actual data (no hallucinations).

**Implementation**:
1. Parse breakdown, measure, and subspace from insight
2. Recompute: `df_filtered = apply_filter(df, subspace)`, `result = df_filtered.groupby(breakdown).agg(measure)`
3. Compare recomputed value with reported value
4. Insight is faithful if difference < threshold

**Characteristics**:
- Objective: Data-driven verification
- No reliance on model internal scores
- Grounded in actual data recomputation

---

### 2. Statistical Significance (Validity - không phải noise)

**Formula**:
```
Significance Rate = (1/N) * Σ 1(p_i < α)
```

**Where**:
- p_i: p-value of insight i
- α = 0.05

**Meaning**: Measures whether insights are statistically significant (not random noise).

**Pattern-specific p-values**:
- **Trend**: Linear regression p-value (tests if coefficient ≠ 0)
- **Outstanding Value**: Z-test p-value (tests if value is outlier)
- **Attribution**: Chi-square test p-value (tests distribution uniformity)
- **Distribution Difference**: KS-test p-value (tests if distributions differ)

**Characteristics**:
- Statistical foundation
- Pattern-specific tests
- Controls for false discoveries

---

### 3. Insight Novelty (Usefulness - khác baseline)

**Formula**:
```
Novelty = (1/|A|) * Σ_{i ∈ A} 1(max_{j ∈ B} sim(i, j) < τ)
```

**Where**:
- A: insights from system A
- B: insights from system B
- sim: cosine similarity
- τ = 0.85

**Insight Representation**:
```
"{breakdown} | {measure} | {pattern} | {condition}"
```

**Meaning**: Measures how many insights are novel compared to the other system (non-trivial discovery).

**Implementation**:
1. Convert insights to structured string representation
2. Embed using sentence-transformers
3. Compute cosine similarity
4. Insight is novel if max similarity < threshold

**Characteristics**:
- Comparative metric
- Embedding-based semantic similarity
- Measures non-trivial discovery

---

### 4. Insight Diversity (Non-redundancy - không trùng lặp)

**Formula**:
```
Diversity = (2 / (N(N-1))) * Σ_{i<j} (1 - sim(i, j))
```

**Where**:
- sim: cosine similarity between embeddings
- N: number of insights

**Meaning**: Measures how spread out the insights are (no duplicate ideas).

**Characteristics**:
- Higher is better: More diverse insights
- Structural metric
- Measures redundancy within system

---

## 2 EFFICIENCY METRICS

### 5. Time to Insight (Efficiency - Speed)

**Formula**:
```
Time per Insight = Total Time / Number of Insights
```

**Meaning**: Measures how long each system takes to generate insights.

**Implementation**:
- Total time measured from pipeline start to completion
- Includes all steps (profiling, quality, statistics, patterns, insights)
- Lower is better

**Characteristics**:
- Practical performance metric
- End-to-end measurement
- Includes all overhead

---

### 6. Token Usage (Efficiency - Cost)

**Formula**:
```
Tokens per Insight = Total Tokens / Number of Insights
```

**Meaning**: Measures how many tokens each system uses to generate insights.

**Implementation**:
- Total tokens from LLM API (input + output)
- Number of insights generated
- Lower is better

**Characteristics**:
- Cost efficiency metric
- LLM resource usage
- Scalability indicator

---

# 2. MAIN QUANTITATIVE RESULTS

## Results on Adidas Dataset

| Metric                      | IFQ    | Baseline   | Winner   | Category   |
|:----------------------------|:-------|:-----------|:---------|:----------|
| 1. Faithfulness             | 100.0% | 51.9%      | IFQ      | Core      |
| 2. Statistical Significance | 47.7%  | 98.9%      | Baseline | Core      |
| 3. Insight Novelty          | 85.4%  | 85.7%      | Baseline | Core      |
| 4. Insight Diversity        | 0.521  | 0.315      | IFQ      | Core      |
| 5. Time to Insight          | 14.35s | 5.23s      | Baseline | Efficiency|
| 6. Token Usage              | 871    | 886        | IFQ      | Efficiency|

**Overall**: IFQ wins 3/6 metrics, Baseline wins 3/6 metrics (Tie)

## Key Findings

### IFQ Strengths
- **Faithfulness**: Perfect (100%) - all insights grounded in actual data
- **Diversity**: Higher (0.521) - more spread out insights
- **Token Efficiency**: Slightly better (871 vs 886 tokens per insight)

### Baseline Strengths
- **Statistical Significance**: Excellent (98.9%) - insights are statistically valid
- **Novelty**: Slightly higher (85.7%) - more novel insights
- **Time to Insight**: Much faster (5.23s vs 14.35s per insight)

## File Structure

```
evaluation_v2/
├── data_loader.py              # Data loading and cleaning
├── faithfulness.py             # Faithfulness metric computation
├── significance.py             # Statistical significance computation
├── novelty.py                  # Insight novelty computation
├── diversity.py                # Insight diversity computation
├── time_to_insight.py          # Time to insight metric
├── token_usage.py              # Token usage metric
├── compare.py                  # Comparison tables and reports
├── run_evaluation.py           # Main evaluation script
├── timing.json                 # Timing data for both systems
├── token.json                  # Token usage data for both systems
└── README.md                   # This file
```

## Usage Examples

### 1. Basic Evaluation

```bash
python evaluation_v2/run_evaluation.py \
  --data data/Adidas_cleaned.csv \
  --system_a IFQ \
  --path_a insights_summary_adidas_2.json \
  --system_b Baseline \
  --path_b baseline/auto_eda_agent/output/quis_format/insights_summary.json
```

### 2. Custom Output Directory

```bash
python evaluation_v2/run_evaluation.py \
  --data data/Adidas_cleaned.csv \
  --system_a IFQ \
  --path_a insights_summary_adidas_2.json \
  --system_b Baseline \
  --path_b baseline/auto_eda_agent/output/quis_format/insights_summary.json \
  --output my_evaluation_results
```

## Requirements

```bash
pip install pandas numpy sentence-transformers scikit-learn
```

## Why These 6 Metrics Are Comprehensive

1. **Model-Independent**: No reliance on internal scores or rules
2. **Unbiased**: Both systems evaluated with identical pipeline
3. **Grounded**: Based on statistics, IR, NLP, and performance foundations
4. **Comprehensive**: Covers all key aspects:
   - Correctness → Faithfulness
   - Validity → Statistical Significance
   - Usefulness → Insight Novelty
   - Redundancy → Insight Diversity
   - Speed → Time to Insight
   - Cost → Token Usage
