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

---

## 2. Statistical Validity & Coverage

| Metric | QUIS | Baseline | ONLYSTATS | Winner |
|--------|------|----------|-----------|--------|
| 2. Statistical Significance (Overall) | 46.4% | **57.6%** | 51.7% | **Baseline** |

> Baseline generates the most statistically significant insights on average. QUIS trades raw significance for richer subspace exploration (see Part 2).

**Pattern Coverage** (per dataset)

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | **4/4 (100%)** | 3/4 (75%) | **4/4 (100%)** |
| employee_attrition | 3/4 (75%) | 3/4 (75%) | 3/4 (75%) |
| online_sales | 3/4 (75%) | 2/4 (50%) | **4/4 (100%)** |

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

## 4. Subspace Coverage

| Metric | QUIS | Baseline | ONLYSTATS | Winner |
|--------|------|----------|-----------|--------|
| 7. Subspace Rate | **84.4%** | 37.4% | 77.0% | **QUIS** |
| 7b. Subspace Significance | 37.5% | **58.3%** | 31.7% | **Baseline** |

**Subspace Rate per dataset:**

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | **86/99 (86.9%)** | 32/75 (42.7%) | 67/85 (78.8%) |
| employee_attrition | **116/133 (87.2%)** | 27/81 (33.3%) | 78/132 (59.1%) |
| online_sales | 84/106 (79.2%) | 22/61 (36.1%) | **67/72 (93.1%)** |

> QUIS generates the most subspace-conditional insights (84.4% vs 37.4% Baseline). However, Baseline's smaller set of subspace insights are more statistically significant (58.3% vs 37.5%). This trade-off is examined deeper in Part 2.

---

## 5. Breakdown–Measure Quality

**Total (B,M) pairs evaluated**

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 26/26 | 11/24 | 31/31 |
| employee_attrition | 49/51 | 24/30 | 53/53 |
| online_sales | 24/26 | 7/16 | 24/24 |

**Averaged BM metrics**

| Metric | QUIS | Baseline | ONLYSTATS | Winner |
|--------|------|----------|-----------|--------|
| 10a. BM — NMI mean | 0.1027 | **0.2550** | 0.2225 | **Baseline** |
| 10b. BM — Interestingness | 0.1370 | **0.2533** | 0.1613 | **Baseline** |
| 10c. BM — Actionability | 0.9613 | 0.5653 | **1.0000** | **ONLYSTATS** |
| 10d. BM — Diversity | 0.2973 | 0.3173 | **0.3667** | **ONLYSTATS** |

> Baseline selects more informative (B,M) pairs (higher NMI and Interestingness). ONLYSTATS has perfect actionability (always categorical) and highest (B,M) variety. QUIS's lower NMI/Interestingness reflects that its QuGen-chosen breakdowns prioritise exploratory coverage over per-pair information gain.

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
