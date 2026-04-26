# ED Agent — Prompt Templates

**Model:** gpt-5.4  
**Date:** April 2026

---

## Step 1: Data Profiling Agent

### System Prompt

```
You are an expert data analyst inferring semantic meaning from data samples.
```

### User Prompt

```
You are an expert data analyst. Your job is to infer the semantic meaning and classification of dataset columns from their names and sample values.

Analyze the following dataset columns and infer their semantic meaning.

Dataset: {n_rows} rows × {n_columns} columns

Column samples (name, dtype, and unique values):
{column_samples_json}

For EACH column, return:
- semantic_meaning: what this column represents in business terms (e.g., "gross revenue per transaction", "date of sale")
- data_type_class: one of ID | Categorical | Numerical | Temporal | Text
- importance: one of high | medium | low
- potential_issues: any quality concerns visible from the sample values (e.g., mixed formats, suspicious values, likely nulls)

Return a JSON object where each key is a column name:

{
  "column_name": {
    "semantic_meaning": "...",
    "data_type_class": "ID|Categorical|Numerical|Temporal|Text",
    "importance": "high|medium|low",
    "potential_issues": "..."
  }
}
```

**API params:** `temperature=0.3`, `max_completion_tokens=8000`, `response_format=json_object`

---

## Step 2: Quality Analysis Agent

### System Prompt

```
You are a data quality expert providing professional assessment.
```

### User Prompt

```
Assess the data quality of the following dataset.

Column importance levels (from profiling):
{importance_by_column_json}

Note: The following columns are identifier fields and have been excluded from outlier analysis:
{id_columns}

Computed quality metrics:
{quality_metrics_json}

For each issue found, provide:
1. A description of the issue
2. Severity: high | medium | low — weighted by the importance of the affected column
3. Business impact: how this issue affects downstream analysis
4. Recommended action

Also provide:
- overall_quality_score: integer 0–100 reflecting overall dataset reliability
- priority_actions: top 3 actions to address the most critical issues

Return JSON:

{
  "critical_issues": [
    {
      "issue": "...",
      "severity": "high|medium|low",
      "impact": "...",
      "recommendation": "..."
    }
  ],
  "overall_quality_score": 0,
  "priority_actions": ["...", "...", "..."],
  "detailed_analysis": "..."
}
```

**API params:** `temperature=0.3`, `max_completion_tokens=4000`, `response_format=json_object`

---

## Step 3: Statistical Analysis Agent

### System Prompt

```
You are an expert statistician interpreting data.
```

### User Prompt

```
Interpret the following statistical findings for this dataset.

Column semantic meanings (from Step 1):
{semantic_meanings_json}

Data quality context (from Step 2):
- Overall quality score: {quality_score}
- Columns with significant outliers: {outlier_columns}
  When interpreting means and distributions for these columns, note that summary statistics may be influenced by outliers.
- Columns flagged as identifiers (exclude from statistical interpretation): {id_columns}

Computed statistics:
{statistics_json}

Provide:
1. distribution_patterns: interpret the shape of each numerical distribution (skewness, kurtosis, mean vs median gaps) in business terms
2. strong_correlations: for each pair with |r| > 0.7, explain what the relationship means and whether it is likely structural or behavioral
3. key_findings: top 3 most important statistical observations
4. statistical_anomalies: unusual patterns that warrant further investigation
5. recommendations: suggested follow-up analyses

Return JSON:

{
  "distribution_patterns": "...",
  "strong_correlations": [
    {
      "variables": "var1 and var2",
      "interpretation": "...",
      "strength": "strong|moderate|weak"
    }
  ],
  "key_findings": ["...", "...", "..."],
  "statistical_anomalies": ["...", "..."],
  "recommendations": ["...", "..."]
}
```

**API params:** `temperature=0.3`, `max_completion_tokens=4000`, `response_format=json_object`

---

## Step 4: Pattern Discovery Agent

Four separate prompts are used, one per pattern category. The same system prompt applies to all four.

### System Prompt

```
You are a pattern recognition expert. Your job is to identify concrete, evidence-backed patterns in data. You must only report patterns that are directly supported by the numbers provided. Do not speculate or infer patterns beyond what the evidence shows.
```

### User Prompt — Temporal Patterns

```
Discover temporal patterns in this dataset.

Focus: time-based trends, seasonality, growth or decline over time, cyclical behavior.

Computed monthly aggregations:
{monthly_aggregations_json}

Column semantic meanings:
{semantic_meanings_json}

Data quality score: {quality_score}

For each pattern found:
- Cite specific numbers from the monthly aggregations above
- State which months or periods show the pattern
- Assess pattern strength: strong | moderate | weak

Return JSON:

{
  "patterns": [
    {
      "pattern_name": "...",
      "description": "...",
      "variables_involved": ["..."],
      "evidence": "... (include specific numbers)",
      "strength": "strong|moderate|weak",
      "business_relevance": "..."
    }
  ]
}
```

### User Prompt — Correlation Patterns

```
Discover correlation patterns in this dataset.

Focus: strong relationships between variables, co-movement, potential dependencies.

Strong correlations computed from data (|r| > 0.7):
{strong_correlations_json}

Column semantic meanings:
{semantic_meanings_json}

Statistical interpretation from Step 3:
{correlation_interpretation}

For each pattern found:
- Reference the specific r value
- Explain the direction and likely business meaning of the relationship
- Note whether the correlation may be structural (e.g., one variable derived from another) or behavioral

Return JSON:

{
  "patterns": [
    {
      "pattern_name": "...",
      "description": "...",
      "variables_involved": ["..."],
      "evidence": "... (include r value and direction)",
      "strength": "strong|moderate|weak",
      "business_relevance": "..."
    }
  ]
}
```

### User Prompt — Grouping Patterns

```
Discover grouping patterns in this dataset.

Focus: differences between segments, dominant groups, uneven distributions across categories.

Computed group aggregations:
{group_aggregations_json}

Column semantic meanings:
{semantic_meanings_json}

For each pattern found:
- Cite specific group values from the aggregations above
- Compare groups directly where relevant (e.g., "Group A is 3× Group B")
- Assess whether the difference is meaningful for business decisions

Return JSON:

{
  "patterns": [
    {
      "pattern_name": "...",
      "description": "...",
      "variables_involved": ["..."],
      "evidence": "... (include specific group values)",
      "strength": "strong|moderate|weak",
      "business_relevance": "..."
    }
  ]
}
```

### User Prompt — Anomaly Patterns

```
Discover anomaly patterns in this dataset.

Focus: unusual values, outliers, spikes, unexpected distributions, zero-inflation.

Outlier flags from Step 2:
{outlier_flags_json}

Distribution statistics from Step 3:
{distribution_stats_json}

Column semantic meanings:
{semantic_meanings_json}

For each anomaly found:
- Cite specific statistics (e.g., mean vs median gap, outlier count, min/max)
- Assess whether the anomaly is likely a data quality issue or a real business event
- Suggest how it should be handled in downstream analysis

Return JSON:

{
  "patterns": [
    {
      "pattern_name": "...",
      "description": "...",
      "variables_involved": ["..."],
      "evidence": "... (include specific statistics)",
      "strength": "strong|moderate|weak",
      "business_relevance": "..."
    }
  ]
}
```

**API params (all 4 categories):** `temperature=0.5`, `max_completion_tokens=8000`, `response_format=json_object`

---

## Step 5: Insight Extraction Agent

Five batches, one prompt per batch. The same system prompt applies to all five.

> **Pipeline note**: The LLM output from this step does NOT include `view_labels`.
> Labels are computed by post-processing code (`_compute_view_labels`) after the LLM responds:
> for each insight, apply its `subspace` filter to `df`, then extract
> sorted unique values of the `breakdown` column from the filtered dataframe.
> This ensures labels always match the subspace-filtered data and pass faithfulness checks.

> **Deduplication note**: Two layers of dedup are applied:
> 1. **Post-hoc (global)**: `used_struct_keys` set tracks `(type, breakdown, measure, subspace)` across all categories. Insights with duplicate structural keys are silently dropped before saving.
> 2. **Pre-emptive (per-category via prompt)**: `used_struct_keys_for_category` is passed into the prompt as an exclusion list so the LLM does not generate structural combinations already extracted in the same category during a previous iteration.

### System Prompt

```
You are an expert data analyst extracting insights for a business audience.
```

### User Prompt Template (used for all 5 batches)

```
Extract insights of the following type(s): {insight_types}

AVAILABLE COLUMNS — use ONLY these exact names in "variables" and "subspace":
- Numerical: {numerical_columns}
- Categorical: {categorical_columns}

CRITICAL: Do NOT use derived or computed column names (e.g., "month", "year", "quarter", "day").
If a temporal insight is needed, use the original date column name (e.g., "Invoice Date").
Even if a "month" column exists in the dataframe, DO NOT use it. Always use the original date column.

VALID SUBSPACE VALUES — when using subspace, the value MUST be taken from this list exactly as written:
{categorical_values_json}

Do NOT invent subspace values. Only use values that appear in the list above.

BREAKDOWN SELECTION RULES — for TREND, ATTRIBUTION, DISTRIBUTION_DIFFERENCE:
- The FIRST variable in "variables" is the breakdown column (grouping dimension)
- Breakdown MUST be a CATEGORICAL or TEMPORAL or ID column (from the categorical columns list above)
- DO NOT use numerical columns as breakdown for these patterns
- Example: Use "Retailer" or "Invoice Date" as breakdown, NOT "Total Sales" or "Units Sold"
- OUTSTANDING_VALUE can use any column as breakdown (it groups by breakdown to find outliers)

Context from prior analysis steps:

Step 1 — Column meanings:
{semantic_meanings_json}

Step 2 — Quality Assessment:
- Overall quality score: {quality_score}
- Critical issues: {critical_issues}

Step 3 — Statistical Analysis:
- Key statistical findings: {statistical_findings_json}
- Strong correlations: {strong_correlations_json}

Step 4 — Discovered patterns (relevant to {insight_types}):
{relevant_patterns}

IMPORTANT: These (breakdown, measure, subspace) combinations are already covered for this category — do NOT repeat them:
{used_struct_keys_for_category}

Generate insights with DIFFERENT breakdown/measure/subspace combinations.

Already extracted insights (do not repeat these):
{used_titles}

Subspace rules:
- Use subspace only when the insight is specifically about a subset of data
- Subspace MUST use a categorical column (from the categorical columns list above)
- Subspace value must be an actual value that exists in that column
- Each insight uses at most ONE subspace condition: [["column_name", "value"]]
- Do NOT use numerical columns, date columns, or derived columns as subspace
- REQUIRED: At least 1 or 2 insights in your response MUST have a non-empty subspace (pick the insights that are most naturally segment-specific)

For each insight:
- Write a specific, concrete title
- Include actual numbers in the description
- Reference which step provided the evidence
- List the columns involved (from available columns only)
- Choose an appropriate chart type: line | bar | scatter | histogram | box

Return JSON:

{
  "insights": [
    {
      "title": "...",
      "description": "... (include specific numbers)",
      "type": "{insight_types}",
      "variables": ["column_name_1", "column_name_2"],
      "evidence": {
        "source_step": "step3_statistics|step4_patterns|step2_quality",
        "key_statistics": "...",
        "data_points": "..."
      },
      "chart_type": "line|bar|scatter|histogram|box",
      "subspace": [["CategoryColumn", "CategoryValue"]]  // or [] for global insights
    }
  ]
}

Extract as many valuable insights as possible.
```

**API params:** `temperature=0.5`, `max_completion_tokens=16000`, `response_format=json_object`

### Batch Mapping

| Batch | insight_types | relevant_patterns source |
|---|---|---|
| 1 | TREND | Temporal Patterns from Step 4 |
| 2 | OUTLIER, ANOMALY | Anomaly Patterns from Step 4 |
| 3 | CORRELATION | Correlation Patterns from Step 4 |
| 4 | DISTRIBUTION, COMPARISON | Grouping Patterns from Step 4 |
| 5 | PATTERN | All pattern categories from Step 4 |

---

## Post-processing: view_labels Computation (Pipeline Code)

> This is not a prompt — it is the pipeline logic that runs after Step 5 LLM output (`_compute_view_labels` in `agent.py`).

```
For each insight generated by Step 5:

1. Read insight["subspace"] — e.g., [["Sales Method", "Online"]]

2. Validate subspace (if not empty):
   - Check that subspace column exists in df.columns
     → If not: drop insight, log "invalid subspace column"
   - Check that subspace value exists in df[col].unique()
     → If not: drop insight, log "subspace value not found in data"
     → This catches cases where LLM invented a value (e.g., Region = "A")

3. Apply subspace filter:
   - If subspace is empty ([]):       filtered_df = df
   - If subspace is [[col, val]]:     filtered_df = df[df[col] == val]

4. Validate breakdown column:
   - Read breakdown column from insight["variables"][0]
   - Check that it exists in filtered_df.columns
     → If not: drop insight, log "breakdown column not found"

5. Compute view_labels:
   view_labels = sorted(filtered_df[breakdown_col].dropna().unique().tolist())
   - If view_labels is empty: drop insight, log "filtered dataframe is empty"

6. Attach view_labels to the insight before passing to faithfulness check

This guarantees view_labels are always derived from the same filtered data
that the faithfulness verifier uses, eliminating the label mismatch issue.
```

---

## Post-processing: Deduplication (Pipeline Code)

> This is not a prompt — it is the pipeline logic in `_run_insight_agent` in `agent.py`.

```
Two layers of deduplication are applied after each batch is returned from the LLM:

Layer 1 — Structural dedup (global, post-hoc):
  For each insight in the LLM response:
    variables = insight["variables"]
    subspace = insight["subspace"]
    breakdown = variables[0] if variables else ''
    measure = variables[1] if len(variables) > 1 else ''
    struct_key = (insight["type"], breakdown, measure, tuple(subspace))

    if struct_key in used_struct_keys:
        → skip (silent drop)
    else:
        used_struct_keys.add(struct_key)
        → accept insight

Layer 2 — Title dedup (global, post-hoc):
    if insight["title"] in used_titles:
        → skip (silent drop)
    else:
        used_titles.add(insight["title"])

Layer 3 — Per-category pre-emptive (via prompt):
    After each accepted insight, add its struct_key to category_struct_keys[type].
    On the next iteration, pass category_struct_keys[type] to the prompt
    as the exclusion list, so the LLM avoids regenerating the same combinations.
    This keeps the exclusion list scoped to the current category only,
    avoiding unnecessary context window inflation.
```