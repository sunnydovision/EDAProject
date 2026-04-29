# Conclusion

This paper presented a reproduction of QUIS, an intent-driven automated exploratory data analysis
system, and introduced a set of evaluation metrics designed to measure the contribution of its
question generation module, QuGen. Experiments were conducted across three heterogeneous
real-world datasets — adidas sales, employee attrition, and online retail — comparing QUIS against
two baselines: a direct LLM-prompted baseline (Baseline) and a purely statistical template system
(ONLYSTATS).

## Summary of Findings

A surface-level reading of standard EDA evaluation metrics appears to favour the Baseline system.
Baseline achieves higher average statistical significance (57.6% vs. 46.4%), higher cross-system
insight novelty (86.2% vs. 72.4%), and higher per-pair breakdown informativeness as measured by
NMI (0.255 vs. 0.103) and Interestingness (0.253 vs. 0.137). However, we argue that these
apparent advantages are systematic artefacts of how the metrics were designed, rather than
evidence of superior analytical quality.

Statistical significance is structurally biased against subspace-conditional insights. QUIS
generates 84.4% of its insights with subspace filters, reducing sample sizes and consequently
statistical power. Insight novelty measures cross-theme breadth rather than within-theme depth;
QUIS deliberately explores multiple subspace variants of the same analytical theme, which
suppresses cross-system novelty scores while increasing analytical coverage. Similarly, NMI and
Interestingness reward sparse, high-precision (Breakdown, Measure) selection — a property that
favours systems which avoid comprehensive coverage. These observations motivate the need for
a richer evaluation framework that captures the qualitative dimensions of intent-driven EDA.

## Contribution of the QuGen Module

Our proposed evaluation metrics reveal a consistent and significant advantage for QUIS on
dimensions directly attributable to QuGen. We summarise the three principal findings.

**Structural semantic understanding.** The Structural Validity Rate (SVR), which measures
whether an insight's breakdown column type is semantically appropriate for its analytical pattern,
exposes the most substantial gap in the entire evaluation. QUIS achieves an SVR of 94.0%
averaged across datasets, compared to 40.0% for Baseline. Baseline frequently assigns numeric
columns to TREND patterns and temporal columns to ATTRIBUTION patterns, producing
structurally invalid insights that cannot yield meaningful statistical results. QuGen eliminates this
failure mode by generating a natural-language question prior to insight computation: the question
implicitly encodes the required column semantics — temporal for trend analysis, categorical for
attribution and distribution difference — constraining the insight engine to structurally valid
configurations. This advantage is corroborated by the per-pattern analysis: QUIS achieves 100%
SVR on ATTRIBUTION for adidas and employee_attrition, and 91–98% for
DISTRIBUTION_DIFFERENCE, while Baseline scores 0% on ATTRIBUTION for adidas and
online_sales.

**Subspace exploration quality.** QUIS generates subspace-conditional insights at more than
double the rate of Baseline (84.4% vs. 37.4%). More importantly, these insights are of higher
analytical quality: the Score Uplift ratio — defined as the mean effect size of subspace insights
relative to global insights — is 1.067 for QUIS versus 0.974 for Baseline and 0.528 for ONLYSTATS.
This result demonstrates that QuGen's question formulation actively steers the insight engine
toward data segments where patterns are amplified. The effect is most pronounced on
employee_attrition, where QUIS's subspace insights achieve effect sizes 57% stronger than their
global counterparts (score ratio x = 1.574). Furthermore, QUIS's subspace insights oppose the
global direction at a higher rate than Baseline (Contrasting Rate: 0.634 vs. 0.389 on adidas;
0.438 vs. 0.300 on employee_attrition), indicating that QuGen systematically surfaces
counter-narrative sub-population findings that global analysis would obscure.

**Intent layer coherence.** Among the intent-layer metrics, Baseline produces questions with
higher surface alignment to their corresponding insight text (Question–Insight Alignment: 0.569
vs. 0.540) and longer, more specific phrasing (Question Specificity: 12.11 vs. 9.80 words). We
attribute this to a fundamental methodological difference: Baseline constructs questions
retrospectively, after the insight has been computed, producing descriptions that naturally
resemble their source. QuGen generates questions prospectively, as analytical hypotheses that
drive the insight engine forward. A hypothesis ("How does attrition rate vary across departments
for high-tenure employees?") will necessarily diverge from the insight it produces, yet it is
precisely this forward-looking intent that guides the system toward structurally valid, subspace-rich
findings. The Reason–Insight Coherence metric, which measures how well QuGen's explanatory
reason is grounded in the actual insight content, marginally favours QUIS (0.526 vs. 0.514),
confirming that the intent layer produces semantically coherent output rather than generic
boilerplate.

## Implications for EDA Evaluation

The results of this study highlight a broader limitation in the evaluation of automated EDA systems.
Metrics derived from information retrieval and statistical hypothesis testing — significance rates,
NMI, cross-system novelty — were originally designed for globally-scoped, low-cardinality insight
generation tasks. Applied to an intent-driven system that deliberately explores conditional,
subspace-level patterns, these metrics produce systematically misleading comparisons. We propose
that future EDA evaluation frameworks incorporate, at minimum, the following complementary
dimensions: (i) Structural Validity Rate, to assess pattern–breakdown semantic compatibility;
(ii) Score Uplift from Subspace, to assess whether conditional filtering reveals stronger patterns
rather than weaker ones; and (iii) Contrasting Rate, to assess the proportion of subspace insights
that expose population heterogeneity invisible at the global level. Together, these metrics capture
what distinguishes an intent-driven EDA system from a statistical baseline: not the strength of
any individual insight in isolation, but the structural coherence and conditional richness of the
analytical narrative it produces.

## Conclusion

This paper reproduces QUIS faithfully — achieving 100% Faithfulness and matching or exceeding
pattern coverage across all datasets — and demonstrates that its QuGen module is the
architectural source of the system's most distinctive capabilities. While conventional metrics such
as statistical significance, insight novelty, and breakdown informativeness superficially favour the
simpler Baseline system, we show that these measures are structurally biased toward globally-scoped,
low-cardinality generation: they penalise the subspace exploration and comprehensive coverage that
QuGen deliberately enables. When evaluated on metrics designed to capture intent-driven quality,
QUIS leads decisively — achieving a Structural Validity Rate of 94.0% versus 40.0% for Baseline,
a Subspace Rate of 84.4% versus 37.4%, and a Score Uplift ratio of 1.067 versus 0.974, indicating
that QuGen not only drives broader conditional exploration but steers the insight engine toward
segments where patterns are genuinely amplified. These advantages originate from QuGen's
question-first design: by formulating a natural-language analytical question before invoking the
insight engine, QuGen encodes semantic constraints on breakdown type, anchors exploration to
meaningful sub-populations, and surfaces counter-narrative findings that global analysis obscures.
We therefore argue that standard EDA evaluation frameworks are insufficient for assessing
intent-driven systems, and propose Structural Validity Rate, Score Uplift from Subspace, and
Contrasting Rate as necessary complementary dimensions — metrics that capture the structural
coherence and conditional richness of the analytical narrative that QuGen produces.
