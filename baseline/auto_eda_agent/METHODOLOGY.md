# Expert-Driven Agentic AutoEDA: Methodology Report

**Version:** 1.0  
**Date:** April 2026  
**Model:** gpt-5.4 (OpenAI)

---

## Abstract

This report describes an LLM-based AutoEDA pipeline that positions large language models as domain specialists rather than code generators. The system performs exploratory data analysis through five sequential agents — data profiling, quality assessment, statistical analysis, pattern discovery, and insight extraction. Each agent receives the accumulated outputs of all prior agents as context, ensuring that later stages build on earlier findings rather than operating independently. The pipeline produces a structured set of insights covering trends, correlations, distributions, anomalies, and grouping patterns, along with supporting visualizations.

---

## 1. Introduction

Exploratory data analysis is a critical early step in any data science workflow, but it is time-consuming and requires expertise across multiple domains: data quality assessment, statistical interpretation, and business context. Automated EDA (AutoEDA) systems aim to reduce this burden by programmatically generating insights from raw data.

Most AutoEDA approaches either rely on fixed statistical templates (e.g., `pandas-profiling`) or ask LLMs to generate and execute code. Template-based systems lack semantic understanding; code-generation systems are fragile and require extensive error handling.

This system takes a different approach: LLMs act as specialist analysts who interpret pre-computed statistics and evidence, rather than generating code or operating on column names alone. All aggregations and statistics are computed programmatically; the LLM's role is to reason over these numbers and extract meaning.

---

## 2. System Overview

The pipeline consists of five sequential agents. Each agent writes its output to a JSON file and passes it to the next agent via an accumulated context object. The cleaned dataframe is available to all agents throughout.

```
Raw CSV
  │
  ▼
[Preprocessing]
  Normalize currency, percentage, and date formats → cleaned df
  │
  ├──▶ Step 1: Data Profiling Agent
  │         Input:  df
  │         Output: profile.json
  │
  ├──▶ Step 2: Quality Analysis Agent
  │         Input:  df + profile.json
  │         Output: quality_report.json
  │
  ├──▶ Step 3: Statistical Analysis Agent
  │         Input:  df + profile.json + quality_report.json
  │         Output: statistics.json
  │
  ├──▶ Step 4: Pattern Discovery Agent
  │         Input:  df + profile.json + quality_report.json + statistics.json
  │         Output: patterns.json
  │
  └──▶ Step 5: Insight Extraction Agent
            Input:  df + all prior outputs
            Output: insights.json + charts
```

---

## 3. Preprocessing

Before any agent runs, the dataset is cleaned to ensure consistent numeric types. The cleaning logic mirrors the QUIS preprocessing pipeline to ensure a fair comparison between the two systems:

- **Separator detection** → auto-detects `,` vs `;` CSV formats
- **Currency strings** (`$50.00`, `$1,200`) → parsed to float
- **Percentage strings** (`35%`) → parsed to float
- **European number formatting** → normalized when `;` separator is detected

This step runs once on load. All agents operate on the cleaned dataframe.

---

## 4. Pipeline

### Step 1: Data Profiling Agent

**Objective:** Understand dataset structure and infer the semantic meaning of each column.

**Process:**

The agent first computes structural metadata for each column: data type, missing value count, and either descriptive statistics (for numerical columns) or value frequency distributions (for categorical columns).

Sample values from each column are then passed to the LLM, which infers:

- `semantic_meaning` — business interpretation of the column (e.g., "gross revenue per transaction")
- `data_type_class` — one of: ID, Categorical, Numerical, Temporal, Text
- `importance` — high, medium, or low relevance for analysis
- `potential_issues` — quality concerns visible from samples

**Output:** `profile.json` — one entry per column containing dtype, missing rate, semantic meaning, data type class, importance level, and statistics or top values.

---

### Step 2: Quality Analysis Agent

**Objective:** Assess data quality with awareness of column semantics from Step 1.

**Process:**

The agent computes three quality metrics directly from the dataframe:

- **Missing values** — count and percentage per column
- **Outliers** — IQR method per numerical column, excluding columns identified as ID type in Step 1, since IQR-based outlier detection is not meaningful for identifier fields
- **Duplicates** — exact row duplicate count

The LLM then receives these metrics along with the importance levels from Step 1, and produces a quality assessment that weights issues by column importance — a quality issue in a high-importance column is flagged as more critical than the same issue in a low-importance column.

**Output:** `quality_report.json` — quality metrics, severity-weighted critical issues, recommended actions, and an overall quality score (0–100).

---

### Step 3: Statistical Analysis Agent

**Objective:** Compute and interpret statistical properties of the dataset.

**Process:**

The agent computes directly from the dataframe:

- **Numerical columns:** mean, median, standard deviation, min, max, quartiles, skewness, kurtosis
- **Categorical columns:** unique count, most frequent value, top-10 value distribution
- **Correlations:** Pearson correlation matrix across all numerical columns; pairs with |r| > 0.7 are extracted as strong correlations

The LLM receives these statistics together with semantic meanings from Step 1 and quality flags from Step 2. This context prevents common misinterpretations — for example, avoiding treating identifier columns as continuous variables, or interpreting means without noting that they may be inflated by flagged outliers.

**Output:** `statistics.json` — raw statistics, strong correlation pairs with r values, and LLM interpretation of distributions, correlations, key findings, and anomalies.

---

### Step 4: Pattern Discovery Agent

**Objective:** Discover patterns grounded in computed evidence.

**Process:**

Before calling the LLM, the agent pre-computes aggregations from the dataframe:

- **Group aggregations:** total and mean of key numerical columns grouped by each categorical column
- **Temporal aggregations:** if a Temporal column was identified in Step 1, monthly totals are computed for key numerical columns

These computed aggregations, along with the strong correlation pairs from Step 3, are passed directly into the LLM prompt as evidence. The LLM identifies patterns within these numbers rather than speculating from column names alone.

Four pattern categories are analyzed with separate prompts:

| Category | Evidence Provided |
|---|---|
| Temporal Patterns | Monthly aggregations |
| Correlation Patterns | Pearson r pairs from Step 3 |
| Grouping Patterns | Groupby aggregations |
| Anomaly Patterns | Outlier flags from Step 2, distribution stats from Step 3 |

**Output:** `patterns.json` — patterns grouped by category, each with a name, description, involved variables, supporting evidence with specific numbers, and assessed strength.

---

### Step 5: Insight Extraction Agent

**Objective:** Extract structured, visualizable insights by synthesizing all prior analysis.

**Process:**

The agent loads all four prior outputs and constructs a unified context for the LLM:

- Semantic meanings and importance levels from Step 1
- Quality score and critical issues from Step 2
- Key statistical findings and strong correlations from Step 3
- Discovered patterns from Step 4
- Top 10 unique values for each categorical column (for subspace generation guidance)

Insights are extracted in five batches, each targeting a specific insight type:

| Batch | Insight Types |
|---|---|
| 1 | TREND |
| 2 | OUTLIER, ANOMALY |
| 3 | CORRELATION |
| 4 | DISTRIBUTION, COMPARISON |
| 5 | PATTERN |

**Subspace Generation:**

The LLM is instructed to optionally generate subspace conditions (filtering criteria) for insights. Subspaces are data segments defined by column-value pairs (e.g., `[["Sales Method", "Online"]]`). The subspace generation follows these principles:

- **Evidence-based**: Subspaces should be grounded in statistical comparisons from Step 3 and pattern aggregations from Step 4
- **Diverse columns**: Use diverse categorical columns across different insights to explore multiple segments
- **Conditional inclusion**: Only add subspace when the insight is significantly stronger or more specific with subspace than without
- **Categorical guidance**: Top 10 unique values per categorical column are provided to inform subspace selection

Each insight includes a title, description with specific numbers, the variables involved, the source evidence, and optionally a subspace condition. A chart is generated for each insight matched to its type: line plot for trends, scatter plot for correlations, histogram for distributions, bar chart for comparisons and groupings, and box plot for outliers and anomalies.

**Post-processing:** After the LLM returns each batch of insights, every insight undergoes automated validation before being accepted. If a subspace condition is specified, the system verifies that the referenced column and value actually exist in the data; insights that fail this check are discarded. For accepted insights, the sorted unique values of the breakdown column under the subspace filter are computed and attached as `view_labels`, ensuring that labels always reflect the actual filtered data.

**Deduplication:** Two layers of deduplication are applied across all batches. First, insights with repeated titles are skipped. Second, insights sharing the same structural combination of type, breakdown column, measure column, and subspace condition are also skipped even if their titles differ. This prevents both surface-level and structural redundancy across extraction batches.

**Output:** `insights.json` — structured list of insights, each with title, description, type, variables involved, evidence, chart path, subspace condition, and `view_labels`.

After Step 5 completes, the pipeline produces an QUIS-compatible output (insight cards and insight summaries) to enable direct evaluation against the QUIS system.

---

## 5. Configuration

| Parameter | Value |
|---|---|
| Model | gpt-5.4 |
| Temperature (Steps 1–3) | 0.3 |
| Temperature (Steps 4–5) | 0.5 |
| Insight types | TREND, OUTLIER, ANOMALY, CORRELATION, DISTRIBUTION, COMPARISON, PATTERN |
| Strong correlation threshold | \|r\| > 0.7 |
| Outlier detection method | IQR (Q1 − 1.5×IQR, Q3 + 1.5×IQR) |
| Max columns for profiling | 30 |

---

## 6. Limitations

- **LLM dependency:** interpretation quality depends on model capability; outputs are not fully deterministic
- **No causal inference:** correlations and patterns are observational only
- **Column limit:** semantic analysis covers the first 30 columns; wider datasets are truncated
- **No hypothesis testing:** statistical significance is not formally tested
- **Reproducibility:** temperature > 0 produces variation between runs; set temperature = 0 for reproducible benchmarks

---

## Appendix: System Requirements

**Python:** 3.8+  
**Dependencies:** `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `openai`, `python-dotenv`  
**Hardware:** 4 GB RAM minimum  
**Network:** Required for OpenAI API access  
**Estimated runtime:** 3–7 minutes depending on dataset size and API latency