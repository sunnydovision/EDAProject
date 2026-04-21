# IFQ: Insight-Finding via Question Generation — Methodology Report

**Version:** 1.0  
**Date:** April 2026  
**Model:** gpt-5.4 (OpenAI Responses API; fallback to Chat Completions)

---

## Abstract

This report describes IFQ (Insight-Finding via Question Generation), an automated EDA pipeline that combines LLM-driven question generation with a statistically grounded insight search engine. The system is composed of two sequential components: QUGEN, which generates a diverse set of analytical questions paired with breakdown and measure dimensions; and ISGEN, which searches the dataset for statistically interesting insights corresponding to those questions. The pipeline produces structured insights covering trends, outstanding values, attribution, and distribution differences, together with natural language explanations and visualizations.

---

## 1. Introduction

Most AutoEDA systems either enumerate all possible column combinations exhaustively (leading to combinatorial explosion) or ask LLMs to freely generate insights without any formal interestingness criterion (leading to unverifiable or trivial findings). IFQ addresses both limitations: the question space is reduced by LLM-guided semantic selection (QUGEN), and insight quality is enforced by quantitative scoring functions applied to actual data (ISGEN). LLMs are used for question generation and subspace guidance, not for making final judgments about data patterns.

---

## 2. System Overview

The pipeline consists of two stages. QUGEN produces Insight Cards from the table schema; ISGEN consumes those cards and the dataset to produce scored, explainable insights.

```
Preprocessed CSV
  │
  ▼
[QUGEN — Question Generation]
  Input:  Table schema (column names + dtypes) + optional dataframe
  Output: Insight Cards (question, reason, breakdown B, measure M)
  │
  ▼
[ISGEN — Insight Search & Generation]
  Input:  Insight Cards + DataFrame
  Output: Insight summaries (insight, explanation, plot)
```

---

## 3. Preprocessing

IFQ expects the input CSV to be preprocessed before loading. The shared data loader (`load_data`) validates that all numerically-intended columns have been converted to numeric types. It also auto-detects the CSV separator (`,` vs `;`) from the first line of the file. If any column appears numeric in content but remains string-typed, loading is rejected and the user is directed to the dataset-specific preprocessing script.

---

## 4. Stage 1 — QUGEN: Question Generation

### 4.1 Objective

Generate a diverse, schema-relevant set of Insight Cards. Each Insight Card consists of four fields:

- **Question (Q):** a natural language analytical question about the data
- **Reason:** why this question is analytically interesting
- **Breakdown (B):** the dimension across which the measure is compared
- **Measure (M):** an aggregation expression (e.g. `SUM(Revenue)`, `MEAN(Profit)`, `COUNT(*)`)

### 4.2 Input Preparation

Before question generation, the pipeline computes **natural language statistics** for the table. An LLM is prompted with the table schema to produce a list of basic statistical questions (tagged with `[STAT]...[/STAT]`). These questions are then answered using simple direct aggregations on the dataframe — column-level min, max, mean for numerical columns and unique-value counts for categorical columns — and formatted as natural language bullet points. This statistical summary is injected into each QUGEN prompt to ground the LLM in actual data properties.

### 4.3 Iterative Generation

QUGEN generates Insight Cards in an iterative loop of `num_iterations=10` iterations. In each iteration:

1. A prompt is constructed containing:
   - Task description and instructions (adapted from the paper's Figure 6)
   - Few-shot examples (schema + Insight Cards) drawn from a fixed pool and from previously accepted cards, selected with preference for **measure diversity**
   - Natural language statistics computed in Section 4.2
   - A measure diversity instruction: cards must use different measure columns; overused measures from prior iterations are listed for the LLM to avoid
   - A request for `num_questions_per_prompt=10` unique Insight Cards

2. The prompt is sent to the LLM `num_samples_per_iteration=3` times independently (temperature `1.1`) to increase output diversity.

3. All responses are parsed for `[INSIGHT]...[/INSIGHT]` tagged blocks, each yielding one Insight Card.

4. Three filters are applied in sequence (Section 4.4).

5. Accepted cards are added to the pool, and the pool is re-deduplicated globally.

6. In-context examples for the next iteration are refreshed from the current pool, prioritizing measure diversity.

After all iterations, if more than 50% of cards in the pool share the same measure column, one additional **diversity enforcement** iteration is run with all overused measures listed as forbidden, to ensure the final pool spans multiple analytical dimensions.

### 4.4 Filtering

Three filters are applied to every batch of generated cards:

| Filter | Method | Threshold |
|---|---|---|
| **Schema relevance** | Cosine similarity between question embedding and schema text embedding (`all-MiniLM-L6-v2`) | ≥ 0.25 |
| **Deduplication** | Cosine similarity between question embeddings; first occurrence kept | < 0.85 to keep |
| **Simple-question removal** | Heuristic: questions shorter than 15 characters or matching single-value patterns (e.g. "what is the count of …") are discarded | — |

The deduplication filter is also applied globally to the accumulated pool after each iteration, ensuring that cards generated in different iterations do not repeat.

### 4.5 Output

A JSON list of Insight Cards, each containing `question`, `reason`, `breakdown`, and `measure`. After generation, a final exact-text deduplication pass removes any cards sharing identical normalized question strings.

---

## 5. Stage 2 — ISGEN: Insight Search and Generation

### 5.1 Objective

For each Insight Card (B, M), search the dataset for subsets (subspaces) where the view `view(D_S, B, M)` — i.e. the aggregated values of measure M grouped by breakdown B, filtered to subspace S — exhibits a statistically interesting pattern.

### 5.2 Insight Representation

Every insight is a 4-tuple **(B, M, S, P)**:

- **B** — breakdown column
- **M** — measure expression (`AGG(column)` or `COUNT(*)`)
- **S** — subspace: a set of (column, value) equality filters applied before aggregation; empty S = whole dataset
- **P** — pattern type: one of Trend, Outstanding Value, Attribution, Distribution Difference

### 5.3 Pattern Scoring

Four pattern types are defined, each with a dedicated scoring function and interestingness threshold:

| Pattern | Score Function | Threshold |
|---|---|---|
| **Trend** | `1 − p-value` of Mann-Kendall monotonic trend test | ≥ 0.90 |
| **Outstanding Value** | Ratio of the two largest absolute values: `vmax1 / vmax2` | ≥ 1.4 |
| **Attribution** | Maximum value as a share of the total: `max(v) / sum(v)` | ≥ 0.5 |
| **Distribution Difference** | Jensen-Shannon divergence between the subspace distribution and the full-dataset distribution | ≥ 0.2 |

Trend is only applicable when the breakdown column is temporal (datetime type or name containing temporal keywords such as "month", "date", "quarter"). All thresholds are scaled by a configurable `threshold_scale` factor (default `0.7`) to allow more insights to surface in interactive settings.

### 5.4 Basic Insight Extraction

For each Insight Card, the pipeline first computes the global view `view(D, B, M)` over the entire dataset with an empty subspace. Each applicable pattern is scored against these values. An insight `(B, M, φ, P)` is accepted if its score meets the scaled threshold. At most `max_insights_per_card=3` insights are retained per card, selecting the single best-scoring insight per pattern to ensure pattern diversity before filling remaining slots by score.

### 5.5 Subspace Search

For each Insight Card and each applicable pattern, a beam search (Algorithm 1 from the paper) explores the space of subspaces to find data segments where the view is more interesting than the global view.

**Algorithm:**

1. Start with a beam containing the empty subspace S₀.
2. At each depth step (default `max_depth=1`), expand each subspace in the beam by sampling `exp_factor=20` candidate extensions. Each extension adds one (column, value) filter, where the column is sampled uniformly from unused columns and the value is sampled with probability proportional to `log(1 + count)`.
3. If an LLM client is available, the LLM is asked to suggest the most semantically meaningful filter columns for the given (B, M) pair. Suggested columns are preferred with probability `w_llm=0.5`; otherwise a random column is chosen.
4. Each candidate subspace is scored using the pattern's scoring function.
5. The top `beam_width=20` candidates by score are retained for the next depth step.
6. Subspaces with score below the threshold are discarded.

For Distribution Difference, the score is the Jensen-Shannon divergence between the full-dataset view and the subspace view, rather than a function of the subspace view values alone.

At most 2 subspace insights are accepted per (card, pattern) combination.

### 5.6 View Computation

The view `view(D_S, B, M)` is computed by:

1. Applying subspace filters to the dataframe (all conditions joined by AND, using string equality).
2. Grouping the filtered dataframe by the breakdown column B.
3. Applying the aggregation function specified in M (`SUM`, `MEAN`, `COUNT`, `MIN`, `MAX`).
4. Coercing the result to numeric, dropping non-numeric entries.

Column names in Insight Cards are resolved to actual dataframe column names using a multi-strategy matching procedure: exact match → space-to-underscore normalization → case-insensitive → partial containment → token overlap. This makes the pipeline robust to naming inconsistencies between card generation and the actual CSV.

### 5.7 Deduplication and Output Limiting

All candidate insights collected across all cards are deduplicated and limited in two passes:

1. **Structural deduplication:** For each `(question, B, M, pattern)` group, at most 1 global (empty subspace) insight and at most 2 subspace insights are kept, each selected by highest score.

2. **Per-question limit:** Each source question retains at most `max_insights_per_question=3` insights. Selection prioritizes pattern diversity — the best-scoring insight for each pattern type is chosen first (Round 1), then remaining slots are filled by score (Round 2).

### 5.8 Natural Language Explanation and Visualization

For each accepted insight, a short natural language explanation is generated from a template parameterized by (B, M, S, P). Each pattern has its own template phrasing (trend, outstanding value, attribution, distribution difference), produced in English or Vietnamese depending on the language setting.

A chart is generated for each insight matched to its pattern type: line chart for Trend, bar chart for Outstanding Value and Attribution, and a paired bar chart comparing subspace vs. overall distributions for Distribution Difference.

### 5.9 Output

A JSON list of insight summaries, each containing `question`, `explanation`, `plot_path`, and an `insight` object with fields `breakdown`, `measure`, `subspace`, `pattern`, `score`, `view_labels`, and `view_values`.

---

## 6. Configuration

| Parameter | Default | Description |
|---|---|---|
| **QUGEN** | | |
| Model | gpt-5.4 | Configurable via `QUGEN_LLM_MODEL` env var |
| Temperature | 1.1 | Higher temperature increases output diversity |
| Iterations | 10 | Number of generation–filter cycles |
| Samples per iteration | 3 | Independent LLM calls per prompt |
| Questions per prompt | 10 | Requested cards per LLM call |
| In-context examples | 6 | Cards from prior iterations used as few-shot examples |
| Schema relevance threshold | 0.25 | Cosine similarity (all-MiniLM-L6-v2) |
| Deduplication threshold | 0.85 | Cosine similarity above which cards are considered duplicate |
| **ISGEN** | | |
| Beam width | 20 | Candidates retained per beam step |
| Expansion factor | 20 | Random subspace extensions tried per beam node |
| Max subspace depth | 1 | Maximum number of filters per subspace |
| LLM guidance weight | 0.5 | Probability of preferring LLM-suggested filter columns |
| Threshold scale | 0.7 | Multiplier applied to all pattern thresholds |
| Max insights per card | 3 | Basic insights kept per Insight Card |
| Max overall per key | 1 | Global insights kept per (question, B, M, pattern) |
| Max subspace per key | 2 | Subspace insights kept per (question, B, M, pattern) |
| Max insights per question | 3 | Final insights retained per source question |

---

## 7. Limitations

- **LLM dependency:** QUGEN output varies across runs due to temperature > 0; set temperature = 0 for reproducible benchmarks
- **No causal inference:** patterns are observational and correlational only
- **Subspace depth:** depth is limited to 1 by default, so insights involving multi-dimensional data segments are not explored
- **Simple-question filter:** the heuristic version (no SQL execution) may retain some trivial questions and discard some valid ones
- **Column resolution:** the token-overlap fallback for column name matching may map to an incorrect column in datasets with similar column names

---

## Appendix: System Requirements

**Python:** 3.9+  
**Dependencies:** `pandas`, `numpy`, `scipy`, `matplotlib`, `openai`, `sentence-transformers`, `pymannkendall`, `python-dotenv`  
**Hardware:** 4 GB RAM minimum; sentence-transformers model (~90 MB) downloaded on first run  
**Network:** Required for OpenAI API access  
**Estimated runtime:** 3–8 minutes depending on number of iterations, dataset size, and API latency
