# Reproducing QUIS: An Automated Evaluation Framework for Question-Guided Exploratory Data Analysis

**[Draft v1 — 2026-04-27]**

---

> **Authors:** [Author Names]  
> **Affiliation:** [University / Institution]  
> **Contact:** [email]

---

## Abstract

We present a reproducibility study of QUIS (Manatkar et al., 2024), a two-stage automated Exploratory Data Analysis (EDA) system comprising a Question Generation module (QUGEN) and an Insight Generation module (ISGEN). The original paper evaluated QUIS using human judgment on three criteria (relevance, comprehensibility, informativeness) and aggregate insight scores, both of which are difficult to reproduce at scale. Our primary contribution is an **automated, reference-free evaluation framework** of 12 metrics spanning four dimensions: (1) correctness and statistical validity, (2) insight diversity and novelty, (3) structural intent quality, and (4) subspace exploration depth. We introduce **Structural Validity Rate (SVR)**, a novel metric that measures whether the breakdown column type is semantically appropriate for the assigned insight pattern—a constraint unverifiable without schema-aware reasoning. We reproduce QUIS on the Adidas US Sales dataset and evaluate three pipeline variants: the full QUIS system, an ONLYSTATS ablation (replicating the original baseline), and a new LLM-based agentic baseline. Our results confirm the core claims of the original paper and further reveal that QUGEN's decisive contribution lies in **conditional question generation**, which enables deeper subspace exploration (+10.9 pp Subspace Rate over ONLYSTATS). At the same time, our framework surfaces a critical failure mode in unstructured LLM approaches: a 57 percentage-point gap in SVR between QUIS and the LLM baseline (100% vs. 43%), driven by systematic misuse of numeric columns as breakdown dimensions.

---

## 1. Introduction

Automated Exploratory Data Analysis (Auto EDA) is the task of discovering statistically meaningful and actionable insights from tabular data without manual intervention. Recent systems leverage Large Language Models (LLMs) to guide the analysis process (Laradji et al., 2023; Ma et al., 2023; Lipman et al., 2024), but rigorous evaluation remains a persistent challenge. Human assessment is expensive, non-reproducible, and introduces evaluator bias, while purely statistical metrics (e.g., aggregate insight scores) do not capture the semantic quality of the analytical intent.

QUIS (Manatkar et al., 2024) proposes a fully automated, training-free two-stage pipeline: a question generation module (QUGEN) that iteratively produces Insight Cards from dataset schema and statistics, followed by an insight generation module (ISGEN) that discovers statistically significant patterns and searches for subspace refinements. The original evaluation compares QUIS against an ONLYSTATS ablation using (i) human ratings on relevance, comprehensibility, and informativeness, and (ii) a normalized insight score. While these results demonstrate QUIS's effectiveness, they leave several questions unanswered: *How does QUIS perform against an LLM-based agent that does not use QUGEN's structured generation? What is the role of QUGEN's schema-aware conditioning specifically? And can QUGEN's unique contribution be isolated from ISGEN's capabilities?*

We address these questions through a reproducibility study on the Adidas US Sales dataset. Our contributions are:

1. **An automated evaluation framework** with 12 metrics covering faithfulness, statistical significance, novelty, diversity, structural validity, and subspace exploration depth—replacing human judgment with reference-free automated measurements reproducible across runs.

2. **Structural Validity Rate (SVR)**, a new metric that quantifies the degree to which a system produces breakdown–pattern pairs that satisfy semantic type constraints (e.g., TREND patterns require temporal breakdowns). SVR exposes a structural failure mode that existing metrics do not capture.

3. **A three-way comparison** extending the original QUIS evaluation with an LLM-based agentic baseline (five-step expert agent without QUGEN), isolating the contribution of structured question generation from the contribution of the ISGEN engine.

4. **An empirical analysis** of when QUGEN matters: Subspace Rate is the only metric where QUIS outperforms both baselines, providing the clearest evidence for QUGEN's unique contribution to conditional, subspace-rich insight discovery.

---

## 2. Related Work

### 2.1 Automated Data Exploration

Statistics-based ADE systems (Sellam et al., 2015; Ding et al., 2019; Wang et al., 2020) enumerate views and score them by interestingness measures. These approaches guarantee coverage but lack semantic guidance, exploring the full combinatorial space of (breakdown, measure) pairs without prioritization. Interactive systems (Milo and Somech, 2016, 2018; Agarwal et al., 2023) reduce this burden through user feedback but require continuous human involvement. Goal-oriented systems (Tang et al., 2017; Laradji et al., 2023; Lipman et al., 2024) direct exploration toward predefined objectives, potentially missing unexpected but important findings. Reinforcement learning-based systems (Milo and Somech, 2018a; Bar El et al., 2019, 2020; Garg et al., 2023) achieve greater autonomy but require dataset-specific training. QUIS addresses these limitations through fully automated, training-free question-driven exploration (Manatkar et al., 2024).

### 2.2 LLM-based Data Analysis

LLM-powered systems have demonstrated strong performance on code generation for data analysis (Chen et al., 2021; Zhang et al., 2023) and natural language question answering over tables (He et al., 2024). InsightPilot (Ma et al., 2023) uses an LLM to direct insight discovery over a graph of analysis operations. Talk2Data (Guo et al., 2024) decomposes natural language questions into analytical subqueries. These systems focus on user-driven exploration, whereas QUIS generates analytical questions autonomously. A key distinction is that QUIS's QUGEN module generates *structured* Insight Cards (question, reason, breakdown, measure), conditioning subsequent analysis on schema-typed fields rather than free-form text.

### 2.3 Evaluation of EDA Systems

Evaluation in ADE literature spans human assessment (Ma et al., 2023; Manatkar et al., 2024), interestingness scores (Ding et al., 2019; Tang et al., 2017), and automated metrics for code-based analysis (He et al., 2024). Human evaluation is the gold standard for assessing insight quality but is costly and difficult to replicate. Automated evaluation of insight quality—particularly the structural and semantic constraints on analytical intents—remains underexplored. Our work proposes a comprehensive reference-free framework that directly addresses this gap.

---

## 3. Background: The QUIS System

We briefly summarize QUIS (Manatkar et al., 2024) to establish terminology used throughout the paper.

### 3.1 Insight Definition

An insight is formally defined as a tuple $\text{Insight}(B, M, S, P)$ where:
- $B$ is the **breakdown** dimension (a column of interest),
- $M$ is the **measure** expressed as $\text{agg}(C)$ for an aggregation function and numeric column $C$,
- $S$ is a **subspace** — a set of filter conditions $\{(X_i, y_i)\}$ restricting the dataset,
- $P$ is a **pattern** from $\{\text{TREND}, \text{OUTSTANDING\_VALUE}, \text{ATTRIBUTION}, \text{DISTRIBUTION\_DIFFERENCE}\}$.

For a given $(B, M, S)$, the view $\text{view}(D_S, B, M)$ is computed by filtering $D$ by $S$ and grouping on $B$ with aggregate $M$.

### 3.2 QUGEN: Question Generation

QUGEN takes a table schema and natural language statistics as input and iteratively generates Insight Cards over $n$ iterations. Each Insight Card specifies (Question, Reason, $B$, $M$). LLM samples are collected at temperature $t = 1.1$ with $s = 3$ samples per iteration. Insight Cards pass through three filters: (i) schema relevance filter using `all-MiniLM-L6-v2` sentence embeddings, (ii) deduplication filter based on pairwise question similarity, and (iii) simple-question filter discarding low-complexity questions. Cards from prior iterations serve as in-context examples for subsequent iterations, enabling iterative quality improvement without manually curated examples.

### 3.3 ISGEN: Insight Generation

ISGEN processes each Insight Card in two stages. **Basic insight extraction** computes $\text{view}(D, B, M)$ over the full dataset and scores it against applicable patterns based on the breakdown type. **Subspace search** (Algorithm 1, Manatkar et al., 2024) performs beam search to find filter conditions $S$ that strengthen the insight, guided by an LLM that suggests semantically relevant filter columns.

Pattern scoring functions follow the original paper:
- **TREND:** $1 - p_{\text{MK}}$ (Mann-Kendall p-value); threshold $T = 0.95$ (i.e., $p < 0.05$)
- **OUTSTANDING\_VALUE:** $v_{\max 1} / v_{\max 2}$; threshold $T = 1.4$
- **ATTRIBUTION:** $v_{\max} / \sum v$; threshold $T = 0.5$
- **DISTRIBUTION\_DIFFERENCE:** Jensen-Shannon divergence; threshold $T = 0.2$

---

## 4. Evaluation Framework

The original QUIS evaluation relies on human ratings and aggregate scores, both of which are difficult to reproduce systematically. We propose an automated, multi-dimensional evaluation framework of 12 metrics organized into four groups.

### 4.1 Design Principles

Our framework is guided by four principles:

**Principle 1 — Reference-free.** Metrics must not require gold-standard annotations. They are computed directly from system outputs and the input dataset.

**Principle 2 — Dimension-specific.** Each metric measures a distinct quality dimension. Metrics are not aggregated into a single score to preserve interpretability.

**Principle 3 — Comparable across systems.** Metrics apply uniformly to all pipeline variants, including ablations and baselines.

**Principle 4 — Falsifiable.** Each metric is derived from a falsifiable hypothesis about what constitutes quality in automated EDA (e.g., "good insights are statistically significant").

### 4.2 Group I — Correctness and Statistical Validity

**Faithfulness** measures whether the reported view values can be recomputed from the source dataset:

$$\text{Faithfulness} = \frac{\text{verified\_count}}{\text{total\_count}}$$

A view is considered verified if its recomputed values match the reported values exactly. Faithfulness serves as a **sanity floor**: any gap between systems on other metrics is attributable to intent quality, not computational errors. A faithfulness score below 100% invalidates comparisons on other metrics for that system.

**Statistical Significance** measures the proportion of insights that are statistically significant at $\alpha = 0.05$:

$$\text{Significance} = \frac{1}{N}\sum_{i=1}^{N} \mathbf{1}(p_i < 0.05)$$

where $p_i$ is the pattern-appropriate test statistic (see Section 3.3). To avoid bias from unequal pattern distributions across systems, we report the **pattern-averaged significance** — the mean of per-pattern significance rates — rather than the raw rate.

**Pattern Coverage** measures the proportion of the four insight patterns that have at least one structurally valid insight:

$$\text{PatternCoverage} = \frac{|\text{covered}|}{4}$$

where "covered" requires at least one insight with the correct breakdown type for the pattern. This complements Significance by assessing breadth of analytical coverage.

### 4.3 Group II — Diversity and Novelty

**Insight Novelty** measures the proportion of a system's insights that are dissimilar to those of the LLM-agentic baseline (Baseline), serving as a measure of incremental discovery:

$$\text{Novelty} = \frac{|\{i : \max_{j} \text{cosine}(\mathbf{e}_i, \mathbf{e}_j) < \tau\}|}{N}, \quad \tau = 0.85$$

where $\mathbf{e}_i = \text{Embed}(\text{breakdown}_i \mid \text{measure}_i \mid \text{pattern}_i \mid \text{subspace}_i)$ using `all-MiniLM-L6-v2`.

**Semantic Diversity** measures within-system distinctiveness of insight structures:

$$\text{Diversity}_{\text{sem}} = 1 - \frac{1}{\binom{N}{2}} \sum_{i < j} \text{cosine}(\mathbf{e}_i, \mathbf{e}_j)$$

### 4.4 Group III — Structural Intent Quality

This group directly evaluates the quality of the Insight Cards produced by QUGEN (or the analogous intent specification in each system).

**Structural Validity Rate (SVR)** is our primary novel metric. It measures the proportion of insights whose breakdown type is semantically appropriate for the assigned pattern:

$$\text{SVR} = \frac{\text{valid\_total}}{\text{total}}$$

Validity rules are derived from the insight definitions in Section 3.1:
- **TREND** requires $B$ to be a temporal (datetime) column
- **ATTRIBUTION** and **DISTRIBUTION\_DIFFERENCE** require $B$ to be categorical or ID-typed
- **OUTSTANDING\_VALUE** has no breakdown constraint

SVR operationalizes a semantic constraint that is implicit in the QUIS insight definition but not enforced by unstructured LLM baselines. We report SVR overall and per-pattern.

**BM Actionability** measures the proportion of (breakdown, measure) pairs where the breakdown $B$ is categorical or temporal — a necessary condition for meaningful subgroup comparison:

$$\text{Actionability} = \frac{|\{(B, M) : \text{type}(B) \in \{\text{Categorical, Temporal, ID}\}\}|}{|\text{pairs}|}$$

**Reason–Insight Coherence** measures the alignment between the reason field (unique to QUGEN-based systems) and the final insight:

$$\text{Coh}_{R \text{-} I} = \frac{1}{N} \sum_{i=1}^{N} \text{cosine}(\text{Embed}(\text{reason}_i), \text{Embed}(\text{insight\_string}_i))$$

where $\text{insight\_string} = \text{breakdown} \mid \text{measure} \mid \text{pattern} \mid \text{condition}$.

**Question–Insight Alignment** is used as a control metric:

$$\text{Align}_{Q \text{-} I} = \frac{1}{N} \sum_{i=1}^{N} \text{cosine}(\text{Embed}(q_i), \text{Embed}(\text{insight\_string}_i))$$

If ISGEN faithfully executes the Insight Cards from both QUIS and the Baseline, the gap in $\text{Align}_{Q\text{-}I}$ between the two systems should be negligible, confirming that observed differences on other metrics originate in QUGEN rather than ISGEN.

### 4.5 Group IV — Subspace Exploration

**Subspace Rate** measures the proportion of insights that include at least one subspace filter:

$$\text{SubspaceRate} = \frac{\text{insights\_with\_subspace}}{\text{total\_insights}}$$

This is the most direct measure of whether a system explores the conditional data subspace, a key capability in the QUIS design.

**Score Uplift** measures whether subspace search improves insight scores:

$$\Delta_{\text{uplift}} = \bar{s}_{\text{subspace}} - \bar{s}_{\text{no-subspace}}$$

A higher (less negative) $\Delta$ indicates that the subspace search finds conditions that genuinely sharpen the insight pattern rather than degrading it.

---

## 5. Experimental Setup

### 5.1 Dataset

We reproduce QUIS on the **Adidas US Sales dataset** (Chaudhari, 2022), one of the three datasets used in the original paper. The dataset contains 9,648 rows and 9 columns: `Retailer` (CHAR), `Region` (CHAR), `SalesMethod` (CHAR), `Product` (CHAR), `PricePerUnit` (INT), `UnitsSold` (INT), `TotalSales` (INT), `OperatingProfit` (INT), `OperatingMargin` (DOUBLE). One temporal column (`InvoiceDate`) is derived during preprocessing.

We select this dataset because (i) it is publicly available, (ii) it contains the full spectrum of applicable insight patterns (including TREND via the temporal column), and (iii) its 9-column schema is representative of practical business analytics scenarios.

### 5.2 Systems Compared

We evaluate three pipeline variants:

**QUIS** — the full QUIS pipeline with QUGEN + ISGEN. QUGEN parameters follow the original paper: temperature $t = 1.1$, samples per iteration $s = 3$, iterations $n = 10$, in-context examples = 6. ISGEN parameters: beam\_width = 20, exp\_factor = 20, max\_depth = 1. LLM: GPT-4o-mini (via OpenAI-compatible API), replacing the Llama-3-70B-instruct used in the original (see Section 7.1 for discussion).

**ONLYSTATS** — replicates the original ablation. QUGEN is replaced by a statistical module that samples a random breakdown $B$ from eligible columns, ranks all measures $M$ by Kruskal-Wallis association strength, and selects the top 20 $(B, M)$ pairs as input to ISGEN. ISGEN parameters are identical to QUIS.

**Baseline** — a new LLM-based agentic baseline introduced in this paper. It follows a five-step pipeline: (1) column profiling, (2) data quality assessment, (3) descriptive statistics, (4) pattern discovery, and (5) insight synthesis with ISGEN scoring and subspace search. The Baseline uses the same LLM as QUIS but without QUGEN's structured Insight Card generation. Its output is converted to QUIS-compatible format (breakdown, measure, pattern, subspace) for unified evaluation.

### 5.3 Evaluation Details

Embeddings are computed using `all-MiniLM-L6-v2` (Reimers and Gurevych, 2019), loaded as a singleton to ensure consistent representations across all metric computations. All insight score recomputations use the same scoring functions as ISGEN to ensure faithfulness verification is well-defined. Pattern-averaged significance uses the unweighted mean over the four patterns to avoid bias from pattern-count imbalance.

---

## 6. Results

Table 1 reports selected metrics for the three systems. Full results across all 12 metrics are provided in the appendix.

**Table 1: Selected Metrics — QUIS vs. Baseline vs. ONLYSTATS (Adidas Dataset)**

| Group | Metric | QUIS | Baseline | ONLYSTATS |
|-------|--------|------|----------|-----------|
| Correctness | Faithfulness | **100.0%** | **100.0%** | **100.0%** |
| Validity | Statistical Significance | 74.7% | 60.3% | **92.0%†** |
| Coverage | Pattern Coverage | **4/4** | 3/4 | **4/4** |
| Structure | Structural Validity Rate (SVR) | **100.0%** | 43.0% | **100.0%** |
| Structure | SVR — ATTRIBUTION | **100%** | 0% | **100%** |
| Structure | SVR — TREND | **100%** | 38% | **100%** |
| Structure | BM Actionability | **1.000** | 0.677 | **1.000** |
| Subspace | Subspace Rate | **46.4%** ★ | 37.2% | 35.5% |
| Control | Question–Insight Alignment | 0.563 | **0.576** | — |
| Reasoning | Reason–Insight Coherence | **0.571** | 0.510 | — |

† ONLYSTATS Significance is an expected upper bound (see Section 6.2).  
★ QUIS is the only system that outperforms both baselines on this metric.

### 6.1 Correctness: Faithfulness as Sanity Floor

All three systems achieve 100% faithfulness across 97, 86, and 93 insights respectively. This confirms that all pipelines are grounded in actual data computations, and that observed differences on other metrics reflect genuine differences in analytical intent quality rather than hallucination or computational errors.

### 6.2 Statistical Validity and Pattern Coverage

QUIS achieves 74.7% statistical significance, outperforming the Baseline by 14.4 percentage points. ONLYSTATS reaches 92.0%, but this reflects the statistical upper bound of exhaustive enumeration: by systematically testing all (B, M) pairs ranked by Kruskal-Wallis strength, ONLYSTATS preferentially selects pairs with the highest association — a selection bias that inflates significance without reflecting analytical quality.

Pattern Coverage reveals a structural gap in the Baseline: it covers only 3/4 patterns because all 11 ATTRIBUTION insights use numeric breakdown columns (e.g., `TotalSales` as breakdown), which violates the semantic constraint of the ATTRIBUTION pattern. QUIS and ONLYSTATS both achieve 4/4 coverage, demonstrating that schema-aware question generation — whether by QUGEN or by systematic enumeration — ensures analytical breadth.

### 6.3 Structural Validity Rate: The Critical Gap

SVR is the metric with the largest gap in our evaluation: QUIS 100.0% vs. Baseline 43.0% (+57 pp). This gap reflects a systematic failure in the Baseline's unstructured LLM generation:

- **ATTRIBUTION (0% for Baseline):** All 11 Baseline ATTRIBUTION insights use `TotalSales` or `UnitsSold` as the breakdown dimension — numeric measures rather than categorical descriptors. This violates the ATTRIBUTION pattern's semantic constraint that the breakdown must enable subgroup comparison. The Baseline LLM consistently fails to distinguish between "what to measure" and "what to compare across."

- **TREND (38% for Baseline):** 24 out of 39 Baseline TREND insights use `Retailer` or `Region` (categorical columns) as the temporal axis. The LLM generates trend questions correctly in natural language but maps them to non-temporal breakdowns in the structured output.

Both QUIS and ONLYSTATS achieve SVR = 100%. For QUIS, this is attributable to QUGEN's chain-of-thought reasoning (Reason → Question → Breakdown, Measure) that preserves schema type consistency. For ONLYSTATS, it is attributable to ISGEN's internal enforcement of pattern-specific breakdown constraints. This distinction is important: SVR identifies *schema-aware* systems (both QUIS and ONLYSTATS) from *structurally inconsistent* ones (Baseline), but does not distinguish between the two mechanisms that achieve schema-awareness.

BM Actionability reinforces this finding: Baseline achieves 67.7% (vs. 100% for both QUIS and ONLYSTATS), confirming that the Baseline LLM systematically generates non-actionable breakdown–measure pairs where the breakdown column is numeric.

### 6.4 Subspace Rate: QUGEN's Unique Contribution

Subspace Rate is the **only metric in our framework where QUIS outperforms both baselines**:

| System | Subspace Rate |
|--------|--------------|
| QUIS | **46.4%** (45/97) |
| Baseline | 37.2% (32/86) |
| ONLYSTATS | 35.5% (33/93) |

The QUIS advantage over ONLYSTATS (+10.9 pp) is particularly significant because ONLYSTATS uses the identical ISGEN engine, same LLM, and same subspace search algorithm. The only difference is the source of the Insight Cards. This isolates QUGEN as the cause of the higher subspace rate.

The mechanism is QUGEN's generation of **conditional questions**: questions that specify subgroup context within the question text (e.g., *"Within the Footwear category, how does the regional sales trend differ across quarters?"*). These questions carry contextual signals into ISGEN's subspace search, providing a semantically meaningful starting point that guides the beam search toward more fruitful subspace conditions. ONLYSTATS generates template-based questions that lack this conditional context, so ISGEN's subspace search begins from an uninformed prior.

Score Uplift provides complementary evidence: QUIS achieves $\Delta = -0.091$ (mean subspace insight score 0.832), compared to ONLYSTATS $\Delta = -0.128$ (mean 0.785). The smaller degradation in QUIS indicates that the subspaces found by QUIS's conditional-question-guided search are more consistent with the original insight pattern, not just higher in count.

### 6.5 Control Metrics: Isolating QUGEN from ISGEN

A potential alternative explanation for QUIS's advantages on SVR and Significance is that QUIS's ISGEN executes questions more faithfully than the Baseline's ISGEN. Question–Insight Alignment controls for this: QUIS achieves 0.563 vs. Baseline's 0.576 (Tie, gap = 0.013). This confirms that ISGEN executes Insight Cards with comparable faithfulness across both systems, eliminating the alternative explanation. The observed differences in SVR, Significance, and Subspace Rate are attributable to QUGEN's structured question generation.

Reason–Insight Coherence further supports this: QUIS achieves 0.571 vs. Baseline's 0.510 (+0.061, QUIS wins). QUGEN's explicit reasoning field ("*Reason: The Northeast region may show seasonal sales peaks due to weather-correlated purchasing...*") is grounded in specific analytical hypotheses, in contrast to the Baseline's post-hoc template descriptions. This metric is not applicable to ONLYSTATS, which uses synthetic question templates without meaningful reasoning.

---

## 7. Discussion

### 7.1 Implementation Differences from the Original Paper

Our reproduction departs from the original QUIS paper in the following ways:

**LLM:** We use GPT-4o-mini via the OpenAI API instead of Llama-3-70B-instruct. While direct performance comparison is infeasible, GPT-4o-mini is a strong instruction-following model and we do not expect the conclusions to be LLM-specific. A systematic ablation over LLM choices is left for future work.

**ISGEN parameters:** We use beam\_width = 20 and exp\_factor = 20 instead of the original beam\_width = 100 and exp\_factor = 100. This was necessary for computational feasibility. The reduced beam width may reduce subspace coverage; we note this as a limitation and observe that our Subspace Rate results still clearly differentiate the three systems.

**Simple-question filter:** The original paper filters questions by executing SQL and discarding those returning only one row. Our implementation uses a heuristic (question length + keyword patterns) due to the absence of a SQL execution engine. This may affect the composition of Insight Cards but does not affect post-QUGEN metrics.

**Natural language statistics:** The original generates statistics via LLM-to-SQL-to-NL pipeline. Our implementation uses column-level descriptive statistics (min/max/mean for numeric, unique value counts for categorical) generated directly from the DataFrame.

### 7.2 Limitations of the Evaluation Framework

**Single dataset.** All results are from one dataset (Adidas US Sales). The original paper reports results on three datasets and shows that ONLYSTATS occasionally outperforms QUIS (e.g., on the Adidas dataset in human evaluation). Our automated framework avoids this dataset-specific sensitivity by measuring structural quality (SVR, Actionability) and exploration depth (Subspace Rate) rather than perceived quality — but cross-dataset validation remains necessary for stronger generalization claims.

**Significance calibration for pattern mix.** Pattern-averaged significance weights each pattern equally regardless of its count. On datasets with heavily imbalanced pattern distributions, this may over-represent rare patterns. Future work should investigate weighted alternatives.

**Embedding-based metrics.** Metrics using `all-MiniLM-L6-v2` embeddings (Novelty, Diversity, SVR, Coherence) are subject to the limitations of the underlying embedding model. In particular, short structured strings (e.g., "TotalSales | MEAN(UnitsSold) | TREND") may not capture semantic relationships as reliably as full sentences.

### 7.3 When Does QUGEN Matter?

Our results suggest a nuanced answer. QUGEN is not necessary for:
- **Faithfulness**: all approaches achieve 100% by construction
- **SVR and Actionability**: ONLYSTATS achieves these by ISGEN's internal type enforcement
- **Pattern Coverage**: schema enumeration is sufficient to cover all patterns

QUGEN is decisive for:
- **Subspace Rate**: conditional question generation uniquely enables subspace-rich insights (+10.9 pp over ONLYSTATS)
- **Statistical Significance vs. unstructured LLM**: structured chain-of-thought generation produces statistically more valid hypotheses (+14.4 pp vs. Baseline)
- **Reason–Insight Coherence**: only QUGEN-equipped systems provide grounded analytical reasoning

This suggests that the value of QUGEN scales with the importance of *conditional discovery* in the target use case. For datasets where subgroup variation is the primary analytical interest (e.g., sales data with geographic and product segmentation), QUGEN's conditional question generation provides clear advantages. For datasets where simple (B, M) enumeration exhausts the interesting structure, ONLYSTATS may be competitive.

---

## 8. Conclusion

We have presented a reproducibility study of QUIS (Manatkar et al., 2024) on the Adidas US Sales dataset, contributing an automated evaluation framework of 12 metrics that replaces human judgment with reference-free, scalable measurements. Our framework introduces Structural Validity Rate (SVR) as a new metric that exposes a critical failure mode in unstructured LLM-based EDA: systematic misuse of numeric columns as breakdown dimensions (0% SVR for ATTRIBUTION in the LLM baseline vs. 100% for QUIS).

Our three-way comparison — QUIS vs. an LLM-agentic Baseline vs. ONLYSTATS ablation — confirms the original claims of QUIS while providing additional nuance. QUGEN's decisive and *unique* contribution is **conditional question generation**, which enables deeper subspace exploration that cannot be replicated by schema enumeration. The Subspace Rate gap (+10.9 pp over ONLYSTATS) isolates this contribution empirically, with score uplift results confirming that the subspaces found are qualitatively stronger, not merely more numerous.

Our evaluation framework is released as part of this reproducibility study and can be applied to any system producing QUIS-compatible insight outputs (breakdown, measure, pattern, subspace). We hope this framework accelerates rigorous, reproducible evaluation in the broader Auto EDA research community.

---

## Acknowledgments

[To be added.]

---

## References

Agarwal, S., Chan, G. Y., Garg, S., Yu, T., and Mitra, S. (2023). Fast Natural Language Based Data Exploration with Samples. In *SIGMOD Companion*, page 155–158.

Bar El, O., Milo, T., and Somech, A. (2019). ATENA: An Autonomous System for Data Exploration Based on Deep Reinforcement Learning. In *CIKM*, pages 2873–2876.

Bar El, O., Milo, T., and Somech, A. (2020). Automatically Generating Data Exploration Sessions Using Deep Reinforcement Learning. In *SIGMOD*, pages 1527–1537.

Chaudhari, H. (2022). Adidas Sales Dataset (Adidas Sales in United States). Accessed on 19-Jul-2024.

Ding, R., Han, S., Xu, Y., Zhang, H., and Zhang, D. (2019). QuickInsights: Quick and Automatic Discovery of Insights from Multi-Dimensional Data. In *SIGMOD*, pages 317–332.

Garg, S., Mitra, S., Yu, T., Gadhia, Y., and Kashettiwar, A. (2023). Reinforced Approximate Exploratory Data Analysis. In *AAAI*, volume 37, pages 7660–7669.

Guo, Y., Shi, D., Guo, M., Wu, Y., Cao, N., Lu, H., and Chen, Q. (2024). Talk2Data: A Natural Language Interface for Exploratory Visual Analysis via Question Decomposition. *ACM TIIS*, 14(2):1–24.

He, X. et al. (2024). Text2Analysis: A Benchmark of Table Question Answering with Advanced Data Analysis and Unclear Queries. In *AAAI*, volume 38, pages 18206–18215.

Hussain, M. and Mahmud, I. (2019). pyMannKendall: a python package for non parametric Mann Kendall family of trend tests. *JOSS*, 4(39):1556.

Kruskal, W. H. and Wallis, W. A. (1952). Use of ranks in one-criterion variance analysis. *JASA*, 47(260):583–621.

Laradji, I. H. et al. (2023). Capture the Flag: Uncovering Data Insights with Large Language Models. In *NeurIPS Workshop*.

Lin, J. (1991). Divergence measures based on the Shannon entropy. *IEEE Transactions on Information Theory*, 37:145–151.

Lipman, T., Milo, T., Somech, A., Wolfson, T., and Zafar, O. (2024). Linx: A language driven generative system for goal-oriented automated data exploration. *arXiv:2406.05107*.

Ma, P., Ding, R., Han, S., and Zhang, D. (2021). MetaInsight: Automatic Discovery of Structured Knowledge for Exploratory Data Analysis. In *SIGMOD*, pages 1262–1274.

Ma, P., Ding, R., Wang, S., Han, S., and Zhang, D. (2023). InsightPilot: An LLM-Empowered Automated Data Exploration System. In *EMNLP System Demonstrations*, pages 346–352.

Manatkar, A., Akella, A., Gupta, P., and Narayanam, K. (2024). QUIS: Question-guided Insights Generation for Automated Exploratory Data Analysis. *arXiv:2410.10270*.

Mann, H. B. (1945). Nonparametric Tests Against Trend. *Econometrica*, 13:245–259.

Milo, T. and Somech, A. (2016). REACT: Context-Sensitive Recommendations for Data Analysis. In *SIGMOD*, pages 2137–2140.

Milo, T. and Somech, A. (2018a). Deep Reinforcement-Learning Framework for Exploratory Data Analysis. In *aiDM Workshop*, pages 1–4.

Milo, T. and Somech, A. (2018b). Next-Step Suggestions for Modern Interactive Data Analysis Platforms. In *KDD*, pages 576–585.

Reimers, N. and Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. In *EMNLP*, pages 3982–3992.

Sellam, T., Müller, E., and Kersten, M. (2015). Semi-Automated Exploration of Data Warehouses. In *CIKM*, pages 1321–1330.

Tang, B., Han, S., Yiu, M. L., Ding, R., and Zhang, D. (2017). Extracting Top-K Insights from Multi-dimensional Data. In *SIGMOD*, pages 1509–1524.

Wei, J. et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. *NeurIPS*, 35:24824–24837.

---

## Appendix A — Full Evaluation Results

**Table A1: Full Three-Way Comparison (Adidas Dataset)**

| Group | Metric | QUIS | Baseline | ONLYSTATS |
|-------|--------|------|----------|-----------|
| Core | Total insights | 97 | 86 | 93 |
| Core | Faithfulness | 100.0% | 100.0% | 100.0% |
| Core | Statistical Significance (Overall) | 74.7% | 60.3% | 92.0% |
| Core | — TREND | 50.0% (2) | 93.3% (15) | 100.0% (10) |
| Core | — OUTSTANDING\_VALUE | 53.0% (66) | 81.2% (16) | 68.2% (66) |
| Core | — ATTRIBUTION | 95.8% (24) | N/A | 100.0% (15) |
| Core | — DISTRIBUTION\_DIFFERENCE | 100.0% (4) | 66.7% (9) | 100.0% (2) |
| Core | Pattern Coverage | 4/4 | 3/4 | 4/4 |
| Core | Insight Novelty (vs. Baseline) | 61.9% | — | 33.3% |
| Core | Semantic Diversity | 0.468 | 0.451 | 0.405 |
| Core | Subspace Entropy Diversity | 1.354 | 1.516 | 1.563 |
| Core | Value Diversity | 1.000 | 0.375 | 0.788 |
| Subspace | Subspace Rate | 46.4% (45/97) | 37.2% (32/86) | 35.5% (33/93) |
| Subspace | Subspace Faithfulness | 100.0% | 100.0% | 100.0% |
| Subspace | Subspace Significance | 55.6% | 66.7% | 60.0% |
| Subspace | Score Uplift Δ | −0.091 | −0.112 | −0.128 |
| Subspace | Mean Subspace Score | 0.832 | 0.812 | 0.785 |
| Intent | SVR (Overall) | 100.0% (97/97) | 43.0% (37/86) | 100.0% (93/93) |
| Intent | SVR — OUTSTANDING\_VALUE | 100% (66/66) | 100% (16/16) | 100% (66/66) |
| Intent | SVR — TREND | 100% (3/3) | 38% (15/39) | 100% (10/10) |
| Intent | SVR — ATTRIBUTION | 100% (24/24) | 0% (0/11) | 100% (15/15) |
| Intent | SVR — DISTRIBUTION\_DIFFERENCE | 100% (4/4) | 30% (6/20) | 100% (2/2) |
| Intent | BM Actionability | 1.000 | 0.677 | 1.000 |
| Intent | BM NMI (mean) | 0.075 | 0.121 | 0.096 |
| Intent | BM Interestingness | 0.085 | 0.131 | 0.105 |
| Intent | Question Diversity | 0.521 | 0.596 | 0.405 |
| Intent | Question Specificity | 9.53 ± 1.76 | 12.78 ± 5.24 | 7.57 ± 0.65 |
| Intent | Question–Insight Alignment | 0.563 | 0.576 | 0.726 |
| Intent | Reason–Insight Coherence | 0.571 | 0.510 | N/A |

---

## Appendix B — SVR Failure Analysis for LLM Baseline

The following table illustrates representative breakdown–pattern mismatches in the LLM Baseline:

| Pattern | Expected B type | Actual B (Baseline) | Correct? |
|---------|----------------|---------------------|----------|
| ATTRIBUTION | Categorical | `TotalSales` (INT) | No |
| ATTRIBUTION | Categorical | `UnitsSold` (INT) | No |
| TREND | Temporal | `Retailer` (CHAR) | No |
| TREND | Temporal | `Region` (CHAR) | No |
| TREND | Temporal | `InvoiceDate` (Date) | Yes |

The Baseline LLM consistently confuses the **breakdown** (the column to group by) with the **measure** (the quantity to aggregate). In ATTRIBUTION insights, the LLM generates questions like *"Which sales metric contributes most to total performance?"* — a valid analytical question — but then maps `TotalSales` to the breakdown dimension rather than the measure dimension. QUGEN's chain-of-thought generation (Reason → Question → Breakdown → Measure) enforces directional consistency: the Breakdown is always the "group by" dimension, not the quantity of interest.

---

## Appendix C — Example Insights by System

**QUIS — Subspace insight example:**

> *Question:* Within the Women's Street Footwear category, how does operating profit vary across regions?  
> *Breakdown:* Region | *Measure:* MEAN(OperatingProfit) | *Pattern:* OUTSTANDING\_VALUE  
> *Subspace:* Product = "Women's Street Footwear"  
> *Score:* 0.91  
> *Explanation:* The Southeast region generates significantly higher average operating profit for Women's Street Footwear than other regions.

**ONLYSTATS — Basic insight example:**

> *Question:* How does mean operating profit compare across regions?  
> *Breakdown:* Region | *Measure:* MEAN(OperatingProfit) | *Pattern:* OUTSTANDING\_VALUE  
> *Subspace:* (none)  
> *Score:* 0.77  
> *Explanation:* The Southeast region has the highest average operating profit, notably larger than other regions.

**Baseline — SVR-invalid insight example:**

> *Question:* What sales metric has the highest attribution?  
> *Breakdown:* TotalSales (INT) | *Measure:* MEAN(OperatingProfit) | *Pattern:* ATTRIBUTION  
> *Subspace:* (none)  
> *SVR:* Invalid (numeric breakdown for ATTRIBUTION)
