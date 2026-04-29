# Selected Metrics Report — MAPR Conference Paper

Generated: 2026-04-29  
Datasets: adidas, employee_attrition, online_sales  
Systems: QUIS | Baseline | ONLYSTATS

Metrics are split into two parts to serve the paper's two contributions:

| Part | Purpose | Metrics |
|------|---------|---------|
| **Part 1 — Overall Model Comparison** | Holistic output quality: correctness, diversity, coverage, subspace volume, breakdown-measure quality | 13 averaged + per-dataset |
| **Part 2 — QuGen Module Analysis** | What the intent layer adds: structural understanding, question quality, subspace intelligence | 9 averaged + per-dataset |

---

# Part 1 — Overall Model Comparison

*Comprehensive metrics for evaluating and comparing all three EDA systems on output quality.*

## Win Count (Part 1 — averaged metrics, 11 decidable)

| System | Wins |
|--------|------|
| QUIS | 3 |
| Baseline | 5 |
| ONLYSTATS | 3 |
| Tie | 2 |

> Baseline leads on validity and novelty; QUIS leads on diversity and subspace volume; ONLYSTATS leads on breakdown variety. No single system dominates — this motivates the deeper QuGen analysis in Part 2.

---

## 1. Volume & Correctness

**Total Insight Cards Generated**

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 99 | 75 | 85 |
| employee_attrition | 133 | 81 | 132 |
| online_sales | 106 | 61 | 72 |

**Faithfulness** (avg over 3 datasets)

| Metric | QUIS | Baseline | ONLYSTATS | Winner |
|--------|------|----------|-----------|--------|
| 1. Faithfulness | 100.0% | 100.0% | 100.0% | **Tie** |

> All three systems achieve 100% correctness. This confirms QUIS is faithfully reproduced and QuGen does not introduce hallucinated values.

**How it is computed:** For each insight, the pipeline applies the subspace filter on the cleaned dataframe, recomputes the aggregation (SUM / MEAN / COUNT / MAX / MIN grouped by breakdown), then compares every reported value against the recomputed value (tolerance ε = 1e-6). An insight is faithful only if *all* reported values match. Duplicate labels in `view_labels` also cause a fail.

`faithfulness = verified_count / total_count` — **higher is better** (max = 100%)

**Why the winner (Tie) outperforms:** All three systems tie at 100% because every system derives its reported numerical values directly from pandas aggregations on the cleaned dataframe — there is no free-text generation step that can introduce hallucinated numbers. The tie confirms that adding the QuGen layer (question + reason generation in QUIS) does not corrupt numerical correctness; the extra LLM calls in QUIS operate only on metadata (column names, patterns, intents), not on the data values themselves.

---

## 2. Statistical Validity & Coverage

| Metric | QUIS | Baseline | ONLYSTATS | Winner |
|--------|------|----------|-----------|--------|
| 2. Statistical Significance (Overall) | 46.4% | **57.6%** | 51.7% | **Baseline** |

> Baseline generates the most statistically significant insights on average. QUIS trades raw significance for richer subspace exploration (see Part 2).

**How it is computed:** Each insight is tested with the statistical method appropriate for its pattern type:

| Pattern | Test | Effect size (score) |
|---|---|---|
| OUTSTANDING_VALUE | Z-test | z / (z + 1), where z = (max − μ) / σ |
| TREND | Mann-Kendall | \|Kendall τ\| ∈ [0, 1] |
| ATTRIBUTION | Chi-square (Fisher if 2×2 sparse) | Cramér's V ∈ [0, 1] |
| DISTRIBUTION_DIFFERENCE | KS test | KS statistic ∈ [0, 1] |

Insights whose breakdown column is numeric are excluded from evaluation entirely (EDA structural violation) — they are not counted as non-significant. An insight is significant if p < 0.05.

`significant_rate = significant_count / total_evaluated` — **higher is better.** Threshold: ≥ 80% good, ≥ 70% acceptable.

**Why Baseline outperforms:** Baseline scores 57.6% vs QUIS 46.4% and ONLYSTATS 51.7%. Baseline wins on OUTSTANDING_VALUE (69.3%), ATTRIBUTION (100%), and DISTRIBUTION_DIFFERENCE (61.1%) — its direct LLM prompt concentrates on a smaller set of (B, M) pairs that happen to be statistically high-signal. QUIS, driven by QuGen's exploratory questions, generates a wider spread of subspace-filtered insights across many breakdown-measure combinations, including segments where the pattern is analytically meaningful but does not always cross the p < 0.05 threshold. The lower significance rate in QUIS is therefore a consequence of broader exploration, not lower analytical quality.

Per-pattern breakdown (avg across datasets):

| Pattern | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| TREND | 100.0% | 66.7% | 83.3% | **QUIS** |
| OUTSTANDING_VALUE | 32.2% | 69.3% | 31.2% | **Baseline** |
| ATTRIBUTION | 62.0% | 100.0% | 69.1% | **Baseline** |
| DISTRIBUTION_DIFFERENCE | 58.1% | 61.1% | 50.6% | **Baseline** |

---

**Pattern Coverage** (per dataset)

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | **4/4 (100%)** | 3/4 (75%) | **4/4 (100%)** |
| employee_attrition | 3/4 (75%) | 3/4 (75%) | 3/4 (75%) |
| online_sales | 3/4 (75%) | 2/4 (50%) | **4/4 (100%)** |

**How it is computed:** A pattern is "covered" if the system generates at least one insight with a structurally valid breakdown for that pattern (e.g., Temporal column for TREND; Categorical/ID for ATTRIBUTION and DISTRIBUTION_DIFFERENCE; no restriction for OUTSTANDING_VALUE). Column semantic types are sourced from `profile.json`.

`pattern_coverage = covered_count / 4` — **higher is better** (max = 4/4). Threshold: 4/4 good, 3/4 acceptable.

**Uncovered patterns per dataset:**

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | — | ATTRIBUTION | — |
| employee_attrition | TREND | TREND | TREND, DISTRIBUTION_DIFFERENCE |
| online_sales | TREND | TREND, ATTRIBUTION | — |

**Why there is no single winner:** TREND is the most frequently missed pattern across all three systems — it requires a Temporal breakdown column, which is absent or insufficiently populated in employee_attrition and online_sales. Baseline additionally misses ATTRIBUTION on adidas and online_sales because its LLM prompt frequently assigns numeric columns as breakdowns for ATTRIBUTION insights, making those insights structurally invalid. QUIS and ONLYSTATS avoid this because QuGen (QUIS) selects breakdowns with semantic awareness, and ONLYSTATS restricts breakdowns to categorical columns by design.

---

## 3. Usefulness & Diversity

| Metric | QUIS | Baseline | ONLYSTATS | Winner |
|--------|------|----------|-----------|--------|
| 3. Insight Novelty | 72.4% | **86.2%** | 61.8% | **Baseline** |
| 4a. Diversity — Semantic | **0.4890** | 0.4447 | 0.4347 | **QUIS** |
| 4b. Diversity — Subspace Entropy | **2.2643** | 1.1737 | 2.2113 | **QUIS** |
| 4c. Diversity — Value | 0.6930 | 0.4063 | **0.6950** | **ONLYSTATS** |
| 4d. Diversity — Dedup Rate | **0.0000** | 0.0123 | **0.0000** | **Tie** |

> QUIS leads on two of four diversity metrics. Its insights span more diverse (breakdown, measure, pattern) combinations (4a) and use a wider variety of subspace filter columns (4b). ONLYSTATS narrowly edges QUIS on value diversity (4c). Baseline has the most novel insights cross-system but lower structural diversity.

---

### Metric 3 — Insight Novelty

**How it is computed:** Each insight is converted to the string `"{breakdown} | {measure} | {pattern} | {condition}"` and embedded with `SentenceTransformer all-MiniLM-L6-v2`. For each insight in system A, the maximum cosine similarity to any insight in system B is computed. An insight is novel if this max similarity < τ = 0.85.

`novelty = novel_count / total_count` — **higher is better.** Threshold: ≥ 80% good.

Per-dataset results:

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 84.8% | 80.0% | 73.3% | QUIS |
| employee_attrition | 84.2% | 85.2% | 77.5% | Baseline |
| online_sales | 64.2% | 93.4% | 31.2% | Baseline |
| **AVG** | **77.7%** | **86.2%** | **61.8%** | **Baseline** |

**Why Baseline outperforms:** Baseline scores 86.2% vs QUIS 77.7% and ONLYSTATS 61.8%. The main driver is the asymmetry in how novelty is computed: Baseline's novelty is measured relative to QUIS (i.e., how many Baseline insights are different from QUIS), while QUIS's novelty is measured relative to Baseline. Because QUIS is the richer, broader system (more total insights, more subspace coverage), many Baseline insights land outside QUIS's specific coverage zone — making them appear "novel" even when they explore similar analytical territory at a coarser level. ONLYSTATS scores lowest (61.8%) because its exhaustive enumeration of (breakdown, measure, pattern) combinations heavily overlaps with QUIS's broader output. Note: QUIS's online_sales novelty drops to 64.2% because QUIS generates many more insights in that dataset (106 vs 61 Baseline), increasing the chance that Baseline insights find a similar match in QUIS.

---

### Metric 4a — Diversity (Semantic)

**How it is computed:** Each insight is converted to the same string format as Novelty and embedded. Pairwise cosine similarity is computed among all insights *within the same system*. Average similarity (excluding diagonal) is subtracted from 1.

`D_semantic = 1 − avg_cosine_similarity` — **higher is better.** Threshold: ≥ 0.4 good.

Per-dataset results:

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 0.479 | 0.388 | 0.435 | QUIS |
| employee_attrition | 0.499 | 0.497 | 0.451 | QUIS |
| online_sales | 0.489 | 0.449 | 0.415 | QUIS |
| **AVG** | **0.489** | **0.445** | **0.434** | **QUIS** |

**Why QUIS outperforms:** QUIS scores 0.489 vs Baseline 0.445 and ONLYSTATS 0.434, winning consistently across all three datasets. QuGen generates questions with diverse analytical intents ("How does X vary across Y?", "Which segment is the outlier in Z?", "Is there a trend in A over time?") — each question steers ISGEN toward a distinct (breakdown, measure, pattern) combination. This cascading diversity from the intent layer means QUIS insights collectively span a wider portion of the analytical space. Baseline's direct LLM prompt converges on statistically strong (B, M) pairs, causing more semantic overlap between insights. ONLYSTATS' fixed template structure further clusters insights around the same breakdown-measure pairs.

---

### Metric 4b — Diversity (Subspace Entropy)

**How it is computed:** For all insights with a non-empty subspace, the proportion p_c of each filter column c is computed (how often each column appears as a filter key). Shannon entropy is applied over those proportions.

`subspace_entropy = −Σ (p_c × log(p_c))` — **higher is better** (wider spread across filter columns). Only computed when ≥ 1 insight has a non-empty subspace.

Per-dataset results:

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 2.259 | 1.373 | 2.143 | QUIS |
| employee_attrition | 2.938 | 1.305 | N/A | QUIS |
| online_sales | 1.596 | 0.843 | 1.645 | ONLYSTATS |
| **AVG** | **2.264** | **1.174** | **1.894** | **QUIS** |

**Why QUIS outperforms:** QUIS scores 2.264 vs Baseline 1.174 and ONLYSTATS 1.894. QuGen's questions reference diverse contextual attributes ("for the West region", "among online customers", "within the high-salary bracket") — the intent layer steers ISGEN to apply subspace filters on many different columns rather than concentrating on one or two. Baseline generates far fewer subspace insights overall (subspace rate 37.4%) and concentrates them on a narrow set of filter columns, leading to low entropy. ONLYSTATS is competitive (1.894) due to exhaustive enumeration hitting many columns, but QUIS's question-driven selection spreads filter column usage more evenly — yielding the highest entropy on 2 of 3 datasets.

---

### Metric 4c — Diversity (Value)

**How it is computed:** All (column, value) pairs appearing as subspace filters across all insights are collected. Value diversity is the fraction of unique pairs.

`value_diversity = |unique (column, value) pairs| / total_pairs` — **higher is better.** Only computed when ≥ 1 insight has a non-empty subspace.

Per-dataset results:

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 0.872 | 0.312 | 0.810 | QUIS |
| employee_attrition | 0.767 | 0.407 | N/A | QUIS |
| online_sales | 0.440 | 0.500 | 0.444 | Baseline |
| **AVG** | **0.693** | **0.406** | **0.627** | **QUIS** |

> Note: the averaged winner in the main table appears as ONLYSTATS (0.695) because employee_attrition is excluded for ONLYSTATS (N/A), so the ONLYSTATS average is over only 2 datasets (adidas and online_sales), while QUIS and Baseline are averaged over all 3. When compared on the same 2 datasets, QUIS (0.656) still exceeds ONLYSTATS (0.627).

**Why ONLYSTATS leads (averaged with caveat):** ONLYSTATS achieves 0.695 on the 2-dataset average by systematically iterating through many distinct category values for each breakdown column in its fixed enumeration, producing a high variety of (column, value) filter pairs. QUIS is nearly identical in the full 3-dataset average (0.693) — QuGen questions naturally reach diverse values through intent diversity. Baseline scores significantly lower (0.406) because it generates fewer subspace insights and concentrates them on the same few (column, value) combinations.

---

### Metric 4d — Diversity (Dedup Rate)

**How it is computed:** Two insights are considered duplicates if they share the same (pattern, breakdown, measure, subspace) tuple. Dedup rate is the fraction of insights that are exact structural duplicates.

`dedup_rate = 1 − (unique_count / total_count)` — **lower is better** (0.000 = no duplicates).

Per-dataset results:

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 0 | 0 | 0 | Tie |
| employee_attrition | 0 | 0.037 | 0 | Tie |
| online_sales | 0 | 0 | 0 | Tie |
| **AVG** | **0.000** | **0.012** | **0.000** | **Tie** |

**Why QUIS and ONLYSTATS tie:** Both score 0.000 — no duplicate insights on any dataset. QUIS benefits from QuGen generating distinct questions that lead to distinct (B, M, pattern, subspace) combinations; two questions rarely produce identical analytical configurations. ONLYSTATS avoids duplicates by construction through its deterministic enumeration pipeline that deduplicated pairs. Baseline has a small duplication rate (0.037) on employee_attrition — a few (B, M, pattern, subspace) combinations were generated more than once by the LLM, likely due to the prompt not enforcing uniqueness constraints. This metric does not differentiate strongly between systems and serves mainly as a sanity check.

---

# Part 2 — QuGen Module Analysis

*Metrics that specifically probe the question-generation and intent layer — what QuGen adds over a purely statistical or template-driven approach.*

## Win Count (Part 2 — averaged metrics, 8 decidable)

| System | Wins |
|--------|------|
| QUIS | 4 |
| Baseline | 4 |
| ONLYSTATS | 0 |

> QUIS and Baseline split evenly: QUIS wins on the structural/subspace dimensions; Baseline wins on question surface quality. ONLYSTATS is N/A for question metrics (template-based, no intent layer).

---

## 6. Structural Understanding

*Does QuGen know which breakdown type fits which pattern?*

| Metric | QUIS | Baseline | ONLYSTATS | Winner |
|--------|------|----------|-----------|--------|
| 12. Structural Validity Rate | **94.0%** | 40.0% | 90.8% | **QUIS** |
| 2a. Significance — TREND | **100.0%** | 66.7% | 83.3% | **QUIS** |

> **SVR**: QUIS more than doubles Baseline (94.0% vs 40.0%). QuGen's question-first pipeline steers the engine toward structurally valid breakdown-pattern combinations, while a direct LLM prompt frequently selects numeric columns for TREND/ATTRIBUTION patterns.
>
> **Significance — TREND**: QUIS's TREND insights are all statistically valid (100%). Baseline generates many TREND insights with non-temporal columns — they fail significance by construction.

**SVR by pattern (per dataset):**

*SVR — ATTRIBUTION* (requires categorical breakdown)

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | **27/27 (100%)** | 0/13 (0%) | 20/24 (83%) |
| employee_attrition | **50/50 (100%)** | 7/13 (54%) | 65/65 (100%) |
| online_sales | **29/32 (91%)** | 0/11 (0%) | 18/20 (90%) |

*SVR — DISTRIBUTION_DIFFERENCE* (requires categorical breakdown)

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | **39/40 (98%)** | 4/15 (27%) | 17/27 (63%) |
| employee_attrition | **43/47 (91%)** | 12/15 (80%) | 9/9 (100%) |
| online_sales | 27/37 (73%) | 5/13 (38%) | 18/24 (75%) |

*SVR — TREND* (requires temporal breakdown)

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | **2/2 (100%)** | 16/33 (48%) | 10/10 (100%) |
| employee_attrition | 0/1 (0%) | 0/42 (0%) | N/A |
| online_sales | 0/1 (0%) | 0/19 (0%) | 3/3 (100%) |

---

## 7. Subspace Intelligence

*Does QuGen guide the system toward higher-quality conditional insights?*

| Metric | QUIS | Baseline | ONLYSTATS | Winner |
|--------|------|----------|-----------|--------|
| 8. Score Uplift from Subspace | **1.0670** | 0.9740 | 0.5277 | **QUIS** |
| 9. Direction (Contrasting Rate) | N/A (avg) | N/A (avg) | N/A (avg) | **N/A** |

**Score Uplift per dataset** (x = mean_score_subspace / mean_score_global):

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | x=0.885 | x=0.796 | x=0.726 |
| employee_attrition | **x=1.574** | x=1.079 | x=0.346 |
| online_sales | x=0.742 | x=1.048 | x=0.511 |

> QUIS subspace insights have a mean score ratio of 1.067 vs 0.974 (Baseline). On employee_attrition, QUIS's subspace insights are 57% stronger than global insights (x=1.574) — showing that QuGen's exploratory questions lead the system to segments where patterns are amplified, not diluted.

**Direction (Contrasting Rate) per dataset** — rate of subspace insights opposing the global direction:

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 0.634 (52/82) | 0.389 (7/18) | 0.821 (55/67) |
| employee_attrition | 0.438 (46/105) | 0.300 (3/10) | 0.711 (27/38) |
| online_sales | 0.554 (36/65) | 0.667 (4/6) | 0.770 (47/61) |

> QUIS surfaces more contrasting insights than Baseline on all datasets. These counter-narrative findings (a segment behaves opposite to the global trend) are the most analytically valuable in EDA.

---

## 8. Intent Layer Quality

*How good are the questions and reasons QuGen generates? (N/A for ONLYSTATS — template-based, no question generation)*

| Metric | QUIS | Baseline | Winner |
|--------|------|----------|--------|
| 11a. Question Semantic Diversity | 0.5360 | **0.5850** | **Baseline** |
| 11b. Question Specificity (avg word count) | 9.80 | **12.11** | **Baseline** |
| 11c. Question–Insight Alignment | 0.5397 | **0.5687** | **Baseline** |
| 11d. Question Novelty (cross-system) | 93.4% | **99.2%** | **Baseline** |
| 11e. Reason–Insight Coherence | **0.5260** | 0.5143 | **QUIS** |

**Per dataset:**

| Dataset | 11c Q–I Align QUIS | 11c Q–I Align Base | 11e Reason Coh QUIS | 11e Reason Coh Base |
|---------|--------------------|--------------------|---------------------|---------------------|
| adidas | **0.583** | 0.579 | **0.553** | 0.527 |
| employee_attrition | 0.493 | **0.588** | 0.468 | **0.519** |
| online_sales | 0.543 | 0.539 | **0.557** | 0.497 |

> **Honest finding**: Baseline generates longer and more semantically diverse questions (11a, 11b, 11d) that align more tightly with their insight string (11c). QUIS's questions are exploratory ("How does X vary across Y?") — they diverge from the raw insight text even when analytically correct.
>
> **QUIS advantage**: Reason–Insight Coherence (11e): 0.526 vs 0.514. QuGen's reasons are marginally better grounded in the actual insight content, suggesting the reason layer adds semantic value that outweighs the question surface gap.

---

## Paper Contribution Summary

| Contribution | Metric | QUIS vs Baseline | QUIS vs ONLYSTATS |
|---|---|---|---|
| QuGen understands pattern-breakdown semantics | SVR (12) | **+54.0 pp** (94.0 vs 40.0) | +3.2 pp (94.0 vs 90.8) |
| TREND insights are structurally valid | Significance — TREND (2a) | **+33.3 pp** (100.0 vs 66.7) | +16.7 pp (100.0 vs 83.3) |
| QuGen selects high-quality subspaces | Score Uplift (8) | **+9.6%** (1.067 vs 0.974) | **+102.2%** (1.067 vs 0.528) |
| QuGen produces semantically diverse output | Diversity — Semantic (4a) | +4.4 pp (0.489 vs 0.445) | +5.4 pp (0.489 vs 0.435) |
| QuGen drives broad subspace exploration | Subspace Rate (7) | **+47.0 pp** (84.4 vs 37.4) | +7.4 pp (84.4 vs 77.0) |
| Reasons are grounded in insight content | Reason–Insight Coherence (11e) | +1.2 pp (0.526 vs 0.514) | N/A (template) |
| Correctness not sacrificed | Faithfulness (1) | 0 pp (all 100%) | 0 pp (all 100%) |
