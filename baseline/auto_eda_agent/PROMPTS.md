# Prompt Catalog

**Complete list of all prompts used in the Expert-Driven AutoEDA system**

---

## Overview

The system uses **9 main prompts** across 5 steps:
- Step 1: 1 prompt (Semantic Analysis)
- Step 2: 1 prompt (Quality Assessment)
- Step 3: 1 prompt (Statistical Interpretation)
- Step 4: 4 prompts (Pattern Discovery - one per category)
- Step 5: 5 prompts (Insight Extraction - one per batch)

---

## Step 1: Data Profiling Agent

### Prompt 1.1: Semantic Analysis

**Purpose:** Infer semantic meaning of columns from data samples

**System Message:**
```
You are an expert data analyst inferring semantic meaning from data samples.
```

**User Prompt:**
```
You are an expert data analyst. Analyze these columns and infer their semantic meaning.

Dataset has {n_rows} rows, {n_columns} columns.

Column samples (showing unique values):
{column_samples_json}

For EACH column, infer:
1. **Semantic meaning**: What does this column represent? (e.g., "customer age", "product category", "transaction date")
2. **Data type classification**: 
   - ID/Code (unique identifiers)
   - Categorical (limited distinct values)
   - Numerical (measurements, counts, amounts)
   - Temporal (dates, times)
   - Text (free text)
3. **Patterns detected**: Any patterns in the values?
4. **Potential issues**: Missing values, inconsistencies, etc.

Return JSON:
{
  "column_name": {
    "semantic_meaning": "what this represents",
    "data_type_class": "ID|Categorical|Numerical|Temporal|Text",
    "patterns": "detected patterns",
    "potential_issues": "any issues noticed",
    "importance": "high|medium|low"
  }
}
```

**Parameters:**
- Model: `gpt-4o-mini`
- Temperature: `0.3`
- Max Tokens: `8000`
- Response Format: `json_object`

**Input Variables:**
- `n_rows`: Number of rows in dataset
- `n_columns`: Number of columns in dataset
- `column_samples_json`: JSON with column samples
  ```json
  {
    "column_name": {
      "unique_count": 5,
      "sample_values": ["value1", "value2", ...],
      "dtype": "int64"
    }
  }
  ```

**Expected Output:**
```json
{
  "Khối lượng": {
    "semantic_meaning": "Weight of the item",
    "data_type_class": "Numerical",
    "patterns": "Continuous values, some clustering",
    "potential_issues": "None detected",
    "importance": "high"
  }
}
```

---

## Step 2: Quality Analysis Agent

### Prompt 2.1: Expert Quality Assessment

**Purpose:** Interpret quality metrics and provide expert assessment

**System Message:**
```
You are a data quality expert providing professional assessment.
```

**User Prompt:**
```
You are a data quality expert. Analyze these quality metrics and provide expert assessment.

Quality Metrics:
{quality_metrics_json}

Provide expert assessment:
1. **Critical Issues**: Which quality issues are most critical and why?
2. **Impact Analysis**: How do these issues affect data reliability?
3. **Recommendations**: What should be done to address each issue?
4. **Overall Quality Score**: Rate data quality 0-100 based on severity of issues
5. **Priority Actions**: Top 3 actions to improve quality

Return JSON:
{
  "critical_issues": [
    {
      "issue": "description",
      "severity": "high|medium|low",
      "impact": "how it affects analysis",
      "recommendation": "what to do"
    }
  ],
  "overall_quality_score": 75,
  "priority_actions": ["action1", "action2", "action3"],
  "detailed_analysis": "comprehensive quality assessment"
}
```

**Parameters:**
- Model: `gpt-4o-mini`
- Temperature: `0.3`
- Max Tokens: `4000`
- Response Format: `json_object`

**Input Variables:**
- `quality_metrics_json`: JSON with computed metrics
  ```json
  {
    "missing_values": {
      "column_name": {"count": 10, "percentage": 5.0}
    },
    "outliers": {
      "column_name": {"count": 5, "percentage": 2.5, "lower_bound": 0, "upper_bound": 100}
    },
    "duplicates": 3,
    "total_issues": 15
  }
  ```

**Expected Output:**
```json
{
  "critical_issues": [
    {
      "issue": "High missing value rate in key columns",
      "severity": "high",
      "impact": "Reduces sample size and may bias analysis",
      "recommendation": "Investigate missing data mechanism and consider imputation"
    }
  ],
  "overall_quality_score": 75,
  "priority_actions": [
    "Address missing values in critical columns",
    "Investigate outliers for data entry errors",
    "Remove duplicate records"
  ],
  "detailed_analysis": "Overall data quality is good with some issues..."
}
```

---

## Step 3: Statistical Analysis Agent

### Prompt 3.1: Statistical Interpretation

**Purpose:** Interpret statistical findings as expert statistician

**System Message:**
```
You are an expert statistician interpreting data.
```

**User Prompt:**
```
You are an expert statistician. Interpret these statistical findings.

Statistical Summary:
{statistics_summary_json}

Provide expert interpretation:
1. **Distribution Patterns**: What do the distributions tell us? (skewness, kurtosis)
2. **Strong Correlations**: Interpret the strong correlations found
3. **Key Statistical Findings**: Most important statistical insights
4. **Anomalies**: Any unusual statistical patterns?
5. **Recommendations**: Statistical tests or analyses to perform next

Return JSON:
{
  "distribution_patterns": "interpretation of distributions",
  "strong_correlations": [
    {
      "variables": "var1 and var2",
      "interpretation": "what this correlation means",
      "strength": "strong|moderate|weak"
    }
  ],
  "key_findings": ["finding1", "finding2", "finding3"],
  "statistical_anomalies": ["anomaly1", "anomaly2"],
  "recommendations": ["recommendation1", "recommendation2"]
}
```

**Parameters:**
- Model: `gpt-4o-mini`
- Temperature: `0.3`
- Max Tokens: `4000`
- Response Format: `json_object`

**Input Variables:**
- `statistics_summary_json`: JSON with statistics summary
  ```json
  {
    "numerical_columns": 23,
    "categorical_columns": 32,
    "strong_correlations": [
      {"var1": "price", "var2": "quality", "correlation": 0.85}
    ],
    "sample_stats": {
      "column_name": {
        "mean": 100, "median": 95, "std": 20,
        "skewness": 0.5, "kurtosis": 2.1
      }
    }
  }
  ```

**Expected Output:**
```json
{
  "distribution_patterns": "Most numerical variables show near-normal distributions with slight positive skew...",
  "strong_correlations": [
    {
      "variables": "price and quality",
      "interpretation": "Higher quality products command higher prices",
      "strength": "strong"
    }
  ],
  "key_findings": [
    "Strong positive correlation between price and quality",
    "Sales volume shows seasonal pattern",
    "Customer age distribution is bimodal"
  ],
  "statistical_anomalies": [
    "Unusually high kurtosis in transaction amounts"
  ],
  "recommendations": [
    "Perform time series analysis on sales data",
    "Investigate bimodal age distribution for customer segmentation"
  ]
}
```

---

## Step 4: Pattern Discovery Agent

### Prompt 4.1: Temporal Patterns

**Purpose:** Discover time-based trends, seasonality, and cycles

**System Message:**
```
You are a pattern recognition expert specializing in temporal patterns.
```

**User Prompt:**
```
You are a pattern recognition expert. Discover Temporal Patterns in this dataset.

Focus: time-based trends, seasonality, cycles

Dataset Info:
{data_info_json}

Previous Analysis Available:
- Data profile with semantic meanings
- Quality metrics and issues
- Statistical analysis and correlations

Discover ALL Temporal Patterns by:
1. Analyzing the data structure and available variables
2. Looking for time-based trends, seasonality, cycles
3. Identifying specific, concrete patterns (not generic)
4. Providing evidence for each pattern

Return JSON:
{
  "patterns": [
    {
      "pattern_name": "specific pattern name",
      "description": "detailed description of the pattern",
      "variables_involved": ["var1", "var2"],
      "evidence": "concrete evidence from data",
      "strength": "strong|moderate|weak",
      "business_relevance": "why this pattern matters"
    }
  ]
}

Find as many valuable patterns as possible.
```

**Parameters:**
- Model: `gpt-4o-mini`
- Temperature: `0.5`
- Max Tokens: `8000`
- Response Format: `json_object`

**Input Variables:**
- `data_info_json`: Dataset structure info
  ```json
  {
    "shape": {"rows": 1036, "columns": 56},
    "numerical_columns": ["price", "quantity", "revenue"],
    "categorical_columns": ["category", "region", "status"]
  }
  ```

---

### Prompt 4.2: Correlation Patterns

**Purpose:** Discover strong relationships between variables

**System Message:**
```
You are a pattern recognition expert specializing in correlation patterns.
```

**User Prompt:**
```
You are a pattern recognition expert. Discover Correlation Patterns in this dataset.

Focus: strong relationships between variables

Dataset Info:
{data_info_json}

Previous Analysis Available:
- Data profile with semantic meanings
- Quality metrics and issues
- Statistical analysis and correlations

Discover ALL Correlation Patterns by:
1. Analyzing the data structure and available variables
2. Looking for strong relationships between variables
3. Identifying specific, concrete patterns (not generic)
4. Providing evidence for each pattern

Return JSON:
{
  "patterns": [
    {
      "pattern_name": "specific pattern name",
      "description": "detailed description of the pattern",
      "variables_involved": ["var1", "var2"],
      "evidence": "concrete evidence from data",
      "strength": "strong|moderate|weak",
      "business_relevance": "why this pattern matters"
    }
  ]
}

Find as many valuable patterns as possible.
```

**Parameters:** Same as Prompt 4.1

---

### Prompt 4.3: Grouping Patterns

**Purpose:** Discover natural clusters and segments

**System Message:**
```
You are a pattern recognition expert specializing in grouping patterns.
```

**User Prompt:**
```
You are a pattern recognition expert. Discover Grouping Patterns in this dataset.

Focus: natural clusters and segments

Dataset Info:
{data_info_json}

Previous Analysis Available:
- Data profile with semantic meanings
- Quality metrics and issues
- Statistical analysis and correlations

Discover ALL Grouping Patterns by:
1. Analyzing the data structure and available variables
2. Looking for natural clusters and segments
3. Identifying specific, concrete patterns (not generic)
4. Providing evidence for each pattern

Return JSON:
{
  "patterns": [
    {
      "pattern_name": "specific pattern name",
      "description": "detailed description of the pattern",
      "variables_involved": ["var1", "var2"],
      "evidence": "concrete evidence from data",
      "strength": "strong|moderate|weak",
      "business_relevance": "why this pattern matters"
    }
  ]
}

Find as many valuable patterns as possible.
```

**Parameters:** Same as Prompt 4.1

---

### Prompt 4.4: Anomaly Patterns

**Purpose:** Discover unusual behaviors and outliers

**System Message:**
```
You are a pattern recognition expert specializing in anomaly patterns.
```

**User Prompt:**
```
You are a pattern recognition expert. Discover Anomaly Patterns in this dataset.

Focus: unusual behaviors and outliers

Dataset Info:
{data_info_json}

Previous Analysis Available:
- Data profile with semantic meanings
- Quality metrics and issues
- Statistical analysis and correlations

Discover ALL Anomaly Patterns by:
1. Analyzing the data structure and available variables
2. Looking for unusual behaviors and outliers
3. Identifying specific, concrete patterns (not generic)
4. Providing evidence for each pattern

Return JSON:
{
  "patterns": [
    {
      "pattern_name": "specific pattern name",
      "description": "detailed description of the pattern",
      "variables_involved": ["var1", "var2"],
      "evidence": "concrete evidence from data",
      "strength": "strong|moderate|weak",
      "business_relevance": "why this pattern matters"
    }
  ]
}

Find as many valuable patterns as possible.
```

**Parameters:** Same as Prompt 4.1

---

## Step 5: Insight Extraction Agent

### Prompt 5.1: TREND Insights

**Purpose:** Extract temporal trends and directional changes

**System Message:**
```
You are an expert data analyst extracting maximum insights. Find as many valuable insights as possible.
```

**User Prompt:**
```
Based on ALL previous analysis steps, extract valuable insights focused on: temporal trends and directional changes

Insight types to find: TREND

Available context:
- Data profile from step 1
- Quality issues from step 2
- Statistical analysis from step 3
- Discovered patterns from step 4

Extract AS MANY valuable insights as possible for these types. Each insight should be:
- Specific and concrete (not generic)
- Supported by evidence from previous steps
- Actionable or decision-relevant
- Visualizable with the available data

Return JSON:
{
  "insights": [
    {
      "title": "Specific insight title",
      "description": "Detailed description with numbers and evidence",
      "type": "TREND",
      "variables": ["var1", "var2"],
      "evidence": {
        "source_step": "step3_statistics",
        "key_statistics": "Specific numbers",
        "data_points": "Concrete evidence"
      }
    }
  ]
}
```

**Parameters:**
- Model: `gpt-4o-mini`
- Temperature: `0.5`
- Max Tokens: `16000`
- Response Format: `json_object`

---

### Prompt 5.2: OUTLIER, ANOMALY Insights

**Purpose:** Extract unusual values and anomalies

**System Message:** Same as Prompt 5.1

**User Prompt:**
```
Based on ALL previous analysis steps, extract valuable insights focused on: unusual values and anomalies

Insight types to find: OUTLIER, ANOMALY

Available context:
- Data profile from step 1
- Quality issues from step 2
- Statistical analysis from step 3
- Discovered patterns from step 4

Extract AS MANY valuable insights as possible for these types. Each insight should be:
- Specific and concrete (not generic)
- Supported by evidence from previous steps
- Actionable or decision-relevant
- Visualizable with the available data

Return JSON:
{
  "insights": [
    {
      "title": "Specific insight title",
      "description": "Detailed description with numbers and evidence",
      "type": "OUTLIER or ANOMALY",
      "variables": ["var1", "var2"],
      "evidence": {
        "source_step": "step2_quality",
        "key_statistics": "Specific numbers",
        "data_points": "Concrete evidence"
      }
    }
  ]
}
```

**Parameters:** Same as Prompt 5.1

---

### Prompt 5.3: CORRELATION Insights

**Purpose:** Extract relationships between variables

**System Message:** Same as Prompt 5.1

**User Prompt:**
```
Based on ALL previous analysis steps, extract valuable insights focused on: relationships between variables

Insight types to find: CORRELATION

Available context:
- Data profile from step 1
- Quality issues from step 2
- Statistical analysis from step 3
- Discovered patterns from step 4

Extract AS MANY valuable insights as possible for these types. Each insight should be:
- Specific and concrete (not generic)
- Supported by evidence from previous steps
- Actionable or decision-relevant
- Visualizable with the available data

Return JSON:
{
  "insights": [
    {
      "title": "Specific insight title",
      "description": "Detailed description with numbers and evidence",
      "type": "CORRELATION",
      "variables": ["var1", "var2"],
      "evidence": {
        "source_step": "step3_statistics",
        "key_statistics": "Specific numbers",
        "data_points": "Concrete evidence"
      }
    }
  ]
}
```

**Parameters:** Same as Prompt 5.1

---

### Prompt 5.4: DISTRIBUTION, COMPARISON Insights

**Purpose:** Extract distributions and group comparisons

**System Message:** Same as Prompt 5.1

**User Prompt:**
```
Based on ALL previous analysis steps, extract valuable insights focused on: distributions and group comparisons

Insight types to find: DISTRIBUTION, COMPARISON

Available context:
- Data profile from step 1
- Quality issues from step 2
- Statistical analysis from step 3
- Discovered patterns from step 4

Extract AS MANY valuable insights as possible for these types. Each insight should be:
- Specific and concrete (not generic)
- Supported by evidence from previous steps
- Actionable or decision-relevant
- Visualizable with the available data

Return JSON:
{
  "insights": [
    {
      "title": "Specific insight title",
      "description": "Detailed description with numbers and evidence",
      "type": "DISTRIBUTION or COMPARISON",
      "variables": ["var1", "var2"],
      "evidence": {
        "source_step": "step1_profiling",
        "key_statistics": "Specific numbers",
        "data_points": "Concrete evidence"
      }
    }
  ]
}
```

**Parameters:** Same as Prompt 5.1

---

### Prompt 5.5: PATTERN Insights

**Purpose:** Extract recurring patterns and cycles

**System Message:** Same as Prompt 5.1

**User Prompt:**
```
Based on ALL previous analysis steps, extract valuable insights focused on: recurring patterns and cycles

Insight types to find: PATTERN

Available context:
- Data profile from step 1
- Quality issues from step 2
- Statistical analysis from step 3
- Discovered patterns from step 4

Extract AS MANY valuable insights as possible for these types. Each insight should be:
- Specific and concrete (not generic)
- Supported by evidence from previous steps
- Actionable or decision-relevant
- Visualizable with the available data

Return JSON:
{
  "insights": [
    {
      "title": "Specific insight title",
      "description": "Detailed description with numbers and evidence",
      "type": "PATTERN",
      "variables": ["var1", "var2"],
      "evidence": {
        "source_step": "step4_patterns",
        "key_statistics": "Specific numbers",
        "data_points": "Concrete evidence"
      }
    }
  ]
}
```

**Parameters:** Same as Prompt 5.1

---

## Prompt Design Principles

### 1. Clear Role Definition
Each prompt starts with clear role definition:
```
You are an expert [domain] [doing specific task]
```

### 2. Explicit Instructions
Prompts provide explicit numbered instructions:
```
1. Do X
2. Do Y
3. Do Z
```

### 3. Structured Output
All prompts request JSON output with specific schema:
```json
{
  "field1": "description",
  "field2": ["list", "of", "items"]
}
```

### 4. Context Provision
Prompts include relevant context from previous steps:
```
Available context:
- Data profile from step 1
- Quality issues from step 2
...
```

### 5. Quality Emphasis
Prompts emphasize quality and specificity:
```
- Specific and concrete (not generic)
- Supported by evidence
- Actionable or decision-relevant
```

---

## Customization Guide

### How to Modify Prompts

1. **Change Focus Area**
   ```python
   # In agent.py, modify category focus
   {'name': 'Your Pattern', 'focus': 'your specific focus'}
   ```

2. **Adjust Output Format**
   ```python
   # Modify JSON schema in prompt
   Return JSON:
   {
     "your_field": "your_description"
   }
   ```

3. **Add More Instructions**
   ```python
   # Add numbered instructions
   5. **Your New Instruction**: Description
   ```

4. **Change Temperature**
   ```python
   # In API call
   temperature=0.3  # More deterministic
   temperature=0.7  # More creative
   ```

5. **Increase Max Tokens**
   ```python
   # In API call
   max_tokens=16000  # For longer outputs
   ```

---

## Prompt Performance

### Token Usage (Approximate)

| Prompt | Input Tokens | Output Tokens | Total |
|--------|--------------|---------------|-------|
| Semantic Analysis | 2000-3000 | 1000-2000 | 3000-5000 |
| Quality Assessment | 1000-1500 | 500-1000 | 1500-2500 |
| Statistical Interpretation | 1000-1500 | 500-1000 | 1500-2500 |
| Pattern Discovery (each) | 500-1000 | 1000-2000 | 1500-3000 |
| Insight Extraction (each) | 1000-2000 | 2000-4000 | 3000-6000 |

**Total per run:** ~30,000-50,000 tokens

### Cost Estimate (GPT-4o-mini)

- Input: $0.150 / 1M tokens
- Output: $0.600 / 1M tokens

**Per run:** $0.02-0.04 USD

---

## Version History

### v1.0 (March 2026)
- Initial prompt catalog
- 9 main prompts across 5 steps
- Multi-prompt strategy for patterns and insights

---

**Last Updated:** March 2026  
**Maintained by:** EDAAgent Project
