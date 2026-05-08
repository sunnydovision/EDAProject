# Aggregated 3-Way Evaluation Report

Generated: 2026-05-08 19:24  
Datasets: adidas, employee_attrition, online_sales  
Systems: QUIS | Baseline | ONLYSTATS

> **Aggregation rules**
> - *Averaged metrics* (%) — mean across datasets reported in the summary table.
> - *Per-dataset metrics* (counts, fractions, text) — kept separately below.

## Win Count Summary (averaged metrics, 26 total)

| System | Wins |
|--------|------|
| QUIS | 8 |
| Baseline | 10 |
| ONLYSTATS | 5 |

## Averaged Metrics (mean across datasets)

### Core & Efficiency

| Metric | QUIS | Baseline | ONLYSTATS | Winner | Description |
|--------|------|----------|-----------|--------|-------------|
| 1. Faithfulness | 100.0% | 100.0% | 100.0% | **Tie** | Correctness - đúng dữ liệu |
| 2. Statistical Significance (Overall) | 46.4% | 57.6% | 58.0% | **ONLYSTATS** | Validity - pattern-averaged (fair comparison) |
| 2a. Significance — TREND | 100.0% | 66.7% | 78.5% | **QUIS** | Validity - TREND pattern |
| 2a. Significance — OUTSTANDING_VALUE | 32.2% | 69.3% | 29.2% | **Baseline** | Validity - OUTSTANDING_VALUE pattern |
| 2a. Significance — ATTRIBUTION | 62.0% | 100.0% | 69.2% | **Baseline** | Validity - ATTRIBUTION pattern |
| 2a. Significance — DISTRIBUTION_DIFFERENCE | 58.1% | 61.1% | 81.5% | **ONLYSTATS** | Validity - DISTRIBUTION_DIFFERENCE pattern |
| 3. Insight Novelty | 67.4% | 86.2% | 57.3% | **Baseline** | Usefulness - khác baseline (from pairwise comparison results) |
| 4a. Diversity — Semantic | 0.4890 | 0.4447 | 0.4797 | **QUIS** | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy | 2.2643 | 1.1737 | 1.9347 | **QUIS** | Entropy of subspace filter columns used |
| 4c. Diversity — Value | 0.6930 | 0.4063 | 0.6177 | **QUIS** | Unique (column, value) pairs in subspace / total |
| 4d. Diversity — Dedup Rate | 0.0000 | 0.0123 | 0.0000 | **Tie** | Duplicate rate — lower is better |
### Subspace Deep-dive

| Metric | QUIS | Baseline | ONLYSTATS | Winner | Description |
|--------|------|----------|-----------|--------|-------------|
| 7. Subspace Rate | 84.4% | 37.4% | 62.6% | **QUIS** | Insights with subspace filter / total |
| 7a. Subspace Faithfulness | 100.0% | 100.0% | 100.0% | **Tie** | Faithfulness restricted to subspace insights |
| 7b. Subspace Significance | 37.5% | 58.3% | 43.0% | **Baseline** | Significance restricted to subspace insights |
| 8. Score Uplift from Subspace | 1.0670 | 0.9743 | 0.8177 | **QUIS** | Δ = mean(score|subspace) - mean(score|no-subspace) |
| 9. Simpson's Paradox Rate (SPR) | 30.1% | 18.9% | 34.7% | **ONLYSTATS** | Rate of statistically significant pattern reversals (p<0.05) — true Simpson's Paradox cases |
### Intent Layer Quality

| Metric | QUIS | Baseline | ONLYSTATS | Winner | Description |
|--------|------|----------|-----------|--------|-------------|
| 10a. BM — NMI mean | 0.1027 | 0.2550 | 0.2350 | **Baseline** | Mean NMI over categorical-B pairs |
| 10b. BM — Interestingness | 0.1370 | 0.2533 | 0.1613 | **Baseline** | Mean Coverage×EffectSize over categorical-B pairs |
| 10c. BM — Actionability | 0.9613 | 0.5653 | 1.0000 | **ONLYSTATS** | % pairs with categorical breakdown |
| 10d. BM — Diversity | 0.2973 | 0.3173 | 0.3510 | **ONLYSTATS** | Unique (B,M) pairs / total insights |
| 11a. Question Semantic Diversity | 0.5360 | 0.5850 | N/A | **Baseline** | 1 - mean cosine sim of question embeddings (within-system); N/A for ONLYSTATS (template) |
| 11b. Question Specificity | 9.7967 | 12.1133 | N/A | **Baseline** | Avg word count per question (mean ± std) — higher = more specific; N/A for ONLYSTATS (template) |
| 11c. Question–Insight Alignment | 0.5397 | 0.5687 | N/A | **Baseline** | Mean cosine(Embed(question), Embed(insight)) — control metric; N/A for ONLYSTATS (template) |
| 11d. Question Novelty (cross-system) | 95.1% | 99.2% | N/A | **Baseline** | % of questions with cross-system max cosine sim < 0.85 (from pairwise comparison results) |
| 11e. Reason–Insight Coherence | 0.5260 | 0.5143 | N/A | **QUIS** | Mean cosine(Embed(reason), Embed(insight)) — reason grounding |
| 12. Structural Validity Rate | 94.0% | 40.0% | 91.2% | **QUIS** | % insights with breakdown type valid for their pattern — measures QuGen structural understanding |

## Per-Dataset Detail (non-averaged metrics)

### Core & Efficiency

**0. Total insights** — Total insight cards generated

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 99 | 75 | 113 |
| employee_attrition | 133 | 81 | 125 |
| online_sales | 106 | 61 | 114 |

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
| adidas | 26/26 | 11/24 | 45/45 |
| employee_attrition | 49/51 | 24/30 | 38/38 |
| online_sales | 24/26 | 7/16 | 40/40 |

**12a. SVR — OUTSTANDING_VALUE** — Structural validity for OUTSTANDING_VALUE pattern

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 30/30 | 14/14 | 38/38 |
| employee_attrition | 35/35 | 11/11 | 49/49 |
| online_sales | 36/36 | 18/18 | 45/45 |

**12a. SVR — TREND** — Structural validity for TREND pattern

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 2/2 | 16/33 | 19/19 |
| employee_attrition | 0/1 | 0/42 | N/A |
| online_sales | 0/1 | 0/19 | 7/7 |

**12a. SVR — ATTRIBUTION** — Structural validity for ATTRIBUTION pattern

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 27/27 | 0/13 | 32/32 |
| employee_attrition | 50/50 | 7/13 | 58/58 |
| online_sales | 29/32 | 0/11 | 26/34 |

**12a. SVR — DISTRIBUTION_DIFFERENCE** — Structural validity for DISTRIBUTION_DIFFERENCE pattern

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 39/40 | 4/15 | 20/24 |
| employee_attrition | 43/47 | 12/15 | 18/18 |
| online_sales | 27/37 | 5/13 | 10/28 |

## Appendix — Full Results Per Dataset

### adidas

| Group | Metric | QUIS | Baseline | ONLYSTATS | Winner |
|-------|--------|------|----------|-----------|--------|
| Core & Efficiency | 0. Total insights | 99 | 75 | 113 | N/A |
| Core & Efficiency | 1. Faithfulness | 100.0% | 100.0% | 100.0% | Tie |
| Core & Efficiency | 2. Statistical Significance (Overall) | 83.4% | 73.2% | 80.7% | QUIS |
| Core & Efficiency | 2a. Significance — TREND | 100.0% (2) | 100.0% (16) | 100.0% (19) | Tie |
| Core & Efficiency | 2a. Significance — OUTSTANDING_VALUE | 40.0% (30) | 92.9% (14) | 39.5% (38) | Baseline |
| Core & Efficiency | 2a. Significance — ATTRIBUTION | 96.0% (25) | N/A | 100.0% (32) | ONLYSTATS |
| Core & Efficiency | 2a. Significance — DISTRIBUTION_DIFFERENCE | 97.4% (39) | 100.0% (4) | 83.3% (24) | Baseline |
| Core & Efficiency | 2b. Pattern Coverage | 4/4 (100%) | 3/4 (75%) | 4/4 (100%) | Tie |
| Core & Efficiency | 2b1. Uncovered Patterns | — | ATTRIBUTION | — | N/A |
| Core & Efficiency | 3. Insight Novelty | 70.7% | 80.0% | 61.9% | Baseline |
| Core & Efficiency | 4a. Diversity — Semantic | 0.479 | 0.388 | 0.473 | QUIS |
| Core & Efficiency | 4b. Diversity — Subspace Entropy | 2.259 | 1.373 | 1.752 | QUIS |
| Core & Efficiency | 4c. Diversity — Value | 0.872 | 0.312 | 0.786 | QUIS |
| Core & Efficiency | 4d. Diversity — Dedup Rate | 0 | 0 | 0 | Tie |
| Subspace Deep-dive | 7. Subspace Rate | 86/99 (86.9%) | 32/75 (42.7%) | 70/113 (61.9%) | QUIS |
| Subspace Deep-dive | 7a. Subspace Faithfulness | 100.0% | 100.0% | 100.0% | Tie |
| Subspace Deep-dive | 7b. Subspace Significance | 44.0% | 75.0% | 39.1% | Baseline |
| Subspace Deep-dive | 8. Score Uplift from Subspace | Δ=-0.043, x=0.885 | Δ=-0.135, x=0.796 | Δ=-0.122, x=0.715 | QUIS |
| Subspace Deep-dive | 9. Simpson's Paradox Rate (SPR) | 27.9% (0/24 sig) | 25.0% (0/8 sig) | 42.9% (0/30 sig) | ONLYSTATS |
| Intent Layer Quality | 10. Total (B,M) pairs evaluated | 26/26 | 11/24 | 45/45 | N/A |
| Intent Layer Quality | 10a. BM — NMI mean | 0.094 | 0.331 | 0.229 | Baseline |
| Intent Layer Quality | 10b. BM — Interestingness | 0.077 | 0.090 | 0.072 | Baseline |
| Intent Layer Quality | 10c. BM — Actionability | 1.000 | 0.458 | 1.000 | Tie |
| Intent Layer Quality | 10d. BM — Diversity | 0.263 | 0.320 | 0.398 | ONLYSTATS |
| Intent Layer Quality | 11a. Question Semantic Diversity | 0.493 | 0.548 | N/A | Baseline |
| Intent Layer Quality | 11b. Question Specificity | 9.15 ± 1.40 | 12.75 ± 5.03 | N/A | Baseline |
| Intent Layer Quality | 11c. Question–Insight Alignment | 0.583 | 0.579 | N/A | Tie |
| Intent Layer Quality | 11d. Question Novelty (cross-system) | 89.9% | 100.0% | N/A | Baseline |
| Intent Layer Quality | 11e. Reason–Insight Coherence | 0.553 | 0.527 | N/A | QUIS |
| Intent Layer Quality | 12. Structural Validity Rate | 99.0% (98/99) | 45.3% (34/75) | 96.5% (109/113) | QUIS |
| Intent Layer Quality | 12a. SVR — OUTSTANDING_VALUE | 30/30 | 14/14 | 38/38 | Tie |
| Intent Layer Quality | 12a. SVR — TREND | 2/2 | 16/33 | 19/19 | Tie |
| Intent Layer Quality | 12a. SVR — ATTRIBUTION | 27/27 | 0/13 | 32/32 | Tie |
| Intent Layer Quality | 12a. SVR — DISTRIBUTION_DIFFERENCE | 39/40 | 4/15 | 20/24 | QUIS |

### employee_attrition

| Group | Metric | QUIS | Baseline | ONLYSTATS | Winner |
|-------|--------|------|----------|-----------|--------|
| Core & Efficiency | 0. Total insights | 133 | 81 | 125 | N/A |
| Core & Efficiency | 1. Faithfulness | 100.0% | 100.0% | 100.0% | Tie |
| Core & Efficiency | 2. Statistical Significance (Overall) | 20.0% | 55.8% | 30.6% | Baseline |
| Core & Efficiency | 2a. Significance — TREND | N/A | 0.0% (4) | N/A | Baseline |
| Core & Efficiency | 2a. Significance — OUTSTANDING_VALUE | 22.2% (27) | 40.0% (10) | 3.8% (26) | Baseline |
| Core & Efficiency | 2a. Significance — ATTRIBUTION | 36.7% (49) | 100.0% (7) | 57.6% (33) | Baseline |
| Core & Efficiency | 2a. Significance — DISTRIBUTION_DIFFERENCE | 20.9% (43) | 83.3% (6) | 61.1% (18) | Baseline |
| Core & Efficiency | 2b. Pattern Coverage | 3/4 (75%) | 3/4 (75%) | 3/4 (75%) | Tie |
| Core & Efficiency | 2b1. Uncovered Patterns | TREND | TREND | TREND | N/A |
| Core & Efficiency | 3. Insight Novelty | 87.2% | 85.2% | 78.4% | QUIS |
| Core & Efficiency | 4a. Diversity — Semantic | 0.499 | 0.497 | 0.491 | QUIS |
| Core & Efficiency | 4b. Diversity — Subspace Entropy | 2.938 | 1.305 | 2.485 | QUIS |
| Core & Efficiency | 4c. Diversity — Value | 0.767 | 0.407 | 0.707 | QUIS |
| Core & Efficiency | 4d. Diversity — Dedup Rate | 0 | 0.037 | 0 | Tie |
| Subspace Deep-dive | 7. Subspace Rate | 116/133 (87.2%) | 27/81 (33.3%) | 75/125 (60.0%) | QUIS |
| Subspace Deep-dive | 7a. Subspace Faithfulness | 100.0% | 100.0% | 100.0% | Tie |
| Subspace Deep-dive | 7b. Subspace Significance | 24.0% | 0.0% | 0.0% | QUIS |
| Subspace Deep-dive | 8. Score Uplift from Subspace | Δ=0.083, x=1.574 | Δ=0.046, x=1.079 | Δ=-0.184, x=0.506 | QUIS |
| Subspace Deep-dive | 9. Simpson's Paradox Rate (SPR) | 30.2% (1/35 sig) | 0.0% (0/0 sig) | 21.3% (0/16 sig) | QUIS |
| Intent Layer Quality | 10. Total (B,M) pairs evaluated | 49/51 | 24/30 | 38/38 | N/A |
| Intent Layer Quality | 10a. BM — NMI mean | 0.035 | 0.086 | nan | Baseline |
| Intent Layer Quality | 10b. BM — Interestingness | 0.090 | 0.157 | 0.087 | Baseline |
| Intent Layer Quality | 10c. BM — Actionability | 0.961 | 0.800 | 1.000 | ONLYSTATS |
| Intent Layer Quality | 10d. BM — Diversity | 0.384 | 0.370 | 0.304 | QUIS |
| Intent Layer Quality | 11a. Question Semantic Diversity | 0.597 | 0.630 | N/A | Baseline |
| Intent Layer Quality | 11b. Question Specificity | 10.25 ± 2.51 | 10.11 ± 5.17 | N/A | QUIS |
| Intent Layer Quality | 11c. Question–Insight Alignment | 0.493 | 0.588 | N/A | Baseline |
| Intent Layer Quality | 11d. Question Novelty (cross-system) | 100.0% | 97.5% | N/A | QUIS |
| Intent Layer Quality | 11e. Reason–Insight Coherence | 0.468 | 0.519 | N/A | Baseline |
| Intent Layer Quality | 12. Structural Validity Rate | 96.2% (128/133) | 37.0% (30/81) | 100.0% (125/125) | ONLYSTATS |
| Intent Layer Quality | 12a. SVR — OUTSTANDING_VALUE | 35/35 | 11/11 | 49/49 | Tie |
| Intent Layer Quality | 12a. SVR — TREND | 0/1 | 0/42 | N/A | Tie |
| Intent Layer Quality | 12a. SVR — ATTRIBUTION | 50/50 | 7/13 | 58/58 | Tie |
| Intent Layer Quality | 12a. SVR — DISTRIBUTION_DIFFERENCE | 43/47 | 12/15 | 18/18 | ONLYSTATS |

### online_sales

| Group | Metric | QUIS | Baseline | ONLYSTATS | Winner |
|-------|--------|------|----------|-----------|--------|
| Core & Efficiency | 0. Total insights | 106 | 61 | 114 | N/A |
| Core & Efficiency | 1. Faithfulness | 100.0% | 100.0% | 100.0% | Tie |
| Core & Efficiency | 2. Statistical Significance (Overall) | 35.9% | 43.8% | 62.8% | ONLYSTATS |
| Core & Efficiency | 2a. Significance — TREND | N/A | 100.0% (2) | 57.1% (7) | Baseline |
| Core & Efficiency | 2a. Significance — OUTSTANDING_VALUE | 34.4% (32) | 75.0% (16) | 44.2% (43) | Baseline |
| Core & Efficiency | 2a. Significance — ATTRIBUTION | 53.3% (30) | N/A | 50.0% (34) | QUIS |
| Core & Efficiency | 2a. Significance — DISTRIBUTION_DIFFERENCE | 56.0% (25) | 0.0% (5) | 100.0% (10) | ONLYSTATS |
| Core & Efficiency | 2b. Pattern Coverage | 3/4 (75%) | 2/4 (50%) | 4/4 (100%) | ONLYSTATS |
| Core & Efficiency | 2b1. Uncovered Patterns | TREND | TREND, ATTRIBUTION | — | N/A |
| Core & Efficiency | 3. Insight Novelty | 44.3% | 93.4% | 31.6% | Baseline |
| Core & Efficiency | 4a. Diversity — Semantic | 0.489 | 0.449 | 0.475 | QUIS |
| Core & Efficiency | 4b. Diversity — Subspace Entropy | 1.596 | 0.843 | 1.567 | QUIS |
| Core & Efficiency | 4c. Diversity — Value | 0.440 | 0.500 | 0.360 | Baseline |
| Core & Efficiency | 4d. Diversity — Dedup Rate | 0 | 0 | 0 | Tie |
| Subspace Deep-dive | 7. Subspace Rate | 84/106 (79.2%) | 22/61 (36.1%) | 75/114 (65.8%) | QUIS |
| Subspace Deep-dive | 7a. Subspace Faithfulness | 100.0% | 100.0% | 100.0% | Tie |
| Subspace Deep-dive | 7b. Subspace Significance | 44.4% | 100.0% | 90.0% | Baseline |
| Subspace Deep-dive | 8. Score Uplift from Subspace | Δ=-0.137, x=0.742 | Δ=0.025, x=1.048 | Δ=0.102, x=1.232 | ONLYSTATS |
| Subspace Deep-dive | 9. Simpson's Paradox Rate (SPR) | 32.1% (1/27 sig) | 31.8% (0/7 sig) | 40.0% (0/30 sig) | ONLYSTATS |
| Intent Layer Quality | 10. Total (B,M) pairs evaluated | 24/26 | 7/16 | 40/40 | N/A |
| Intent Layer Quality | 10a. BM — NMI mean | 0.179 | 0.348 | 0.241 | Baseline |
| Intent Layer Quality | 10b. BM — Interestingness | 0.244 | 0.513 | 0.325 | Baseline |
| Intent Layer Quality | 10c. BM — Actionability | 0.923 | 0.438 | 1.000 | ONLYSTATS |
| Intent Layer Quality | 10d. BM — Diversity | 0.245 | 0.262 | 0.351 | ONLYSTATS |
| Intent Layer Quality | 11a. Question Semantic Diversity | 0.518 | 0.577 | N/A | Baseline |
| Intent Layer Quality | 11b. Question Specificity | 9.99 ± 2.21 | 13.48 ± 4.68 | N/A | Baseline |
| Intent Layer Quality | 11c. Question–Insight Alignment | 0.543 | 0.539 | N/A | Tie |
| Intent Layer Quality | 11d. Question Novelty (cross-system) | 95.3% | 100.0% | N/A | Baseline |
| Intent Layer Quality | 11e. Reason–Insight Coherence | 0.557 | 0.497 | N/A | QUIS |
| Intent Layer Quality | 12. Structural Validity Rate | 86.8% (92/106) | 37.7% (23/61) | 77.2% (88/114) | QUIS |
| Intent Layer Quality | 12a. SVR — OUTSTANDING_VALUE | 36/36 | 18/18 | 45/45 | Tie |
| Intent Layer Quality | 12a. SVR — TREND | 0/1 | 0/19 | 7/7 | ONLYSTATS |
| Intent Layer Quality | 12a. SVR — ATTRIBUTION | 29/32 | 0/11 | 26/34 | QUIS |
| Intent Layer Quality | 12a. SVR — DISTRIBUTION_DIFFERENCE | 27/37 | 5/13 | 10/28 | QUIS |
