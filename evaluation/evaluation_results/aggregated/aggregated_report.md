# Aggregated 3-Way Evaluation Report

Generated: 2026-04-28 23:56  
Datasets: adidas, transactions, employee_attrition, online_sales  
Systems: QUIS | Baseline | ONLYSTATS

> **Aggregation rules**
> - *Averaged metrics* (%) — mean across datasets reported in the summary table.
> - *Per-dataset metrics* (counts, fractions, text) — kept separately below.

## Win Count Summary (averaged metrics, 26 total)

| System | Wins |
|--------|------|
| QUIS | 5 |
| Baseline | 14 |
| ONLYSTATS | 5 |

## Averaged Metrics (mean across datasets)

### Core & Efficiency

| Metric | QUIS | Baseline | ONLYSTATS | Winner | Description |
|--------|------|----------|-----------|--------|-------------|
| 1. Faithfulness | 97.9% | 97.6% | 97.7% | **QUIS** | Correctness - đúng dữ liệu |
| 2. Statistical Significance (Overall) | 34.8% | 52.6% | 49.8% | **Baseline** | Validity - pattern-averaged (fair comparison) |
| 2a. Significance — TREND | 100.0% | 62.5% | 83.3% | **QUIS** | Validity - TREND pattern |
| 2a. Significance — OUTSTANDING_VALUE | 24.1% | 77.0% | 43.4% | **Baseline** | Validity - OUTSTANDING_VALUE pattern |
| 2a. Significance — ATTRIBUTION | 46.5% | 100.0% | 71.1% | **Baseline** | Validity - ATTRIBUTION pattern |
| 2a. Significance — DISTRIBUTION_DIFFERENCE | 43.6% | 61.1% | 43.0% | **Baseline** | Validity - DISTRIBUTION_DIFFERENCE pattern |
| 3. Insight Novelty | 79.3% | 89.7% | 71.3% | **Baseline** | Usefulness - khác baseline (from pairwise comparison results) |
| 4a. Diversity — Semantic | 0.4750 | 0.4572 | 0.4243 | **QUIS** | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy | 2.1353 | 1.1402 | 2.4108 | **ONLYSTATS** | Entropy of subspace filter columns used |
| 4c. Diversity — Value | 0.7490 | 0.4922 | 0.7512 | **ONLYSTATS** | Unique (column, value) pairs in subspace / total |
| 4d. Diversity — Dedup Rate | 0.0000 | 0.0330 | 0.0000 | **Tie** | Duplicate rate — lower is better |
### Subspace Deep-dive

| Metric | QUIS | Baseline | ONLYSTATS | Winner | Description |
|--------|------|----------|-----------|--------|-------------|
| 7. Subspace Rate | 88.3% | 32.8% | 70.5% | **QUIS** | Insights with subspace filter / total |
| 7a. Subspace Faithfulness | 97.9% | 100.0% | 98.0% | **Baseline** | Faithfulness restricted to subspace insights |
| 7b. Subspace Significance | 28.1% | 43.8% | 41.0% | **Baseline** | Significance restricted to subspace insights |
| 8. Score Uplift from Subspace | 1.0670 | 0.7670 | 0.6850 | **QUIS** | Δ = mean(score|subspace) - mean(score|no-subspace) |
| 9. Direction (Contrasting Rate) | N/A | N/A | N/A | **N/A** | Rate of subspace insights where subspace value opposes global value — higher means more contrasting/valuable insights |
### Intent Layer Quality

| Metric | QUIS | Baseline | ONLYSTATS | Winner | Description |
|--------|------|----------|-----------|--------|-------------|
| 10a. BM — NMI mean | 0.0775 | 0.2838 | 0.1780 | **Baseline** | Mean NMI over categorical-B pairs |
| 10b. BM — Interestingness | 0.1030 | 0.4400 | 0.1628 | **Baseline** | Mean Coverage×EffectSize over categorical-B pairs |
| 10c. BM — Actionability | 0.7835 | 0.4865 | 1.0000 | **ONLYSTATS** | % pairs with categorical breakdown |
| 10d. BM — Diversity | 0.3063 | 0.3332 | 0.4000 | **ONLYSTATS** | Unique (B,M) pairs / total insights |
| 11a. Question Semantic Diversity | 0.5035 | 0.5777 | N/A | **Baseline** | 1 - mean cosine sim of question embeddings (within-system); N/A for ONLYSTATS (template) |
| 11b. Question Specificity | 9.7225 | 12.5250 | N/A | **Baseline** | Avg word count per question (mean ± std) — higher = more specific; N/A for ONLYSTATS (template) |
| 11c. Question–Insight Alignment | 0.4703 | 0.5530 | N/A | **Baseline** | Mean cosine(Embed(question), Embed(insight)) — control metric; N/A for ONLYSTATS (template) |
| 11d. Question Novelty (cross-system) | 95.0% | 99.4% | N/A | **Baseline** | % of questions with cross-system max cosine sim < 0.85 (from pairwise comparison results) |
| 11e. Reason–Insight Coherence | 0.4453 | 0.4745 | N/A | **Baseline** | Mean cosine(Embed(reason), Embed(insight)) — reason grounding |
| 12. Structural Validity Rate | 80.9% | 40.7% | 93.1% | **ONLYSTATS** | % insights with breakdown type valid for their pattern — measures QuGen structural understanding |

## Per-Dataset Detail (non-averaged metrics)

### Core & Efficiency

**0. Total insights** — Total insight cards generated

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 99 | 75 | 85 |
| transactions | 12 | 21 | 98 |
| employee_attrition | 133 | 81 | 132 |
| online_sales | 106 | 61 | 72 |

**2b. Pattern Coverage** — Patterns with ≥1 structurally valid insight / 4 total patterns

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 4/4 (100%) | 3/4 (75%) | 4/4 (100%) |
| transactions | 1/4 (25%) | 1/4 (25%) | 3/4 (75%) |
| employee_attrition | 3/4 (75%) | 3/4 (75%) | 3/4 (75%) |
| online_sales | 3/4 (75%) | 2/4 (50%) | 4/4 (100%) |

**2b1. Uncovered Patterns** — Patterns with 0 valid insights (breakdown type mismatch)

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | — | ATTRIBUTION | — |
| transactions | TREND, ATTRIBUTION, DISTRIBUTION_DIFFERENCE | TREND, ATTRIBUTION, DISTRIBUTION_DIFFERENCE | TREND |
| employee_attrition | TREND | TREND | TREND |
| online_sales | TREND | TREND, ATTRIBUTION | — |

### Intent Layer Quality

**10. Total (B,M) pairs evaluated** — Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness)

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 26/26 | 11/24 | 31/31 |
| transactions | 1/4 | 2/8 | 49/49 |
| employee_attrition | 49/51 | 24/30 | 53/53 |
| online_sales | 24/26 | 7/16 | 24/24 |

**12a. SVR — OUTSTANDING_VALUE** — Structural validity for OUTSTANDING_VALUE pattern

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 30/30 | 14/14 | 24/24 |
| transactions | 5/5 | 9/9 | 40/40 |
| employee_attrition | 35/35 | 11/11 | 58/58 |
| online_sales | 36/36 | 18/18 | 25/25 |

**12a. SVR — TREND** — Structural validity for TREND pattern

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 2/2 | 16/33 | 10/10 |
| transactions | N/A | 0/12 | N/A |
| employee_attrition | 0/1 | 0/42 | N/A |
| online_sales | 0/1 | 0/19 | 3/3 |

**12a. SVR — ATTRIBUTION** — Structural validity for ATTRIBUTION pattern

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 27/27 | 0/13 | 20/24 |
| transactions | 0/5 | N/A | 53/53 |
| employee_attrition | 50/50 | 7/13 | 65/65 |
| online_sales | 29/32 | 0/11 | 18/20 |

**12a. SVR — DISTRIBUTION_DIFFERENCE** — Structural validity for DISTRIBUTION_DIFFERENCE pattern

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 39/40 | 4/15 | 17/27 |
| transactions | 0/2 | N/A | 5/5 |
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
| Subspace Deep-dive | 9. Direction (Contrasting Rate) | 0.634 (52/82) | 0.389 (7/18) | 0.821 (55/67) | ONLYSTATS |
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

### transactions

| Group | Metric | QUIS | Baseline | ONLYSTATS | Winner |
|-------|--------|------|----------|-----------|--------|
| Core & Efficiency | 0. Total insights | 12 | 21 | 98 | N/A |
| Core & Efficiency | 1. Faithfulness | 91.7% | 90.5% | 90.8% | QUIS |
| Core & Efficiency | 2. Statistical Significance (Overall) | 0.0% | 37.5% | 44.3% | ONLYSTATS |
| Core & Efficiency | 2a. Significance — TREND | N/A | 50.0% (4) | N/A | Baseline |
| Core & Efficiency | 2a. Significance — OUTSTANDING_VALUE | 0.0% (1) | 100.0% (6) | 80.0% (25) | Baseline |
| Core & Efficiency | 2a. Significance — ATTRIBUTION | 0.0% (1) | N/A | 77.1% (48) | ONLYSTATS |
| Core & Efficiency | 2a. Significance — DISTRIBUTION_DIFFERENCE | 0.0% (1) | N/A | 20.0% (5) | ONLYSTATS |
| Core & Efficiency | 2b. Pattern Coverage | 1/4 (25%) | 1/4 (25%) | 3/4 (75%) | ONLYSTATS |
| Core & Efficiency | 2b1. Uncovered Patterns | TREND, ATTRIBUTION, DISTRIBUTION_DIFFERENCE | TREND, ATTRIBUTION, DISTRIBUTION_DIFFERENCE | TREND | N/A |
| Core & Efficiency | 3. Insight Novelty | 100.0% | 100.0% | 100.0% | Tie |
| Core & Efficiency | 4a. Diversity — Semantic | 0.433 | 0.495 | 0.393 | Baseline |
| Core & Efficiency | 4b. Diversity — Subspace Entropy | 1.748 | 1.040 | 3.009 | ONLYSTATS |
| Core & Efficiency | 4c. Diversity — Value | 0.917 | 0.750 | 0.920 | ONLYSTATS |
| Core & Efficiency | 4d. Diversity — Dedup Rate | 0 | 0.095 | 0 | Tie |
| Subspace Deep-dive | 7. Subspace Rate | 12/12 (100.0%) | 4/21 (19.0%) | 50/98 (51.0%) | QUIS |
| Subspace Deep-dive | 7a. Subspace Faithfulness | 91.7% | 100.0% | 92.0% | Baseline |
| Subspace Deep-dive | 7b. Subspace Significance | 0.0% | 0.0% | 68.8% | ONLYSTATS |
| Subspace Deep-dive | 8. Score Uplift from Subspace | N/A | Δ=-0.486, x=0.145 | Δ=0.048, x=1.157 | ONLYSTATS |
| Subspace Deep-dive | 9. Direction (Contrasting Rate) | 1.000 (3/3) | N/A | 0.705 (31/44) | QUIS |
| Intent Layer Quality | 10. Total (B,M) pairs evaluated | 1/4 | 2/8 | 49/49 | N/A |
| Intent Layer Quality | 10a. BM — NMI mean | 0.002 | 0.370 | 0.089 | Baseline |
| Intent Layer Quality | 10b. BM — Interestingness | 0.001 | 1.000 | 0.167 | Baseline |
| Intent Layer Quality | 10c. BM — Actionability | 0.250 | 0.250 | 1.000 | ONLYSTATS |
| Intent Layer Quality | 10d. BM — Diversity | 0.333 | 0.381 | 0.500 | ONLYSTATS |
| Intent Layer Quality | 11a. Question Semantic Diversity | 0.406 | 0.556 | N/A | Baseline |
| Intent Layer Quality | 11b. Question Specificity | 9.50 ± 0.87 | 13.76 ± 8.22 | N/A | Baseline |
| Intent Layer Quality | 11c. Question–Insight Alignment | 0.262 | 0.506 | N/A | Baseline |
| Intent Layer Quality | 11d. Question Novelty (cross-system) | 100.0% | 100.0% | N/A | Tie |
| Intent Layer Quality | 11e. Reason–Insight Coherence | 0.203 | 0.355 | N/A | Baseline |
| Intent Layer Quality | 12. Structural Validity Rate | 41.7% (5/12) | 42.9% (9/21) | 100.0% (98/98) | ONLYSTATS |
| Intent Layer Quality | 12a. SVR — OUTSTANDING_VALUE | 5/5 | 9/9 | 40/40 | Tie |
| Intent Layer Quality | 12a. SVR — TREND | N/A | 0/12 | N/A | Tie |
| Intent Layer Quality | 12a. SVR — ATTRIBUTION | 0/5 | N/A | 53/53 | ONLYSTATS |
| Intent Layer Quality | 12a. SVR — DISTRIBUTION_DIFFERENCE | 0/2 | N/A | 5/5 | ONLYSTATS |

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
| Subspace Deep-dive | 9. Direction (Contrasting Rate) | 0.438 (46/105) | 0.300 (3/10) | 0.711 (27/38) | ONLYSTATS |
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
| Subspace Deep-dive | 9. Direction (Contrasting Rate) | 0.554 (36/65) | 0.667 (4/6) | 0.770 (47/61) | ONLYSTATS |
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
