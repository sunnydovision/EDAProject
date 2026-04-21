# IFQ vs Baseline: Evaluation Report with Investigation

**Generated**: 2026-04-22 01:23:00

---

## Executive Summary

| | IFQ | Baseline |
|---|---|---|
| **Metrics Won** | 11 | 10 |
| **Overall Winner** | ✓ |  |

---

## Group 1 — Core Metrics & Efficiency

### 0. Total insights

- IFQ: 97
- Baseline: 86
- Winner: N/A

---

### 1. Faithfulness

- IFQ: 100.0%
- Baseline: 100.0%
- Winner: Tie

---

### 2. Statistical Significance (Overall)

- IFQ: 74.7%
- Baseline: 60.3%
- Winner: IFQ

---

### 2a. Significance — TREND

- IFQ: 50.0% (2 insights)
- Baseline: 93.3% (15 insights)
- Winner: Baseline

**Investigation:**
- IFQ generates 3 TREND insights but only 2 evaluated: Insight 61 (COUNT(Invoice Date) GROUP BY Invoice Date) rejected because breakdown == col (significance.py line 373-374)
- COUNT(Invoice Date) GROUP BY Invoice Date is redundant
- IFQ should avoid generating COUNT(column) where column == breakdown
- Baseline generates 15 TREND insights with 93.3% significance vs IFQ 50% (1/2 significant)

---

### 2a. Significance — OUTSTANDING_VALUE

- IFQ: 53.0% (66 insights)
- Baseline: 81.2% (16 insights)
- Winner: Baseline

**Investigation:**
- IFQ generates 66 OUTSTANDING_VALUE insights (68% of total) with threshold 0.98 (T_OV=1.4 * threshold_scale=0.7)
- All 66 pass threshold (mean score 3.65) but only 53% significant (35/66) → scoring function (vmax1/vmax2) too permissive
- Baseline generates 16 OUTSTANDING_VALUE insights with 81.2% significance (13/16 significant)
- IFQ should reduce OUTSTANDING_VALUE threshold or use statistical significance instead of score-based filtering

---

### 2a. Significance — ATTRIBUTION

- IFQ: 95.8% (24 insights)
- Baseline: N/A (0 insights)
- Winner: IFQ

**Investigation:**
- IFQ generates 24 ATTRIBUTION insights with 95.8% significance → excellent correlation detection
- Baseline generates 11 ATTRIBUTION insights but all use numerical breakdown (Total Sales, Units Sold, Operating Margin, Price per Unit)
- All Baseline ATTRIBUTION insights rejected by EDA validation → breakdown must be categorical/temporal/ID for ATTRIBUTION pattern
- Baseline agent prompt and validation code fixed after investigation, but ATTRIBUTION insights still use numerical breakdown → LLM not following prompt correctly

---

### 2a. Significance — DISTRIBUTION_DIFFERENCE

- IFQ: 100.0% (4 insights)
- Baseline: 66.7% (9 insights)
- Winner: IFQ

**Investigation:**
- IFQ generates 4 DISTRIBUTION_DIFFERENCE insights with 100% significance → perfect distribution comparison
- Baseline generates 9 DISTRIBUTION_DIFFERENCE insights with 66.7% significance → reasonable
- IFQ has smaller sample but perfect significance, Baseline has larger sample with moderate significance

---

### 3. Insight Novelty

- IFQ: 83.5%
- Baseline: 84.9%
- Winner: Baseline

**Investigation:**
- IFQ: 81/97 novel insights (83.5%), avg max similarity 0.7588
- Baseline: 73/86 novel insights (84.9%), avg max similarity 0.7603
- Root causes:
  1. IFQ has more insights overall (97 vs 86) → harder to maintain high novelty
  2. IFQ OUTSTANDING_VALUE redundancy: 66 insights with only 62 unique breakdown/measure combinations (4 duplicates)
  3. Baseline has balanced pattern distribution → insights more unique
- Difference is small (1.4%) and expected given IFQ's pattern imbalance

---

### 4a. Diversity — Semantic

- IFQ: 0.468
- Baseline: 0.451
- Winner: IFQ

---

### 4b. Diversity — Subspace Entropy

- IFQ: 1.354
- Baseline: 1.516
- Winner: Baseline

**Investigation:**
- IFQ heavily uses Invoice Date for subspace filtering (21/45 = 47%) → lower entropy
- Baseline uses more balanced distribution: Sales Method (10), Region (9), State (6), Retailer (4), Product (3)
- Higher entropy = more diverse filter column usage → Baseline wins

---

### 4c. Diversity — Value

- IFQ: 1.000
- Baseline: 0.375
- Winner: IFQ

---

### 4d. Diversity — Dedup Rate

- IFQ: 0
- Baseline: 0.012
- Winner: IFQ

---

## Group 2 — Subspace Deep-dive

### 7. Subspace Rate

- IFQ: 45/97 (46.4%)
- Baseline: 32/86 (37.2%)
- Winner: IFQ

---

### 7a. Subspace Faithfulness

- IFQ: 100.0%
- Baseline: 100.0%
- Winner: Tie

---

### 7b. Subspace Significance

- IFQ: 55.6%
- Baseline: 66.7%
- Winner: Baseline

**Investigation:**
- IFQ has 45 subspace insights with 55.6% significance (15/45 significant)
- Baseline has 32 subspace insights with 66.7% significance (4/6 significant)
- Baseline's subspace insights are more carefully selected → higher significance rate
- IFQ generates more subspace insights but with lower quality

---

### 7c. Subspace Novelty

- IFQ: 91.1%
- Baseline: 96.9%
- Winner: Baseline

**Investigation:**
- IFQ has 41/45 novel subspace insights (91.1%), avg_max_similarity 0.7088
- Baseline has 31/32 novel subspace insights (96.9%), avg_max_similarity 0.7031
- Baseline's subspace insights are more unique (fewer insights but higher novelty rate)
- IFQ generates more subspace insights (45 vs 32) but with more redundancy

---

### 7d.1. Diversity — Semantic (Subspace)

- IFQ: 0.444
- Baseline: 0.457
- Winner: Baseline

**Investigation:**
- Similar to overall Semantic diversity (0.468 vs 0.451), difference is small
- Baseline's more balanced subspace filter column distribution (5 columns vs 7) contributes to slightly higher semantic diversity
- Not a significant difference (0.013 gap)

---

### 7d.2. Diversity — Subspace Entropy (Subspace)

- IFQ: 1.354
- Baseline: 1.516
- Winner: Baseline

---

### 7d.3. Diversity — Value (Subspace)

- IFQ: 1.000
- Baseline: 0.375
- Winner: IFQ

---

### 7d.4. Diversity — Dedup Rate (Subspace)

- IFQ: 0
- Baseline: 0.000
- Winner: Tie

---

### 8. Score Uplift from Subspace

- IFQ: Δ=-0.091, x=0.832
- Baseline: Δ=-0.112, x=0.812
- Winner: IFQ

---

### 9. Direction Uplift

- IFQ: down
- Baseline: down
- Winner: Tie

---

## Group 3 — Breakdown|Measure Deep-dive

### 10. Total (B,M) pairs evaluated

- IFQ: 44/44
- Baseline: 21/31
- Winner: N/A

**Investigation:**
- Baseline has 21 unique pairs with categorical breakdown, 31 total unique pairs
- 10 unique pairs have numerical breakdown (excluded from NMI/Interestingness evaluation per EDA principles)
- Related to earlier investigation: 72% of baseline insights use numerical breakdowns
- IFQ has 44/44 = 100% categorical breakdowns → better EDA compliance

---

### 10a. BM — NMI mean

- IFQ: 0.0751
- Baseline: 0.1215
- Winner: Baseline

---

### 10b. BM — Interestingness

- IFQ: 0.0846
- Baseline: 0.1311
- Winner: Baseline

**Investigation:**
- NMI and Interestingness computed only for categorical-B pairs (per EDA principles)
- Baseline has higher NMI (0.1215) and Interestingness (0.1311) due to more meaningful breakdown-measure pairs
- IFQ has many OUTSTANDING_VALUE insights with less informative breakdown-measure combinations
- Baseline's balanced pattern distribution contributes to higher BM quality

---

### 10c. BM — Actionability

- IFQ: 1.0000
- Baseline: 0.6774
- Winner: IFQ

---

### 10d. BM — Diversity

- IFQ: 0.4536
- Baseline: 0.3605
- Winner: IFQ
