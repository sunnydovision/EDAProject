# Evaluation Framework for QUIS vs Baseline

Comprehensive evaluation comparing QUIS and Baseline EDA systems.

## Quick Start

```bash
# Run full evaluation
python evaluation/run_evaluation.py \
  --data data/Adidas.csv \
  --quis insights_summary_v2.json \
  --baseline baseline/auto_eda_agent/output/quis_format/insights_summary.json \
  --output evaluation/results
```

## Output

The evaluation generates:

```
evaluation/results/
├── quis_results.json              # QUIS metrics
├── baseline_results.json          # Baseline metrics
├── comparison_table.csv           # Side-by-side comparison
├── comparison_report.md           # Full markdown report
└── plots/
    ├── core_metrics.png           # Yield, Score, Redundancy
    ├── coverage_metrics.png       # Schema, Pattern, Subspace
    ├── pattern_distribution.png   # Pattern type distribution
    └── radar_comparison.png       # Overall radar chart
```

## Metrics Computed

### Core Metrics ⭐⭐⭐
1. **Insight Yield**: `|I| / |Q|` - Insights per question
2. **Average Score**: Mean ISGEN score
3. **Redundancy**: Duplicate (B,M,S,P) tuples

### Coverage Metrics ⭐⭐
4. **Schema Coverage**: Columns explored
5. **Pattern Coverage**: Pattern types found
6. **Subspace Exploration**: Conditional patterns (KEY DIFFERENTIATOR)

### Quality Metrics ⭐
7. **Question Diversity**: Semantic diversity of questions
8. **Insight Significance**: Z-Score statistical significance (p < 0.05)
9. **Faithfulness**: Hallucination detection (data grounding)

### Performance Metrics ⭐⭐⭐
10. **Time-to-Insight (TTI)**: Evaluation execution time

## File Structure

```
evaluation/
├── compute_metrics.py      # All metric computation functions
├── compare_systems.py      # Comparison tables and plots
├── run_evaluation.py       # Main entry point
└── README.md              # This file
```

## Metric Definitions

See `../EVALUATION_METRICS.md` for detailed metric definitions and formulas.

## Expected Results

| Metric | QUIS Expected | Baseline Expected | Winner |
|--------|---------------|-------------------|--------|
| Insight Yield | Higher | Lower | QUIS |
| Avg Score | Similar | Similar | Tie |
| Redundancy | Lower | Higher | QUIS |
| Schema Coverage | Higher | Lower | QUIS |
| Pattern Coverage | Lower | Higher | Baseline |
| **Subspace Exploration** | **Much Higher** | **~0** | **QUIS** |
| Question Diversity | Similar | Similar | Tie |
| Insight Significance | Higher | Lower | QUIS |
| **Faithfulness** | **~100%** | **85-95%** | **QUIS** |
| Time-to-Insight | Faster | Slower | QUIS |

**Key Insight**: Subspace exploration is the critical differentiator showing QUIS's advantage.

## Requirements

```bash
pip install pandas numpy matplotlib seaborn sentence-transformers scikit-learn
```

## Usage Examples

### 1. Basic Evaluation

```bash
python evaluation/run_evaluation.py \
  --data data/Adidas.csv \
  --quis insights_summary_v2.json \
  --baseline baseline/auto_eda_agent/output/quis_format/insights_summary.json
```

### 2. Custom Output Directory

```bash
python evaluation/run_evaluation.py \
  --data data/Adidas.csv \
  --quis insights_summary_v2.json \
  --baseline baseline/auto_eda_agent/output/quis_format/insights_summary.json \
  --output my_evaluation_results
```

### 3. Multiple Datasets

```bash
# Dataset 1
python evaluation/run_evaluation.py \
  --data data/Adidas.csv \
  --quis quis_adidas.json \
  --baseline baseline_adidas.json \
  --output evaluation/adidas

# Dataset 2
python evaluation/run_evaluation.py \
  --data data/Transactions.csv \
  --quis quis_transactions.json \
  --baseline baseline_transactions.json \
  --output evaluation/transactions
```

## Interpreting Results

### High QUIS Yield
- QUIS generates more usable insights per question
- Indicates efficient question generation

### Low Redundancy
- Fewer duplicate insights
- Better deduplication in pipeline

### High Subspace Rate
- More conditional patterns discovered
- Key advantage of QUIS's beam search

### High Schema Coverage
- More comprehensive data exploration
- Explores more columns

## Troubleshooting

### Missing sentence-transformers
```bash
pip install sentence-transformers
```

### File not found
- Ensure paths are correct
- Use absolute paths if needed

### Empty insights
- Check that insights_summary.json has correct format
- Verify insights passed ISGEN threshold

## Citation

If using this evaluation framework, please cite:

```
@article{quis2026,
  title={QUIS: Question-driven Insight Generation for Exploratory Data Analysis},
  author={...},
  year={2026}
}
```
