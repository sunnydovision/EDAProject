# Expert-Driven Agentic AutoEDA Baseline

A true agentic AutoEDA system where LLM acts as multiple expert specialists performing comprehensive exploratory data analysis.

## 🎯 Overview

This baseline implements an **expert-driven agentic workflow** where:
1. **LLM acts as domain experts** - not code generators, but actual analysts
2. **Each step is an autonomous specialist agent** with deep domain knowledge
3. **Multi-phase analysis** - profiling, quality, statistics, patterns, insights
4. **Direct analysis** - LLM analyzes data directly instead of writing code
5. **ISGEN scoring** - insights evaluated using academic methodology

## 📊 ISGEN Scoring

Insights are scored using patterns from the ISGEN paper:

| Pattern | Scoring Function | Threshold | Description |
|---------|-----------------|-----------|-------------|
| **TREND** | Mann-Kendall test (1 - p_value) | 0.95 | Monotonic trend detection |
| **OUTSTANDING_VALUE** | max/second_max ratio | 1.4 | Outlier/anomaly detection |
| **ATTRIBUTION** | max/sum ratio | 0.5 | Dominant category detection |
| **QUALITY** | Heuristic quality score | 0.6 | For other insight types |

## 🚀 Quick Start

### Prereifqites

```bash
# Install dependencies
pip install -r ../../requirements.txt

# Setup OpenAI API key
cp ../../.env.example ../../.env
# Edit .env and add your OPENAI_API_KEY
```

### Run Baseline

```bash
cd baseline/auto_eda_agent
python run.py ../../data/transactions.csv output
```

### Run Demo

The demo app visualizes the baseline pipeline results interactively:

```bash
# Activate virtual environment
source venv/bin/activate

# Run Streamlit demo from root (port 8502 to avoid conflict with main app)
streamlit run baseline/auto_eda_agent/demo/app.py --server.port 8502
```

**Demo Features:**
- Interactive visualization of 5-step EDA pipeline
- Sub-step breakdown with Input/Process/Output format
- Modal dialogs to view LLM prompts (Template vs Actual)
- Toggle between prompt modes with data-filled examples
- Dark theme with configurable colors (see `.streamlit/config.toml`)

**Demo Requirements:**
- Baseline pipeline must be run first to generate output JSON files
- Data file: `data/Adidas_cleaned.csv`
- Output directory: `baseline/auto_eda_agent/output/` (contains results from pipeline)

### Output Structure

```
output/
├── step1_profiling/
│   ├── profile.json           # Comprehensive data profile with semantic analysis
│   └── summary.md             # Human-readable profile summary
├── step2_quality/
│   ├── quality_report.json    # Quality metrics + expert assessment
│   └── summary.md             # Quality issues and recommendations
├── step3_statistics/
│   ├── statistics.json        # Statistics + expert interpretation
│   └── summary.md             # Statistical findings
├── step4_patterns/
│   ├── patterns.json          # Discovered patterns (25+ patterns)
│   └── summary.md             # Pattern descriptions
├── step5_insights/
│   ├── insights.json          # All insights with ISGEN scores
│   └── insight_*.png          # Visualizations (26+ charts)
├── ifq_format/               # ⭐ IFQ-compatible output (auto-generated)
│   ├── insight_cards.json     # InsightCards with (Question, Reason, Breakdown, Measure)
│   └── insights.json          # Insights with (B, M, S, P, score, view_labels, view_values)
└── summary/
    └── summary.txt            # Overall summary with ISGEN metrics
```

**Note**: The `ifq_format/` directory is automatically generated at the end of the pipeline, converting baseline insights to IFQ-compatible format for fair comparison.

## 📁 File Structure

```
baseline/
├── __init__.py          # Package initialization
├── agent.py             # Core 5-step agentic workflow
├── scorer.py            # ISGEN scoring functions
├── output_converter.py  # Converts output to IFQ-compatible format
├── run.py               # Main entry point
└── README.md            # This file
```

## 🔍 Architecture: Expert-Driven Agentic Workflow

### Core Philosophy

**LLM as Expert Analyst, Not Code Generator**

Instead of having LLM write Python code that may fail, the LLM directly acts as domain experts:
- **Data Profiling Expert** - infers semantic meaning from data samples
- **Quality Analyst** - assesses data quality issues and impacts
- **Statistician** - interprets distributions and correlations
- **Pattern Recognition Expert** - discovers temporal, correlation, grouping, and anomaly patterns
- **Insight Specialist** - extracts actionable insights

### 5-Step Agentic Pipeline

#### **Step 1: Data Profiling Agent** 🔍

**Phase 1: Initial Exploration**
- Loads data and examines structure
- Identifies numerical vs categorical columns
- Counts missing values

**Phase 2: Semantic Analysis** 🧠
- LLM analyzes sample values from each column
- Infers semantic meaning (e.g., "customer age", "transaction date")
- Classifies data types (ID, Categorical, Numerical, Temporal, Text)
- Assigns importance levels (high/medium/low)

**Phase 3: Comprehensive Profiling**
- Combines structural + semantic analysis
- Computes statistics for each column
- Generates human-readable summary

**Output:** `profile.json` with semantic meanings + `summary.md`

---

#### **Step 2: Quality Analysis Agent** 📊

**Phase 1: Compute Quality Metrics**
- Missing values analysis
- Outlier detection (IQR method)
- Duplicate detection

**Phase 2: Expert Quality Assessment** 🧠
- LLM interprets quality metrics
- Identifies critical issues
- Assesses impact on analysis
- Provides recommendations
- Assigns quality score (0-100)

**Output:** `quality_report.json` with expert assessment + `summary.md`

---

#### **Step 3: Statistical Analysis Agent** 📈

**Phase 1: Compute Comprehensive Statistics**
- Descriptive statistics (mean, median, std, quartiles)
- Distribution analysis (skewness, kurtosis)
- Correlation analysis (strong correlations >0.7)

**Phase 2: Statistical Interpretation** 🧠
- LLM interprets distributions
- Explains correlation meanings
- Identifies statistical anomalies
- Provides recommendations

**Output:** `statistics.json` with interpretation + `summary.md`

---

#### **Step 4: Pattern Discovery Agent** 🔎

**Multi-Prompt Strategy** - 4 specialized prompts:

1. **Temporal Patterns** - trends, seasonality, cycles
2. **Correlation Patterns** - strong relationships between variables
3. **Grouping Patterns** - natural clusters and segments
4. **Anomaly Patterns** - unusual behaviors and outliers

For each category:
- LLM analyzes data structure
- Discovers specific, concrete patterns
- Provides evidence and business relevance
- Assigns strength (strong/moderate/weak)

**Output:** `patterns.json` with 25+ patterns + `summary.md`

---

#### **Step 5: Insight Extraction Agent** 💡

**Iterative Generation Strategy** (like IFQ):

1. **Multi-Prompt Extraction** - 5 insight batches:
   - **TREND** - temporal trends and directional changes
   - **OUTLIER, ANOMALY** - unusual values
   - **CORRELATION** - relationships between variables
   - **DISTRIBUTION, COMPARISON** - distributions and group comparisons
   - **PATTERN** - recurring patterns and cycles

2. **ISGEN Scoring & Filtering**:
   - Each insight scored using ISGEN patterns
   - Only insights **passing threshold** are kept
   - Failed insights are discarded (charts deleted)

3. **Iterative Refinement** (if needed):
   - If < 15 insights pass threshold → generate more
   - LLM generates **different** insights (avoids duplicates)
   - Max 3 iterations to prevent infinite loops

**Output:** `insights.json` with 15+ high-quality insights passing ISGEN threshold

---

### Key Advantages

✅ **No Code Execution Failures** - LLM analyzes directly, no generated code to fail
✅ **Deep Semantic Understanding** - LLM infers meaning from data samples
✅ **Expert-Level Analysis** - Each step acts as domain specialist
✅ **Comprehensive Coverage** - Multi-prompt strategy ensures thorough analysis
✅ **Verbose Logging** - Shows what agent is thinking and doing
✅ **Reproducible** - Structured output format for comparison

## 📈 Example Output

### summary/summary.txt

```
======================================================================
AGENTIC AUTOEDA BASELINE - SUMMARY
======================================================================

Total Insights: 26
Passed ISGEN Threshold: 13/26 (50.0%)
Average Pattern Score: 0.500

Insights by Type:
  • TREND: 5
  • CORRELATION: 5
  • PATTERN: 5
  • ANOMALY: 3
  • DISTRIBUTION: 3
  • COMPARISON: 3
  • OUTLIER: 2

Insights by ISGEN Pattern:
  • QUALITY: 13
  • None: 13

Top 10 Insights:
  1. ✓ insight_011: High correlation between advertising spend and sales revenue
     Pattern: QUALITY, Score: 1.000
  2. ✓ insight_012: Inverse correlation between customer complaints and satisfaction
     Pattern: QUALITY, Score: 1.000
  ...
======================================================================
```

### step1_profiling/profile.json

```json
{
  "dataset_overview": {
    "shape": {"rows": 1036, "columns": 56},
    "total_columns": 56,
    "numerical_columns": 23,
    "categorical_columns": 32
  },
  "columns": {
    "Phân loại": {
      "dtype": "str",
      "missing_percentage": 0.0,
      "semantic_meaning": "Classification of items or products",
      "data_type_class": "Categorical",
      "importance": "medium",
      "unique_count": 5,
      "top_values": {"1": 876, "2": 77, "1A": 62}
    },
    "Khối lượng": {
      "dtype": "float64",
      "missing_percentage": 0.0,
      "semantic_meaning": "Weight of the item",
      "data_type_class": "Numerical",
      "importance": "high",
      "statistics": {
        "min": 0.5, "max": 1500.0,
        "mean": 125.3, "median": 98.2
      }
    }
  }
}
```

### step4_patterns/patterns.json

```json
{
  "pattern_categories": [
    "Temporal Patterns",
    "Correlation Patterns",
    "Grouping Patterns",
    "Anomaly Patterns"
  ],
  "total_patterns": 25,
  "patterns_by_category": {
    "Temporal Patterns": [
      {
        "pattern_name": "Monthly Sales Seasonality",
        "description": "Sales show strong seasonal pattern...",
        "variables_involved": ["Ngày bán", "Thành Tiền"],
        "evidence": "Peak in Q4, low in Q2",
        "strength": "strong",
        "business_relevance": "Inventory planning for seasonal demand"
      }
    ]
  }
}
```

### step5_insights/insights.json

```json
[
  {
    "insight_id": "insight_001",
    "title": "Increase in Monthly Sales Over the Last Year",
    "description": "Sales revenue shows consistent upward trend...",
    "insight_type": "TREND",
    "chart_path": "output/step5_insights/insight_001.png",
    "data_evidence": {
      "source_step": "step3_statistics",
      "key_statistics": "15% YoY growth"
    },
    "score": {
      "pattern_type": "QUALITY",
      "pattern_score": 1.0,
      "threshold": 0.6,
      "passed": true
    },
    "variables": ["Ngày bán", "Thành Tiền"]
  }
]
```

## 🎨 Customization

### Change LLM Model

```bash
# In .env
MODEL=gpt-4o  # Use more powerful model for better analysis
```

### Adjust Max Iterations

```python
# In run.py
agent.run_autoeda(output_dir='output', max_iterations=5)  # Default: 3
```

### Modify Pattern Categories

Edit `agent.py`, `_run_pattern_agent()`:

```python
pattern_categories = [
    {'name': 'Temporal Patterns', 'focus': 'time-based trends, seasonality, cycles'},
    {'name': 'Your Custom Pattern', 'focus': 'your focus area'},
    # Add more categories
]
```

### Adjust ISGEN Scoring Thresholds

Edit `scorer.py`:

```python
# Example: Make TREND scoring more strict
score['threshold'] = 0.98  # Instead of 0.95
```

### Adjust Insight Generation Parameters

Edit `agent.py`, `_run_insight_agent()`:

```python
# Change minimum insights passing threshold
def _run_insight_agent(self, output_dir: str, min_insights: int = 20, max_iterations: int = 5):
    # min_insights: Target number of passing insights (default: 15)
    # max_iterations: Max iterations to avoid infinite loop (default: 3)
```

### Change Insight Extraction Strategy

Edit `agent.py`, `_run_insight_agent()`:

```python
insight_categories = [
    {'types': ['TREND'], 'focus': 'temporal trends and directional changes'},
    {'types': ['YOUR_TYPE'], 'focus': 'your custom focus'},
    # Modify or add categories
]
```

## 🔄 IFQ-Compatible Output

The baseline automatically generates IFQ-compatible output for fair comparison:

### Automatic Conversion

After the 5-step pipeline completes, the baseline automatically converts its output to IFQ format:

```
output/ifq_format/
├── insight_cards.json    # InsightCards: (Question, Reason, Breakdown, Measure)
└── insights.json         # Insights: (B, M, S, P, score, view_labels, view_values)
```

### Output Format

**InsightCards** (backward-mapped from insights):
```json
{
  "question": "How does X change over Y?",
  "reason": "Understanding this helps...",
  "breakdown": "CategoryColumn",
  "measure": "MEAN(NumericColumn)"
}
```

**Insights** (IFQ-compatible):
```json
{
  "breakdown": "CategoryColumn",
  "measure": "MEAN(NumericColumn)",
  "subspace": [],
  "pattern": "Trend",
  "score": 0.85,
  "question": "How does X change over Y?",
  "reason": "Explanation...",
  "view_labels": ["A", "B", "C"],
  "view_values": [10.5, 20.3, 15.7]
}
```

### Manual Conversion

If you need to convert existing baseline output:

```bash
python output_converter.py \
  --data ../../data/your_data.csv \
  --insights output/step5_insights/insights.json \
  --output output/ifq_format
```

### Key Differences from IFQ

| Aspect | IFQ | Baseline |
|--------|------|----------|
| **Methodology** | Statistical search (QUGEN + ISGEN) | Expert-driven LLM analysis |
| **Questions** | Generated first (QUGEN) | Backward-mapped from insights |
| **Subspace (S)** | Beam search exploration | Empty (no subspace) |
| **Patterns** | 4 types (Trend, Outstanding, Attribution, Distribution) | Same 4 types |
| **Scoring** | ISGEN scoring | Same ISGEN scoring |
| **Output Format** | (B, M, S, P) | Converted to (B, M, S, P) |

**Note**: Baseline doesn't explore subspaces (S = ∅), which is expected - this is a key differentiator showing IFQ's advantage in conditional pattern discovery.

## 📊 Comparison with IFQ

To compare this baseline with IFQ:

1. **Run baseline:**
   ```bash
   python run.py ../../data/your_data.csv output
   ```

2. **Run IFQ** on same dataset

3. **Compare using evaluation metrics:**
   - Insight Yield: `|I| / |Q|`
   - Average Score: Mean ISGEN scores
   - Redundancy: Unique (B, M, S, P) tuples
   - Schema Coverage: Columns explored
   - Pattern Coverage: Pattern types found
   - **Subspace Exploration**: Baseline = 0, IFQ > 0 ⭐
   - Question Diversity: Semantic similarity
   - Downstream ML: Feature engineering performance

See `../../EVALUATION_METRICS.md` for detailed metric definitions.

## 🐛 Troubleshooting

### Semantic analysis returns empty

- Check OpenAI API key is valid
- Increase `max_tokens` in semantic analysis (currently 8000)
- Reduce number of columns analyzed (currently first 30)

### Few patterns discovered

- Use more capable model (gpt-4o instead of gpt-4o-mini)
- Adjust `temperature` parameter (currently 0.5 for pattern discovery)
- Modify pattern category prompts to be more specific

### Low ISGEN pass rates

- Review scoring thresholds in `scorer.py`
- Check if data has sufficient signal for patterns
- Verify numerical values are being extracted correctly

### Charts not generating

- Check variable names match dataset columns exactly
- Ensure data types are compatible (numerical for trends, etc.)
- Review error messages in console output

### LLM API errors

- Check API rate limits
- Verify API key has sufficient credits
- Reduce `max_tokens` if hitting context limits

## 📚 Dependencies

Core dependencies (from `../requirements.txt`):

```
pandas>=2.0.0
numpy>=1.24.0
openai>=1.0.0
python-dotenv>=1.0.0
pymannkendall>=1.4.3
matplotlib>=3.7.0
scipy>=1.10.0
```

## 🔗 References

- **ISGEN Paper**: Insight generation methodology and scoring functions
- **OpenAI API**: LLM for insight extraction
- **Mann-Kendall Test**: Trend detection (via pymannkendall)

## 📝 Notes

- This is a **baseline implementation** for comparison purposes
- Designed to be simple, reproducible, and well-documented
- UTF-8 encoding ensures Vietnamese text displays correctly
- All outputs are JSON-serializable for easy integration

## 🚀 Integration

To integrate this baseline into another project:

```python
from baseline.auto_eda_agent.agent import AgenticAutoEDA

# Initialize agent
agent = AgenticAutoEDA(
    data_path='data/your_data.csv',
    model='gpt-4o-mini',  # or 'gpt-4o'
    api_key='your-api-key'
)

# Run complete workflow
results = agent.run_autoeda(
    output_dir='output',
    max_iterations=3
)

# Access step outputs
profile = results['step1']  # Data profile
quality = results['step2']  # Quality report
statistics = results['step3']  # Statistical analysis
patterns = results['step4']  # Discovered patterns
insights = results['step5']  # Extracted insights
```

## 📊 Methodology Notes

### Why Expert-Driven Instead of Code Generation?

**Problems with Code Generation Approach:**
- LLM-generated code often fails (syntax errors, wrong APIs, path issues)
- Requires multiple iterations and fallback mechanisms
- Limited by LLM's coding ability, not analytical ability
- Hard to debug and maintain

**Advantages of Expert-Driven Approach:**
- ✅ LLM uses its full analytical capability
- ✅ No code execution failures
- ✅ Deeper semantic understanding
- ✅ More reliable and reproducible
- ✅ Direct access to data through pandas

### Multi-Prompt Strategy

Each complex task (pattern discovery, insight extraction) is broken into multiple specialized prompts:
- **Better coverage** - each prompt focuses on specific pattern type
- **Higher quality** - specialized prompts produce better results
- **More insights** - 4-5 prompts extract more than single prompt
- **Easier to debug** - can improve individual prompts independently

### Semantic Analysis Innovation

Step 1 samples unique values from each column and asks LLM to infer meaning:
- Goes beyond `.describe()` statistics
- Understands business context (e.g., "customer age" vs "product code")
- Assigns importance levels for downstream analysis
- Detects data quality issues early

This semantic understanding flows through all subsequent steps, enabling more relevant pattern discovery and insight extraction.
