# Aggregated 3-Way Evaluation Report

Generated: 2026-05-06 22:55  
Datasets: adidas, employee_attrition, online_sales  
Systems: QUIS | Baseline | ONLYSTATS

> **Aggregation rules**
> - *Averaged metrics* (%) — mean across datasets reported in the summary table.
> - *Per-dataset metrics* (counts, fractions, text) — kept separately below.

## Win Count Summary (averaged metrics, 26 total)

| System | Wins |
|--------|------|
| QUIS | 8 |
| Baseline | 12 |
| ONLYSTATS | 3 |

## Averaged Metrics (mean across datasets)

### Core & Efficiency

| Metric | QUIS | Baseline | ONLYSTATS | Winner | Description |
|--------|------|----------|-----------|--------|-------------|
| 1. Faithfulness | 100.0% | 100.0% | 100.0% | **Tie** | Correctness - đúng dữ liệu |
| 2. Statistical Significance (Overall) | 46.4% | 57.6% | 51.7% | **Baseline** | Validity - pattern-averaged (fair comparison) |
| 2a. Significance — TREND | 100.0% | 66.7% | 83.3% | **QUIS** | Validity - TREND pattern |
| 2a. Significance — OUTSTANDING_VALUE | 32.2% | 69.3% | 31.2% | **Baseline** | Validity - OUTSTANDING_VALUE pattern |
| 2a. Significance — ATTRIBUTION | 62.0% | 100.0% | 69.1% | **Baseline** | Validity - ATTRIBUTION pattern |
| 2a. Significance — DISTRIBUTION_DIFFERENCE | 58.1% | 61.1% | 50.6% | **Baseline** | Validity - DISTRIBUTION_DIFFERENCE pattern |
| 3. Insight Novelty | 72.4% | 86.2% | 61.8% | **Baseline** | Usefulness - khác baseline (from pairwise comparison results) |
| 4a. Diversity — Semantic | 0.4890 | 0.4447 | 0.4347 | **QUIS** | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy | 2.2643 | 1.1737 | 2.2113 | **QUIS** | Entropy of subspace filter columns used |
| 4c. Diversity — Value | 0.6930 | 0.4063 | 0.6950 | **ONLYSTATS** | Unique (column, value) pairs in subspace / total |
| 4d. Diversity — Dedup Rate | 0.0000 | 0.0123 | 0.0000 | **Tie** | Duplicate rate — lower is better |
### Subspace Deep-dive

| Metric | QUIS | Baseline | ONLYSTATS | Winner | Description |
|--------|------|----------|-----------|--------|-------------|
| 7. Subspace Rate | 84.4% | 37.4% | 77.0% | **QUIS** | Insights with subspace filter / total |
| 7a. Subspace Faithfulness | 100.0% | 100.0% | 100.0% | **Tie** | Faithfulness restricted to subspace insights |
| 7b. Subspace Significance | 37.5% | 58.3% | 31.7% | **Baseline** | Significance restricted to subspace insights |
| 8. Score Uplift from Subspace | 1.0670 | 0.9743 | 0.5277 | **QUIS** | Δ = mean(score|subspace) - mean(score|no-subspace) |
| 9. Simpson's Paradox Rate (SPR) | 30.1% | 18.9% | 25.4% | **QUIS** | Rate of statistically significant pattern reversals (p<0.05) — true Simpson's Paradox cases |
### Intent Layer Quality

| Metric | QUIS | Baseline | ONLYSTATS | Winner | Description |
|--------|------|----------|-----------|--------|-------------|
| 10a. BM — NMI mean | 0.1027 | 0.2550 | 0.2225 | **Baseline** | Mean NMI over categorical-B pairs |
| 10b. BM — Interestingness | 0.1370 | 0.2533 | 0.1613 | **Baseline** | Mean Coverage×EffectSize over categorical-B pairs |
| 10c. BM — Actionability | 0.9613 | 0.5653 | 1.0000 | **ONLYSTATS** | % pairs with categorical breakdown |
| 10d. BM — Diversity | 0.2973 | 0.3173 | 0.3667 | **ONLYSTATS** | Unique (B,M) pairs / total insights |
| 11a. Question Semantic Diversity | 0.5360 | 0.5850 | N/A | **Baseline** | 1 - mean cosine sim of question embeddings (within-system); N/A for ONLYSTATS (template) |
| 11b. Question Specificity | 9.7967 | 12.1133 | N/A | **Baseline** | Avg word count per question (mean ± std) — higher = more specific; N/A for ONLYSTATS (template) |
| 11c. Question–Insight Alignment | 0.5397 | 0.5687 | N/A | **Baseline** | Mean cosine(Embed(question), Embed(insight)) — control metric; N/A for ONLYSTATS (template) |
| 11d. Question Novelty (cross-system) | 93.4% | 99.2% | N/A | **Baseline** | % of questions with cross-system max cosine sim < 0.85 (from pairwise comparison results) |
| 11e. Reason–Insight Coherence | 0.5260 | 0.5143 | N/A | **QUIS** | Mean cosine(Embed(reason), Embed(insight)) — reason grounding |
| 12. Structural Validity Rate | 94.0% | 40.0% | 90.8% | **QUIS** | % insights with breakdown type valid for their pattern — measures QuGen structural understanding |

## Per-Dataset Detail (non-averaged metrics)

### Core & Efficiency

**0. Total insights** — Total insight cards generated

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 99 | 75 | 85 |
| employee_attrition | 133 | 81 | 132 |
| online_sales | 106 | 61 | 72 |

**2b. Pattern Coverage** — Patterns with ≥1 structurally valid insight / 4 total patterns

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 4/4 (100%) | 3/4 (75%) | 4/4 (100%) |
| employee_attrition | 3/4 (75%) | 3/4 (75%) | 3/4 (75%) |
| online_sales | 3/4 (75%) | 2/4 (50%) | 4/4 (100%) |

**2b1. Uncovered Patterns** — Patterns with 0 valid insights (breakdown type mismatch)

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | — | ATTRIBUTION | — |
| employee_attrition | TREND | TREND | TREND |
| online_sales | TREND | TREND, ATTRIBUTION | — |

### Intent Layer Quality

**10. Total (B,M) pairs evaluated** — Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness)

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 26/26 | 11/24 | 31/31 |
| employee_attrition | 49/51 | 24/30 | 53/53 |
| online_sales | 24/26 | 7/16 | 24/24 |

**12a. SVR — OUTSTANDING_VALUE** — Structural validity for OUTSTANDING_VALUE pattern

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 30/30 | 14/14 | 24/24 |
| employee_attrition | 35/35 | 11/11 | 58/58 |
| online_sales | 36/36 | 18/18 | 25/25 |

**12a. SVR — TREND** — Structural validity for TREND pattern

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 2/2 | 16/33 | 10/10 |
| employee_attrition | 0/1 | 0/42 | N/A |
| online_sales | 0/1 | 0/19 | 3/3 |

**12a. SVR — ATTRIBUTION** — Structural validity for ATTRIBUTION pattern

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 27/27 | 0/13 | 20/24 |
| employee_attrition | 50/50 | 7/13 | 65/65 |
| online_sales | 29/32 | 0/11 | 18/20 |

**12a. SVR — DISTRIBUTION_DIFFERENCE** — Structural validity for DISTRIBUTION_DIFFERENCE pattern

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 39/40 | 4/15 | 17/27 |
| employee_attrition | 43/47 | 12/15 | 9/9 |
| online_sales | 27/37 | 5/13 | 18/24 |

## Appendix — Full Results Per Dataset

### adidas

| Group | Metric | QUIS | Baseline | ONLYSTATS | Winner |
|-------|--------|------|----------|-----------|--------|
| Core & Efficiency | 0. Total insights | 99 | 75 | 85 | N/A |
| Core & Efficiency | 1. Faithfulness | 100.0% | 100.0% | 100.0% | Tie |
| Core & Efficiency | 2. Statistical Significance (Overall) | 83.4% | 73.2% | 76.2% | QUIS |
| Core & Efficiency | 2a. Significance — TREND | 100.0% (2) | 100.0% (16) | 100.0% (10) | Tie |
| Core & Efficiency | 2a. Significance — OUTSTANDING_VALUE | 40.0% (30) | 92.9% (14) | 41.7% (24) | Baseline |
| Core & Efficiency | 2a. Significance — ATTRIBUTION | 96.0% (25) | N/A | 100.0% (24) | ONLYSTATS |
| Core & Efficiency | 2a. Significance — DISTRIBUTION_DIFFERENCE | 97.4% (39) | 100.0% (4) | 63.0% (27) | Baseline |
| Core & Efficiency | 2b. Pattern Coverage | 4/4 (100%) | 3/4 (75%) | 4/4 (100%) | Tie |
| Core & Efficiency | 2b1. Uncovered Patterns | — | ATTRIBUTION | — | N/A |
| Core & Efficiency | 3. Insight Novelty | 79.8% | 80.0% | 72.9% | Baseline |
| Core & Efficiency | 4a. Diversity — Semantic | 0.479 | 0.388 | 0.439 | QUIS |
| Core & Efficiency | 4b. Diversity — Subspace Entropy | 2.259 | 1.373 | 2.027 | QUIS |
| Core & Efficiency | 4c. Diversity — Value | 0.872 | 0.312 | 0.866 | QUIS |
| Core & Efficiency | 4d. Diversity — Dedup Rate | 0 | 0 | 0 | Tie |
| Subspace Deep-dive | 7. Subspace Rate | 86/99 (86.9%) | 32/75 (42.7%) | 67/85 (78.8%) | QUIS |
| Subspace Deep-dive | 7a. Subspace Faithfulness | 100.0% | 100.0% | 100.0% | Tie |
| Subspace Deep-dive | 7b. Subspace Significance | 44.0% | 75.0% | 50.0% | Baseline |
| Subspace Deep-dive | 8. Score Uplift from Subspace | Δ=-0.043, x=0.885 | Δ=-0.135, x=0.796 | Δ=-0.126, x=0.726 | QUIS |
| Subspace Deep-dive | 9. Simpson's Paradox Rate (SPR) | 27.9% (0/24 sig) | 25.0% (0/8 sig) | 37.3% (0/25 sig) | ONLYSTATS |
| Intent Layer Quality | 10. Total (B,M) pairs evaluated | 26/26 | 11/24 | 31/31 | N/A |
| Intent Layer Quality | 10a. BM — NMI mean | 0.094 | 0.331 | 0.217 | Baseline |
| Intent Layer Quality | 10b. BM — Interestingness | 0.077 | 0.090 | 0.068 | Baseline |
| Intent Layer Quality | 10c. BM — Actionability | 1.000 | 0.458 | 1.000 | Tie |
| Intent Layer Quality | 10d. BM — Diversity | 0.263 | 0.320 | 0.365 | ONLYSTATS |
| Intent Layer Quality | 11a. Question Semantic Diversity | 0.493 | 0.548 | N/A | Baseline |
| Intent Layer Quality | 11b. Question Specificity | 9.15 ± 1.40 | 12.75 ± 5.03 | N/A | Baseline |
| Intent Layer Quality | 11c. Question–Insight Alignment | 0.583 | 0.579 | N/A | Tie |
| Intent Layer Quality | 11d. Question Novelty (cross-system) | 84.8% | 100.0% | N/A | Baseline |
| Intent Layer Quality | 11e. Reason–Insight Coherence | 0.553 | 0.527 | N/A | QUIS |
| Intent Layer Quality | 12. Structural Validity Rate | 99.0% (98/99) | 45.3% (34/75) | 83.5% (71/85) | QUIS |
| Intent Layer Quality | 12a. SVR — OUTSTANDING_VALUE | 30/30 | 14/14 | 24/24 | Tie |
| Intent Layer Quality | 12a. SVR — TREND | 2/2 | 16/33 | 10/10 | Tie |
| Intent Layer Quality | 12a. SVR — ATTRIBUTION | 27/27 | 0/13 | 20/24 | QUIS |
| Intent Layer Quality | 12a. SVR — DISTRIBUTION_DIFFERENCE | 39/40 | 4/15 | 17/27 | QUIS |

### employee_attrition

| Group | Metric | QUIS | Baseline | ONLYSTATS | Winner |
|-------|--------|------|----------|-----------|--------|
| Core & Efficiency | 0. Total insights | 133 | 81 | 132 | N/A |
| Core & Efficiency | 1. Faithfulness | 100.0% | 100.0% | 100.0% | Tie |
| Core & Efficiency | 2. Statistical Significance (Overall) | 20.0% | 55.8% | 20.2% | Baseline |
| Core & Efficiency | 2a. Significance — TREND | N/A | 0.0% (4) | N/A | Baseline |
| Core & Efficiency | 2a. Significance — OUTSTANDING_VALUE | 22.2% (27) | 40.0% (10) | 0.0% (19) | Baseline |
| Core & Efficiency | 2a. Significance — ATTRIBUTION | 36.7% (49) | 100.0% (7) | 47.3% (55) | Baseline |
| Core & Efficiency | 2a. Significance — DISTRIBUTION_DIFFERENCE | 20.9% (43) | 83.3% (6) | 33.3% (9) | Baseline |
| Core & Efficiency | 2b. Pattern Coverage | 3/4 (75%) | 3/4 (75%) | 3/4 (75%) | Tie |
| Core & Efficiency | 2b1. Uncovered Patterns | TREND | TREND | TREND | N/A |
| Core & Efficiency | 3. Insight Novelty | 90.2% | 85.2% | 81.8% | QUIS |
| Core & Efficiency | 4a. Diversity — Semantic | 0.499 | 0.497 | 0.432 | QUIS |
| Core & Efficiency | 4b. Diversity — Subspace Entropy | 2.938 | 1.305 | 2.948 | ONLYSTATS |
| Core & Efficiency | 4c. Diversity — Value | 0.767 | 0.407 | 0.756 | QUIS |
| Core & Efficiency | 4d. Diversity — Dedup Rate | 0 | 0.037 | 0 | Tie |
| Subspace Deep-dive | 7. Subspace Rate | 116/133 (87.2%) | 27/81 (33.3%) | 78/132 (59.1%) | QUIS |
| Subspace Deep-dive | 7a. Subspace Faithfulness | 100.0% | 100.0% | 100.0% | Tie |
| Subspace Deep-dive | 7b. Subspace Significance | 24.0% | 0.0% | 0.0% | QUIS |
| Subspace Deep-dive | 8. Score Uplift from Subspace | Δ=0.083, x=1.574 | Δ=0.046, x=1.079 | Δ=-0.188, x=0.346 | QUIS |
| Subspace Deep-dive | 9. Simpson's Paradox Rate (SPR) | 30.2% (1/35 sig) | 0.0% (0/0 sig) | 7.7% (0/6 sig) | QUIS |
| Intent Layer Quality | 10. Total (B,M) pairs evaluated | 49/51 | 24/30 | 53/53 | N/A |
| Intent Layer Quality | 10a. BM — NMI mean | 0.035 | 0.086 | nan | Baseline |
| Intent Layer Quality | 10b. BM — Interestingness | 0.090 | 0.157 | 0.102 | Baseline |
| Intent Layer Quality | 10c. BM — Actionability | 0.961 | 0.800 | 1.000 | ONLYSTATS |
| Intent Layer Quality | 10d. BM — Diversity | 0.384 | 0.370 | 0.402 | ONLYSTATS |
| Intent Layer Quality | 11a. Question Semantic Diversity | 0.597 | 0.630 | N/A | Baseline |
| Intent Layer Quality | 11b. Question Specificity | 10.25 ± 2.51 | 10.11 ± 5.17 | N/A | QUIS |
| Intent Layer Quality | 11c. Question–Insight Alignment | 0.493 | 0.588 | N/A | Baseline |
| Intent Layer Quality | 11d. Question Novelty (cross-system) | 100.0% | 97.5% | N/A | QUIS |
| Intent Layer Quality | 11e. Reason–Insight Coherence | 0.468 | 0.519 | N/A | Baseline |
| Intent Layer Quality | 12. Structural Validity Rate | 96.2% (128/133) | 37.0% (30/81) | 100.0% (132/132) | ONLYSTATS |
| Intent Layer Quality | 12a. SVR — OUTSTANDING_VALUE | 35/35 | 11/11 | 58/58 | Tie |
| Intent Layer Quality | 12a. SVR — TREND | 0/1 | 0/42 | N/A | Tie |
| Intent Layer Quality | 12a. SVR — ATTRIBUTION | 50/50 | 7/13 | 65/65 | Tie |
| Intent Layer Quality | 12a. SVR — DISTRIBUTION_DIFFERENCE | 43/47 | 12/15 | 9/9 | ONLYSTATS |

### online_sales

| Group | Metric | QUIS | Baseline | ONLYSTATS | Winner |
|-------|--------|------|----------|-----------|--------|
| Core & Efficiency | 0. Total insights | 106 | 61 | 72 | N/A |
| Core & Efficiency | 1. Faithfulness | 100.0% | 100.0% | 100.0% | Tie |
| Core & Efficiency | 2. Statistical Significance (Overall) | 35.9% | 43.8% | 58.6% | ONLYSTATS |
| Core & Efficiency | 2a. Significance — TREND | N/A | 100.0% (2) | 66.7% (3) | Baseline |
| Core & Efficiency | 2a. Significance — OUTSTANDING_VALUE | 34.4% (32) | 75.0% (16) | 52.0% (25) | Baseline |
| Core & Efficiency | 2a. Significance — ATTRIBUTION | 53.3% (30) | N/A | 60.0% (20) | ONLYSTATS |
| Core & Efficiency | 2a. Significance — DISTRIBUTION_DIFFERENCE | 56.0% (25) | 0.0% (5) | 55.6% (18) | QUIS |
| Core & Efficiency | 2b. Pattern Coverage | 3/4 (75%) | 2/4 (50%) | 4/4 (100%) | ONLYSTATS |
| Core & Efficiency | 2b1. Uncovered Patterns | TREND | TREND, ATTRIBUTION | — | N/A |
| Core & Efficiency | 3. Insight Novelty | 47.2% | 93.4% | 30.6% | Baseline |
| Core & Efficiency | 4a. Diversity — Semantic | 0.489 | 0.449 | 0.433 | QUIS |
| Core & Efficiency | 4b. Diversity — Subspace Entropy | 1.596 | 0.843 | 1.659 | ONLYSTATS |
| Core & Efficiency | 4c. Diversity — Value | 0.440 | 0.500 | 0.463 | Baseline |
| Core & Efficiency | 4d. Diversity — Dedup Rate | 0 | 0 | 0 | Tie |
| Subspace Deep-dive | 7. Subspace Rate | 84/106 (79.2%) | 22/61 (36.1%) | 67/72 (93.1%) | ONLYSTATS |
| Subspace Deep-dive | 7a. Subspace Faithfulness | 100.0% | 100.0% | 100.0% | Tie |
| Subspace Deep-dive | 7b. Subspace Significance | 44.4% | 100.0% | 45.0% | Baseline |
| Subspace Deep-dive | 8. Score Uplift from Subspace | Δ=-0.137, x=0.742 | Δ=0.025, x=1.048 | Δ=-0.386, x=0.511 | Baseline |
| Subspace Deep-dive | 9. Simpson's Paradox Rate (SPR) | 32.1% (1/27 sig) | 31.8% (0/7 sig) | 31.3% (1/21 sig) | QUIS |
| Intent Layer Quality | 10. Total (B,M) pairs evaluated | 24/26 | 7/16 | 24/24 | N/A |
| Intent Layer Quality | 10a. BM — NMI mean | 0.179 | 0.348 | 0.228 | Baseline |
| Intent Layer Quality | 10b. BM — Interestingness | 0.244 | 0.513 | 0.314 | Baseline |
| Intent Layer Quality | 10c. BM — Actionability | 0.923 | 0.438 | 1.000 | ONLYSTATS |
| Intent Layer Quality | 10d. BM — Diversity | 0.245 | 0.262 | 0.333 | ONLYSTATS |
| Intent Layer Quality | 11a. Question Semantic Diversity | 0.518 | 0.577 | N/A | Baseline |
| Intent Layer Quality | 11b. Question Specificity | 9.99 ± 2.21 | 13.48 ± 4.68 | N/A | Baseline |
| Intent Layer Quality | 11c. Question–Insight Alignment | 0.543 | 0.539 | N/A | Tie |
| Intent Layer Quality | 11d. Question Novelty (cross-system) | 95.3% | 100.0% | N/A | Baseline |
| Intent Layer Quality | 11e. Reason–Insight Coherence | 0.557 | 0.497 | N/A | QUIS |
| Intent Layer Quality | 12. Structural Validity Rate | 86.8% (92/106) | 37.7% (23/61) | 88.9% (64/72) | ONLYSTATS |
| Intent Layer Quality | 12a. SVR — OUTSTANDING_VALUE | 36/36 | 18/18 | 25/25 | Tie |
| Intent Layer Quality | 12a. SVR — TREND | 0/1 | 0/19 | 3/3 | ONLYSTATS |
| Intent Layer Quality | 12a. SVR — ATTRIBUTION | 29/32 | 0/11 | 18/20 | QUIS |
| Intent Layer Quality | 12a. SVR — DISTRIBUTION_DIFFERENCE | 27/37 | 5/13 | 18/24 | ONLYSTATS |
