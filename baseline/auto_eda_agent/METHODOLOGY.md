# Expert-Driven Agentic AutoEDA: Methodology Report

**Version:** 1.0  
**Date:** March 2026  
**Model:** GPT-4o-mini (OpenAI)

---

## Abstract

This report documents the methodology of an expert-driven agentic AutoEDA system that leverages Large Language Models (LLMs) as domain specialists rather than code generators. Unlike traditional AutoEDA approaches that generate and execute code, our system positions the LLM as multiple expert analysts who directly analyze data and produce insights. The system achieves comprehensive exploratory data analysis through a 5-step pipeline: data profiling with semantic analysis, quality assessment, statistical interpretation, pattern discovery, and insight extraction. Each step employs a multi-prompt strategy to ensure thorough coverage. Insights are evaluated using the ISGEN methodology for objective quality assessment.

---

## 1. Introduction

### 1.1 Motivation

Traditional AutoEDA systems face several challenges:

1. **Code Generation Reliability**: LLM-generated code often contains syntax errors, incorrect API usage, or path issues, requiring extensive error handling and fallback mechanisms.

2. **Limited Semantic Understanding**: Statistical summaries (e.g., `df.describe()`) provide numerical information but lack business context and semantic meaning.

3. **Single-Pass Analysis**: Most systems perform analysis in a single pass, missing opportunities for iterative refinement and comprehensive coverage.

4. **Evaluation Challenges**: Lack of standardized metrics to evaluate insight quality objectively.

### 1.2 Proposed Approach

We propose an **expert-driven agentic architecture** where:

- **LLM acts as domain experts** with specialized knowledge in data profiling, quality analysis, statistics, pattern recognition, and insight extraction
- **Direct data analysis** instead of code generation eliminates execution failures
- **Multi-prompt strategy** ensures comprehensive coverage of different analysis aspects
- **Semantic analysis** infers business meaning from data samples
- **ISGEN scoring** provides objective insight quality evaluation

---

## 2. System Architecture

### 2.1 Overview

The system consists of 5 sequential autonomous agents, each acting as a specialist in their domain:

```
┌─────────────────────────────────────────────────────────────┐
│                    AgenticAutoEDA System                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Step 1: Data Profiling Agent (Semantic Analysis)           │
│           ↓                                                   │
│  Step 2: Quality Analysis Agent (Expert Assessment)         │
│           ↓                                                   │
│  Step 3: Statistical Analysis Agent (Interpretation)        │
│           ↓                                                   │
│  Step 4: Pattern Discovery Agent (Multi-Prompt)             │
│           ↓                                                   │
│  Step 5: Insight Extraction Agent (Multi-Prompt + ISGEN)    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Core Design Principles

1. **Autonomy**: Each agent operates independently with its own objectives
2. **Expertise**: Each agent embodies domain-specific knowledge
3. **Iterability**: Agents can refine analysis through multiple iterations
4. **Composability**: Outputs from earlier steps inform later steps
5. **Transparency**: Verbose logging shows agent reasoning process

---

## 3. Detailed Methodology

### 3.1 Step 1: Data Profiling Agent

**Objective**: Deeply understand dataset structure and semantics

#### Phase 1: Initial Exploration

```python
- Load dataset using pandas
- Identify column types (numerical, categorical)
- Count missing values
- Extract basic statistics
```

**Output**: Structural metadata (shape, dtypes, missing counts)

#### Phase 2: Semantic Analysis (Innovation)

**Key Innovation**: Instead of just computing statistics, we sample unique values and ask LLM to infer semantic meaning.

**Process**:
1. For each column (up to 30 columns):
   - Extract unique values (up to 20 if few, 10 if many)
   - Prepare sample data with dtype information

2. LLM Prompt Structure:
```
You are an expert data analyst. Analyze these columns and infer their semantic meaning.

Column samples (showing unique values):
{column_name: {unique_count, sample_values, dtype}}

For EACH column, infer:
1. Semantic meaning: What does this represent?
2. Data type classification: ID/Categorical/Numerical/Temporal/Text
3. Patterns detected: Any patterns in values?
4. Potential issues: Missing values, inconsistencies?
5. Importance: high/medium/low

Return JSON with analysis for each column.
```

3. LLM analyzes samples and returns:
   - `semantic_meaning`: Business interpretation (e.g., "customer age", "transaction date")
   - `data_type_class`: Semantic type beyond pandas dtype
   - `patterns`: Detected patterns in values
   - `potential_issues`: Quality concerns
   - `importance`: Relevance for analysis

**Example Output**:
```json
{
  "Khối lượng": {
    "semantic_meaning": "Weight of the item",
    "data_type_class": "Numerical",
    "importance": "high",
    "patterns": "Continuous values, some clustering around standard weights"
  }
}
```

#### Phase 3: Comprehensive Profiling

Combines structural analysis with semantic analysis:
- Merge statistics with semantic meanings
- Assign importance levels
- Generate human-readable summary

**Output**: `profile.json` + `summary.md`

**Advantages**:
- Goes beyond statistical summaries
- Understands business context
- Identifies key variables early
- Informs downstream analysis

---

### 3.2 Step 2: Quality Analysis Agent

**Objective**: Assess data quality and identify critical issues

#### Phase 1: Compute Quality Metrics

Direct computation using pandas:
```python
- Missing values: count and percentage per column
- Outliers: IQR method (Q1 - 1.5*IQR, Q3 + 1.5*IQR)
- Duplicates: exact row duplicates
```

**Output**: Quantitative metrics

#### Phase 2: Expert Quality Assessment

**Key Innovation**: LLM acts as quality expert to interpret metrics and provide actionable recommendations.

**LLM Prompt Structure**:
```
You are a data quality expert. Analyze these quality metrics.

Quality Metrics:
{missing_values, outliers, duplicates}

Provide expert assessment:
1. Critical Issues: Which issues are most critical and why?
2. Impact Analysis: How do these affect data reliability?
3. Recommendations: What should be done?
4. Overall Quality Score: Rate 0-100
5. Priority Actions: Top 3 actions

Return JSON with structured assessment.
```

**Output**: `quality_report.json` with:
- Quantitative metrics
- Expert interpretation
- Critical issues with severity levels
- Actionable recommendations
- Quality score (0-100)

**Advantages**:
- Prioritizes issues by impact
- Provides business context
- Actionable recommendations
- Holistic quality assessment

---

### 3.3 Step 3: Statistical Analysis Agent

**Objective**: Compute and interpret statistical properties

#### Phase 1: Compute Comprehensive Statistics

Direct computation:
```python
Numerical columns:
- Descriptive: mean, median, std, min, max, quartiles
- Distribution: skewness, kurtosis

Categorical columns:
- Unique count, most common value, distribution

Correlations:
- Pearson correlation matrix
- Strong correlations (|r| > 0.7)
```

**Output**: Comprehensive statistics

#### Phase 2: Statistical Interpretation

**Key Innovation**: LLM acts as statistician to interpret findings.

**LLM Prompt Structure**:
```
You are an expert statistician. Interpret these statistical findings.

Statistical Summary:
{numerical_stats, categorical_stats, strong_correlations}

Provide expert interpretation:
1. Distribution Patterns: What do distributions tell us?
2. Strong Correlations: Interpret relationships
3. Key Statistical Findings: Most important insights
4. Anomalies: Unusual statistical patterns?
5. Recommendations: Next analyses to perform

Return JSON with interpretation.
```

**Output**: `statistics.json` with:
- Raw statistics
- Expert interpretation
- Key findings
- Correlation explanations

**Advantages**:
- Explains what statistics mean
- Identifies important relationships
- Provides statistical context
- Guides further analysis

---

### 3.4 Step 4: Pattern Discovery Agent

**Objective**: Discover patterns across multiple dimensions

#### Multi-Prompt Strategy (Innovation)

**Key Innovation**: Instead of single prompt, use 4 specialized prompts for different pattern types.

**Pattern Categories**:
1. **Temporal Patterns**: time-based trends, seasonality, cycles
2. **Correlation Patterns**: strong relationships between variables
3. **Grouping Patterns**: natural clusters and segments
4. **Anomaly Patterns**: unusual behaviors and outliers

**For Each Category**:

1. Prepare context from previous steps
2. LLM Prompt Structure:
```
You are a pattern recognition expert. Discover {category_name}.

Focus: {category_focus}

Dataset Info:
{shape, numerical_columns, categorical_columns}

Previous Analysis Available:
- Data profile with semantic meanings
- Quality metrics and issues
- Statistical analysis and correlations

Discover ALL {category_name} by:
1. Analyzing data structure and variables
2. Looking for {category_focus}
3. Identifying specific, concrete patterns (not generic)
4. Providing evidence for each pattern

Return JSON:
{
  "patterns": [
    {
      "pattern_name": "specific name",
      "description": "detailed description",
      "variables_involved": ["var1", "var2"],
      "evidence": "concrete evidence",
      "strength": "strong|moderate|weak",
      "business_relevance": "why this matters"
    }
  ]
}
```

3. Consolidate patterns from all categories

**Output**: `patterns.json` with 20-30 patterns across 4 categories

**Advantages**:
- Comprehensive coverage of pattern types
- Specialized prompts produce better results
- More patterns discovered than single prompt
- Structured by category for easy analysis

---

### 3.5 Step 5: Insight Extraction Agent

**Objective**: Extract actionable insights and evaluate quality

#### Multi-Prompt Strategy

**Key Innovation**: 5 specialized prompts for different insight types.

**Insight Batches**:
1. **TREND**: temporal trends and directional changes
2. **OUTLIER, ANOMALY**: unusual values
3. **CORRELATION**: relationships between variables
4. **DISTRIBUTION, COMPARISON**: distributions and group comparisons
5. **PATTERN**: recurring patterns and cycles

**For Each Batch**:

1. Collect context from all previous steps
2. LLM Prompt Structure:
```
Based on ALL previous analysis steps, extract valuable insights focused on: {focus}

Insight types to find: {types}

Available context:
- Data profile from step 1
- Quality issues from step 2
- Statistical analysis from step 3
- Discovered patterns from step 4

Extract AS MANY valuable insights as possible. Each insight should be:
- Specific and concrete (not generic)
- Supported by evidence from previous steps
- Actionable or decision-relevant
- Visualizable with available data

Return JSON with insights array.
```

3. Generate visualization for each insight
4. Apply ISGEN scoring
5. Filter by quality threshold

**Output**: `insights.json` with 25-30 insights + charts + ISGEN scores

---

## 4. ISGEN Scoring Methodology

### 4.1 Overview

We adopt the ISGEN (Insight Generation) methodology for objective insight quality evaluation.

### 4.2 Pattern Types and Scoring Functions

| Pattern | Scoring Function | Threshold | Description |
|---------|-----------------|-----------|-------------|
| **TREND** | Mann-Kendall test (1 - p_value) | 0.95 | Monotonic trend detection |
| **OUTSTANDING_VALUE** | max/second_max ratio | 1.4 | Outlier/anomaly detection |
| **ATTRIBUTION** | max/sum ratio | 0.5 | Dominant category detection |
| **QUALITY** | Heuristic quality score | 0.6 | For other insight types |

### 4.3 Implementation

```python
def score_insight(insight_data, values):
    insight_type = insight_data.get('type', '')
    
    if insight_type == 'TREND':
        # Mann-Kendall test for monotonic trend
        result = mk.original_test(values)
        score = 1 - result.p
        threshold = 0.95
        pattern = 'TREND'
    
    elif insight_type in ['OUTLIER', 'ANOMALY']:
        # Outstanding value detection
        sorted_vals = sorted(values, reverse=True)
        ratio = sorted_vals[0] / sorted_vals[1] if len(sorted_vals) > 1 else 1
        score = ratio
        threshold = 1.4
        pattern = 'OUTSTANDING_VALUE'
    
    # ... other patterns
    
    return {
        'pattern_type': pattern,
        'pattern_score': score,
        'threshold': threshold,
        'passed': score >= threshold
    }
```

### 4.4 Evaluation Metrics

- **Total Insights**: Number of insights extracted
- **Pass Rate**: Percentage passing ISGEN threshold
- **Average Score**: Mean pattern score across all insights
- **Type Distribution**: Diversity across insight types
- **Pattern Distribution**: Distribution across ISGEN patterns

---

## 5. Experimental Setup

### 5.1 Dataset

- **Name**: transactions.csv
- **Size**: 1,036 rows × 56 columns
- **Types**: 23 numerical, 32 categorical
- **Domain**: Sales/transaction data (Vietnamese)

### 5.2 Configuration

```python
Model: gpt-4o-mini (OpenAI)
Temperature: 0.3 (profiling, quality, statistics)
            0.5 (pattern discovery, insight extraction)
Max Tokens: 4000-8000 (varies by step)
Max Iterations: 3 (not used in expert-driven approach)
```

### 5.3 Execution

```bash
python run.py ../../data/transactions.csv output
```

**Runtime**: ~3-5 minutes (depends on API latency)

---

## 6. Results

### 6.1 Quantitative Results

```
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

Patterns Discovered: 25 patterns
  • Temporal Patterns: 5
  • Correlation Patterns: 6
  • Grouping Patterns: 7
  • Anomaly Patterns: 7
```

### 6.2 Qualitative Analysis

#### Semantic Analysis Quality

The system successfully inferred semantic meanings:
- "Khối lượng" → "Weight of the item" (Numerical, High importance)
- "Ngày bán" → "Date of sale" (Temporal, High importance)
- "Phân loại" → "Classification of items" (Categorical, Medium importance)

This semantic understanding enabled more relevant pattern discovery and insight extraction.

#### Pattern Discovery Coverage

Multi-prompt strategy discovered diverse patterns:
- **Temporal**: Monthly sales seasonality, weekly traffic patterns
- **Correlation**: Strong relationships between advertising spend and sales
- **Grouping**: Customer segments by purchase behavior
- **Anomaly**: Unusual spikes in specific product categories

#### Insight Quality

Top insights (ISGEN score = 1.0):
1. High correlation between advertising spend and sales revenue
2. Inverse correlation between customer complaints and satisfaction
3. Correlation between product return rates and quality ratings
4. Age distribution skewness in customer base
5. Monthly sales spike during holiday season

All top insights are:
- Specific and concrete
- Supported by statistical evidence
- Actionable for business decisions
- Properly visualized

---

## 7. Advantages and Limitations

### 7.1 Advantages

✅ **No Code Execution Failures**
- LLM analyzes directly, eliminating code generation errors
- More reliable and reproducible

✅ **Deep Semantic Understanding**
- Infers business meaning from data samples
- Goes beyond statistical summaries

✅ **Comprehensive Coverage**
- Multi-prompt strategy ensures thorough analysis
- 25+ patterns, 26+ insights extracted

✅ **Expert-Level Analysis**
- Each step acts as domain specialist
- Provides interpretations and recommendations

✅ **Objective Evaluation**
- ISGEN scoring provides standardized quality metrics
- Enables comparison with other methods

✅ **Verbose and Transparent**
- Shows agent reasoning process
- Easy to debug and improve

### 7.2 Limitations

❌ **LLM Dependency**
- Requires API access and credits
- Quality depends on LLM capability
- API latency affects runtime

❌ **Limited to LLM Knowledge**
- Cannot discover patterns requiring complex algorithms
- No advanced statistical tests (e.g., hypothesis testing)

❌ **Moderate ISGEN Pass Rate**
- 50% pass rate indicates room for improvement
- Many insights scored as "QUALITY" (heuristic) rather than specific patterns

❌ **Scalability Concerns**
- Analyzes only first 30 columns for semantic analysis
- Multiple API calls increase cost and time

❌ **Language Dependency**
- Optimized for English prompts
- Vietnamese data may reduce LLM understanding

---

## 8. Comparison with Traditional Approaches

### 8.1 vs. Code Generation Approach

| Aspect | Code Generation | Expert-Driven (Ours) |
|--------|----------------|---------------------|
| **Reliability** | ❌ Frequent failures | ✅ No execution errors |
| **Semantic Understanding** | ❌ Limited | ✅ Deep inference |
| **Iteration Needed** | ❌ 2-3 iterations | ✅ Single pass |
| **Debugging** | ❌ Complex | ✅ Straightforward |
| **LLM Capability Used** | Coding | ✅ Analytical reasoning |

### 8.2 vs. Traditional AutoEDA Tools

| Aspect | Traditional Tools | Expert-Driven (Ours) |
|--------|------------------|---------------------|
| **Semantic Analysis** | ❌ None | ✅ Infers meaning |
| **Pattern Discovery** | ❌ Predefined | ✅ LLM-discovered |
| **Insight Quality** | ❌ No scoring | ✅ ISGEN scoring |
| **Interpretability** | ❌ Limited | ✅ Expert explanations |
| **Customization** | ❌ Hard-coded | ✅ Prompt-based |

---

## 9. Future Work

### 9.1 Improvements

1. **Iterative Refinement**
   - Currently single-pass per step
   - Could add self-reflection and refinement loops
   - Agent evaluates output and decides to continue or stop

2. **Advanced Statistical Tests**
   - Integrate hypothesis testing
   - Causality analysis
   - Time series decomposition

3. **Hybrid Approach**
   - Combine LLM analysis with algorithmic methods
   - Use LLM to decide which algorithms to apply
   - LLM interprets algorithmic results

4. **Improved ISGEN Scoring**
   - Develop better heuristics for QUALITY pattern
   - Add more ISGEN pattern types
   - Calibrate thresholds per dataset

5. **Scalability**
   - Analyze all columns (not just first 30)
   - Batch processing for large datasets
   - Optimize API usage

### 9.2 Extensions

1. **Interactive Mode**
   - User can guide analysis
   - Agent asks clarifying questions
   - Iterative refinement based on feedback

2. **Multi-Dataset Analysis**
   - Compare patterns across datasets
   - Identify common vs unique patterns
   - Cross-dataset insights

3. **Domain-Specific Agents**
   - Finance-specialized agent
   - Healthcare-specialized agent
   - Custom domain knowledge

4. **Automated Report Generation**
   - Generate executive summary
   - Create presentation slides
   - Export to various formats

---

## 10. Conclusion

This work presents an expert-driven agentic AutoEDA system that positions LLM as domain specialists rather than code generators. The key innovations are:

1. **Semantic Analysis**: Inferring business meaning from data samples
2. **Expert-Driven Architecture**: LLM acts as multiple domain experts
3. **Multi-Prompt Strategy**: Comprehensive coverage through specialized prompts
4. **Direct Analysis**: No code generation, eliminating execution failures
5. **ISGEN Scoring**: Objective insight quality evaluation

The system successfully extracts 26 insights with 50% ISGEN pass rate, discovers 25 patterns across 4 categories, and provides comprehensive data profiling with semantic understanding. While there are limitations (LLM dependency, moderate pass rate), the approach demonstrates the potential of using LLMs as analytical experts rather than code generators.

This baseline provides a robust foundation for comparing with other AutoEDA methods and can be extended with iterative refinement, advanced statistical tests, and domain-specific knowledge.

---

## References

1. **ISGEN Paper**: Insight generation methodology and scoring functions
2. **OpenAI GPT-4**: Large language model for expert analysis
3. **Mann-Kendall Test**: Trend detection in time series (pymannkendall library)
4. **Pandas**: Data manipulation and analysis library
5. **AutoEDA Literature**: Survey of automated exploratory data analysis methods

---

## Appendix A: Prompt Templates

### A.1 Semantic Analysis Prompt

```
You are an expert data analyst. Analyze these columns and infer their semantic meaning.

Dataset has {n_rows} rows, {n_columns} columns.

Column samples (showing unique values):
{column_samples_json}

For EACH column, infer:
1. **Semantic meaning**: What does this column represent?
2. **Data type classification**: ID/Categorical/Numerical/Temporal/Text
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

### A.2 Pattern Discovery Prompt

```
You are a pattern recognition expert. Discover {category_name} in this dataset.

Focus: {category_focus}

Dataset Info:
{data_info_json}

Previous Analysis Available:
- Data profile with semantic meanings
- Quality metrics and issues
- Statistical analysis and correlations

Discover ALL {category_name} by:
1. Analyzing the data structure and available variables
2. Looking for {category_focus}
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

### A.3 Insight Extraction Prompt

```
Based on ALL previous analysis steps, extract valuable insights focused on: {focus}

Insight types to find: {types}

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
      "type": "One of: {types}",
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

---

## Appendix B: System Requirements

### B.1 Hardware

- **CPU**: Any modern processor
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB for dependencies + output

### B.2 Software

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Internet**: Required for OpenAI API access

### B.3 Dependencies

```
pandas>=2.0.0
numpy>=1.24.0
openai>=1.0.0
python-dotenv>=1.0.0
pymannkendall>=1.4.3
matplotlib>=3.7.0
seaborn>=0.12.0
scipy>=1.10.0
```

---

**End of Report**
