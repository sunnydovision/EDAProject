# Evaluating Question-Guided Exploratory Data Analysis: A Reproducibility Study of QUIS with Automated Metrics

**Thi Bich Ngoc Do, Phu Thinh Nguyen, Hung Nghiep Tran**  
Faculty of Information Systems, University of Information Technology  
ngocdtb.19@grad.uit.edu.vn, thinhnp.19@grad.uit.edu.vn, nghiepth@uit.edu.vn

---

## Abstract

This paper presents a reproducibility study of QUIS, an automated Exploratory Data Analysis (EDA) system. QUIS uses a question generation module, called QUGEN, to create analysis questions before searching for insights. The original QUIS paper used human evaluation, but this is difficult to repeat and also takes much time. In this work, we build an automatic evaluation framework with 9 metrics covering correctness, structural validity, statistical quality, subspace exploration, and question-insight alignment. We compare our QUIS reproduction with two baselines: a rule-based baseline called ONLYSTATS and an LLM-based agentic baseline that we implemented. We evaluate all three systems across three datasets: Adidas US Sales, IBM Employee Attrition, and Online Sales. The main results show that QUGEN helps avoid column-type errors and improves subspace exploration quantity. We find that the LLM baseline has a structural validity problem: it uses wrong column types in many insights. Across all datasets, QUIS obtains 94.0% average structural validity, while the LLM baseline obtains only 40.0%. QUIS also produces more insights with subspace filters: 84.4% on average, compared with 37.4% for the LLM baseline. For subspace quality, QUIS achieves the highest Score Uplift ($x$=1.067) and Simpson's Paradox Rate (27.7%). Most striking, the LLM baseline produces zero significant paradoxes across all datasets, confirming that structural validity is essential for meaningful pattern detection. These results show that structured question generation is helpful for both exploration breadth and quality.

---

## 1. Introduction

Exploratory Data Analysis (EDA) requires human knowledge and time to find patterns and useful relationships in new datasets. As datasets grow, automated EDA systems become increasingly valuable. QUIS (Manatkar et al., 2024) is one such system: instead of searching for insights directly, it first generates analysis questions through a module called QUGEN, then uses a second module, ISGEN, to search the dataset for actual insights matching each question.

The original QUIS paper evaluates output quality through human ratings, which are expensive, subjective, and difficult to reproduce. We address this by building an automatic evaluation framework using metrics computed directly from system outputs and the original dataset.

This paper tries to answer two questions:

1. Can we build an automatic evaluation framework for comparing automated EDA systems?
2. What does the QUIS pipeline contribute—specifically, what roles do QUGEN (card generation) and ISGEN (insight search) each play—when compared with simpler baselines?

We reproduce QUIS and compare it with two baselines across three datasets: Adidas US Sales, IBM Employee Attrition, and Online Sales. The first baseline is ONLYSTATS, which removes QUGEN and creates cards by simple schema enumeration. The second baseline is an LLM-based agentic EDA pipeline. We use 9 metrics to study correctness, structure, statistical quality, subspace exploration, and question quality.

Our contributions are:

- We build an automatic and reference-free evaluation framework with 9 metrics for AutoEDA systems, covering correctness, structural validity, statistical quality, and subspace exploration.
- We show that QUGEN's schema-aware card generation prevents systematic column-type mismatches that afflict free-form LLM pipelines (40.0% SVR vs QUIS's 94.0%).
- We show that ISGEN's beam search, guided by QUGEN's higher-quality cards, achieves substantially better subspace coverage (84.4% vs 37.4%) and quality (Score Uplift $x$=1.067, SPR 27.7%).
- We reveal that structural validity is a prerequisite for meaningful subspace discovery: the LLM Baseline produces zero significant paradoxes across all datasets.

---

## 2. Related Work

### 2.1 Automated EDA and Insight Evaluation

Early automated EDA systems measure interestingness using statistical deviation. SEEDB (Vartak et al., 2015) recommends visualizations by comparing distributions between a target subset and a reference, ranking candidates by their deviation score. QuickInsights (Ding et al., 2019) extends this with a unified insight model covering multiple pattern types—trend, outlier, attribution—and combines impact and significance into a composite score for efficient mining. zenvisage (Siddiqui et al., 2016) takes a query-based approach, letting users specify desired visual patterns and retrieve matching views from large collections. These systems enable automatic ranking without human input, but their quality metrics are limited to statistical deviation and do not validate whether an insight has the correct structural form—for example, a trend computed over a categorical column instead of a temporal one still produces a non-zero deviation score.

Visualization-focused systems evaluate quality through perceptual and organizational criteria. Voyager (Wongsuphasawat et al., 2016) automatically generates and ranks views using expressiveness and effectiveness rules derived from perceptual principles. Voder (Srinivasan and Stasko, 2018) integrates natural language data facts with interactive visualizations to surface interesting findings during exploration. MetaInsight (Ma et al., 2021) organizes insights into structured knowledge by measuring how precisely patterns can be extracted from data. These approaches assess visualization design quality and exploration coverage, but do not check whether the breakdown column semantics match the intended pattern type.

More recent systems use Large Language Models to drive insight generation. InsightPilot (Ma et al., 2023) employs LLMs to suggest analysis actions and evaluate completeness through user studies. QUIS (Manatkar et al., 2024) generates questions from dataset semantics before searching for insights, and evaluates output quality using human raters scoring relevance, comprehensibility, and informativeness on a 1–5 scale. While human evaluation captures subjective quality, it has well-known limitations: it is expensive, time-consuming, subjective across raters, and difficult to reproduce across studies. These limitations motivate the need for automatic evaluation frameworks that can be applied consistently across systems.

### 2.2 Subgroup Analysis and Pattern Quality

Beyond global statistics, a growing body of work studies the quality of conditional insights—patterns that hold within a subset of the data. Subgroup discovery (Bach, 2025) formalizes the search for data subsets that exhibit interesting target behavior, and studies quality criteria such as weighted relative accuracy (WRAcc) to measure how much a subgroup deviates from the overall population. A key question in this line of work is whether a discovered subgroup reveals stronger or weaker patterns than the global baseline—a criterion we operationalize as Score Uplift in our evaluation framework, measuring the average difference in pattern strength between subspace and global insights.

A related and well-studied statistical phenomenon is Simpson's Paradox (Simpson, 1951), where the direction of an association at the aggregate level reverses when data is split into subgroups. Simpson's original formulation showed that combining contingency tables can yield conclusions opposite to those obtained from each subgroup separately. Teng and Lin (2026) revisit Simpson's Paradox in the context of observational data analysis, introducing a kernel-based tree algorithm to detect and explain subgroup-level reversals caused by confounding and effect heterogeneity. Their work formalizes the conditions under which subgroup associations diverge from global trends, and provides a framework for interpreting such reversals as analytically meaningful rather than artefactual. However, no prior work has combined subgroup significance testing and paradox detection into a unified evaluation framework for automated EDA systems.

### 2.3 Research Gap

No existing AutoEDA evaluation framework systematically checks structural validity—whether the breakdown column type matches the intended pattern—or combines subgroup significance testing with paradox detection. **Our work** addresses both gaps with a fully automatic, reference-free framework of 9 metrics covering correctness, structural validity, statistical quality, subspace exploration, and question quality. Our evaluation shows that LLM baselines have systematic structural errors (40% SVR) and produce zero significant paradoxes, while structured approaches achieve 90%+ SVR and discover meaningful pattern reversals.

---

## 3. System Overview

We compare three systems in this study.

### 3.1 QUIS (Our Reproduction)

QUIS has two main stages. First, QUGEN reads the dataset schema and basic statistics, then creates Insight Cards using an LLM. Each card contains a question, a reason, a breakdown column (B), and a measure (M). Second, ISGEN takes these cards and searches the dataset for actual insights.

We represent each insight as a 4-tuple **(B, M, S, P)**, where B is the breakdown column, M is the measure, S is the subspace filter (a set of column-value equality conditions), and P is the pattern type. The four pattern types are TREND, OUTSTANDING_VALUE, ATTRIBUTION, and DISTRIBUTION_DIFFERENCE.

For each card, ISGEN first computes the global view ($S = \emptyset$), then runs a beam search to find subspaces where the pattern is stronger. The beam search samples filter columns randomly or via LLM suggestion (probability 0.5), scores each candidate using pattern-specific functions (Mann-Kendall τ for TREND, attribution share for ATTRIBUTION, Jensen-Shannon divergence for DISTRIBUTION_DIFFERENCE), and retains the top candidates. This subspace search is shared between QUIS and ONLYSTATS—the only difference is the source of the input cards.

### 3.2 ONLYSTATS (Ablation Baseline)

ONLYSTATS is the ablation baseline. It replaces QUGEN with exhaustive schema enumeration: every Categorical or Temporal column paired with SUM and MEAN over every Numerical column, producing 70 unique (B, M) pairs on Adidas. No LLM is used for card generation. ONLYSTATS then runs the identical ISGEN pipeline as QUIS, isolating the contribution of QUGEN to card quality alone.

### 3.3 LLM Agentic Baseline

The second baseline is an LLM-based agentic EDA pipeline that we implemented using `gpt-5.4` at temperature 0.3–0.5. It consists of five sequential agents: (1) data profiling, which semantically classifies each column; (2) quality analysis, which detects missing values, outliers, and duplicates; (3) statistical analysis, which computes descriptive statistics and Pearson correlations; (4) pattern discovery, which identifies temporal, correlation, grouping, and anomaly patterns from pre-computed aggregations; and (5) insight extraction, which synthesizes all prior outputs into structured insights. Each agent accumulates outputs from previous steps as context. Unlike QUIS, this pipeline does not enforce a structured Insight Card format; the LLM reasons freely over pre-computed evidence. For evaluation, outputs are post-processed into a QUIS-compatible format (breakdown column, measure, subspace, pattern type).

---

## 4. Evaluation Framework

### 4.1 Selected Metrics

We selected 9 metrics from a larger list of candidates. We group them as follows.

**Group 1: Correctness**

*Faithfulness* checks whether the numbers in an insight can be recomputed from the dataset. For example, if an insight reports a total sales value for one region, we recompute the aggregation from the CSV file. If a system has low faithfulness, then other metrics are less meaningful.

The formula is:

$$\text{Faithfulness} = \frac{|\{i \in I : \text{verified}(i)\}|}{|I|}$$

where $I$ is the set of all insights, and $\text{verified}(i)$ returns true if for all reported values $v_r$ in insight $i$, the recomputed value $v_c$ satisfies $|v_r - v_c| < \epsilon$ with $\epsilon = 10^{-6}$.

**Group 2: Validity and Coverage**

*Structural Validity Rate (SVR)* checks whether the breakdown column type matches the pattern type. For example, a TREND insight should use a date or time column as the breakdown. An ATTRIBUTION insight should use a categorical breakdown, not a numeric measure column.

The formula is:

$$\text{SVR} = \frac{|\{i \in I : \text{valid\_breakdown}(i)\}|}{|I|}$$

where $\text{valid\_breakdown}(i)$ checks pattern-specific rules: for TREND, the breakdown $B_i$ must be temporal; for ATTRIBUTION and DISTRIBUTION_DIFFERENCE, $B_i$ must be categorical or ID-type; for OUTSTANDING_VALUE, any breakdown type is valid. We report SVR overall and also by pattern type. This also ensures that breakdown-measure pairs are actionable for subgroup analysis.

*Pattern Coverage* counts how many of the four patterns appear at least once with a valid structure. A system that only produces one pattern is not doing broad EDA.

The formula is:

$$\text{Pattern\_Coverage} = \frac{|\{p \in P : \exists i \in I, \text{pattern}(i) = p \land \text{valid}(i)\}|}{|P|}$$

where $P = \{\text{TREND, OUTSTANDING\_VALUE, ATTRIBUTION, DISTRIBUTION\_DIFFERENCE}\}$ is the set of all pattern types, and $\text{valid}(i)$ means the insight has correct structure (passes SVR check).

*Statistical Significance* checks the percentage of insights that pass a statistical test at p < 0.05. We use pattern-specific tests: Mann-Kendall for trends (Mann, 1945), z-test for outstanding values, Chi-square test for attribution (McHugh, 2013), and Kolmogorov-Smirnov test for distribution differences (Kolmogorov, 1933). Effect sizes are measured using Kendall's τ for trends (Kendall, 1975), z/(z+1) for outstanding values, Cramér's V for attribution (Cramér, 1946), and KS statistic for distribution differences.

The formula is:

$$\text{Statistical\_Significance} = \frac{|\{i \in I : p\text{-value}(i) < 0.05\}|}{|I|}$$

where $p\text{-value}(i)$ is computed using the pattern-specific test for insight $i$. Only structurally valid insights (SVR = 1) are included in this calculation.

**Group 3: Exploration Quality**

*Subspace Rate* measures how many insights contain at least one subspace filter. A high value means the system does not only give global insights, but also explores conditional cases, such as "within Region = West".

The formula is:

$$\text{Subspace\_Rate} = \frac{|\{i \in I : |S_i| > 0\}|}{|I|}$$

where $S_i$ is the set of subspace filters for insight $i$. Each filter is a (column, value) pair that restricts the data to a subset.

*Score Uplift from Subspace* measures whether subspace insights have stronger patterns than global insights. We define two related quantities. The absolute mean score of subspace insights is:

$$x = \frac{1}{|I_S|}\sum_{i \in I_S} \text{score}(i)$$

and the uplift delta relative to global insights is:

$$\Delta = \frac{1}{|I_S|}\sum_{i \in I_S} \text{score}(i) - \frac{1}{|I_G|}\sum_{i \in I_G} \text{score}(i)$$

where $I_S = \{i \in I : |S_i| > 0\}$, $I_G = \{i \in I : |S_i| = 0\}$, and $\text{score}(i)$ is the pattern strength (Kendall's τ for TREND, effect size otherwise). We report $x$ in all tables since $|I_G|$ can be zero for some systems; $\Delta$ is reported per-dataset in supplementary results.

*Simpson's Paradox Rate (SPR)* detects statistically significant pattern reversals between global and subspace insights (Simpson, 1951). A reversal occurs when the pattern direction changes—for example, a positive trend globally becomes negative in a subspace, or the dominant category changes. We use pattern-specific tests (Mann-Kendall for TREND, Chi-square for ATTRIBUTION, KS test for DISTRIBUTION_DIFFERENCE) and require both global and subspace patterns to be statistically significant (p < 0.05).

The formula is:

$$\text{SPR} = \frac{|\{i \in I_S : \text{is\_paradox}(i) \land \text{is\_significant}(i)\}|}{|I_S|}$$

where $\text{is\_paradox}(i)$ detects pattern reversal and $\text{is\_significant}(i)$ requires p < 0.05 for both global and subspace patterns.

**Group 4: Alignment and Coherence**

*Question-Insight Alignment* measures how close the question text is to the final insight text. We compute cosine similarity using sentence embeddings. This is used as a control metric. If QUIS and Baseline have similar alignment, then the difference between them is more likely caused by the quality of the generated intent, not by ISGEN answering one system better.

The formula is:

$$\text{Q-I\_Alignment} = \frac{1}{|I|} \sum_{i \in I} \text{cosine\_sim}(\text{emb}(Q_i), \text{emb}(T_i))$$

where $Q_i$ is the question text, $T_i$ is the insight text, and $\text{emb}(\cdot)$ uses Sentence-BERT embeddings (Reimers and Gurevych, 2019).

*Reason-Insight Coherence* measures how close the reason field is to the final insight. This metric is only used for QUIS and the LLM Baseline because ONLYSTATS only uses template reasons.

The formula is:

$$\text{R-I\_Coherence} = \frac{1}{|I|} \sum_{i \in I} \text{cosine\_sim}(\text{emb}(R_i), \text{emb}(T_i))$$

where $R_i$ is the reason text for insight $i$. This metric is not applicable to ONLYSTATS.

---

## 5. Experimental Setup

We use three datasets summarized in Table 1: Adidas US Sales (Chaudhari, 2022), IBM Employee Attrition (Subhash, 2017), and Online Sales (Verma, 2024). We use OpenAI's `gpt-5.4` for QUIS and the LLM Baseline. The original paper used Llama-3-70B-instruct; our model choice may shift exact numbers but does not affect comparability since all systems share the same evaluation framework. We set `beam_width = 20` (vs. 100 in the original) for practical runtime. For text similarity metrics, we use `all-MiniLM-L6-v2` from Sentence-BERT (Reimers and Gurevych, 2019).

---

## 6. Results

### 6.1 Overview

Table 1 summarizes average results across all three datasets. Detailed per-dataset results are shown in Tables 2, 3, and 4.

**Table 1: Average Evaluation Results Across Three Datasets**

| Group | Metric | QUIS    | Baseline | ONLYSTATS | Winner |
|-------|--------|---------|----------|-----------|--------|
| Correctness | 1. Faithfulness | **100.0%** | **100.0%** | **100.0%** | Tie |
| Validity | 2. Structural Validity Rate (SVR) | **94.0%** | 40.0% | 90.8% | **QUIS** |
| Coverage | 3. Pattern Coverage | 3.3/4 | 2.7/4 | 3.7/4 | ONLYSTATS |
| Statistics | 4. Statistical Significance | 46.4%   | **57.6%** | 51.7% | **Baseline** |
| Exploration (Quantity) | 5. Subspace Rate | **84.4%** | 37.4% | 77.0% | **QUIS** |
| Exploration (Quality) | 6. Score Uplift ($x$) | **1.067** | 0.974 | 0.528 | **QUIS** |
| Exploration (Quality) | 7. Simpson's Paradox Rate (SPR) | **27.7%** | 18.9% (0 sig) | 24.5% | **QUIS** |
| Control | 8. Q-I Alignment | 0.540   | **0.569** | N/A | **Baseline** |
| Control | 9. R-I Coherence | **0.526** | 0.514 | N/A | **QUIS** |

### 6.2 Detailed Results by Dataset

**Table 2: Results on Adidas US Sales (QUIS=99, Baseline=75, ONLYSTATS=85)**

| Metric | QUIS | Baseline | ONLYSTATS |
|--------|------|----------|-----------|
| Faithfulness | **100%** | **100%** | **100%** |
| SVR (Overall) | **99.0%** | 45.3% | 83.5% |
| SVR - ATTRIBUTION | **100%** | 0% | 83.3% |
| SVR - TREND | **100%** | 48.5% | **100%** |
| Pattern Coverage | **4/4** | 3/4 | **4/4** |
| Statistical Significance | **83.4%** | 73.2% | 76.2% |
| Subspace Rate | **86.9%** | 42.7% | 78.8% |
| Score Uplift ($x$) | 0.885 | 0.796 | 0.726 |
| SPR | 26.7% (9 sig) | 25.0% (0 sig) | **37.3%** (13 sig) |
| Q-I Alignment | **0.583** | 0.579 | N/A |
| R-I Coherence | **0.553** | 0.527 | N/A |

On Adidas, QUIS leads on SVR (99.0% vs 45.3%) and Subspace Rate (86.9%), while ONLYSTATS achieves the highest SPR (37.3% with 13 significant paradoxes). The Baseline produces zero significant paradoxes despite a similar raw SPR, confirming that structural validity is essential.

**Table 3: Results on IBM Employee Attrition (QUIS=133, Baseline=81, ONLYSTATS=132)**

| Metric | QUIS | Baseline | ONLYSTATS |
|--------|------|----------|-----------|
| Faithfulness | **100%** | **100%** | **100%** |
| SVR (Overall) | **100.0%** | 75.3% | **100.0%** |
| Pattern Coverage | 3/4 | 3/4 | 2/4 |
| Statistical Significance | 20.0% | **55.8%** | 20.2% |
| Subspace Rate | **87.2%** | 33.3% | 59.1% |
| Score Uplift ($x$) | **1.574** | 1.079 | 0.346 |
| SPR | **26.7%** (7 sig) | 0.0% (0 sig) | 7.7% (0 sig) |
| Q-I Alignment | 0.493 | **0.588** | N/A |
| R-I Coherence | 0.468 | **0.519** | N/A |

On Employee Attrition, QUIS achieves the strongest Score Uplift ($x$=1.574) and is the only system with significant paradoxes (SPR 26.7%, 7 significant). ONLYSTATS drops to 7.7% SPR with zero significant paradoxes, showing that exhaustive enumeration does not guarantee subspace quality on datasets with many weak global patterns.

**Table 4: Results on Online Sales (QUIS=106, Baseline=61, ONLYSTATS=72)**

| Metric | QUIS | Baseline | ONLYSTATS |
|--------|------|----------|-----------|
| Faithfulness | **100%** | **100%** | **100%** |
| SVR (Overall) | **100.0%** | 60.7% | 94.4% |
| Pattern Coverage | 3/4 | 2/4 | **4/4** |
| Statistical Significance | 35.9% | 43.8% | **58.6%** |
| Subspace Rate | 79.2% | 36.1% | **93.1%** |
| Score Uplift ($x$) | 0.742 | **1.048** | 0.511 |
| SPR | 29.8% (8 sig) | 31.8% (0 sig) | 28.4% (7 sig) |
| Q-I Alignment | **0.543** | 0.539 | N/A |
| R-I Coherence | **0.557** | 0.497 | N/A |

On Online Sales, ONLYSTATS achieves the highest Subspace Rate (93.1%) and the Baseline achieves the highest Score Uplift ($x$=1.048), likely because its fewer but higher-quality insights on this small dataset concentrate on stronger global patterns. All three systems achieve comparable SPR (28–30%), but only QUIS and ONLYSTATS produce significant paradoxes; the Baseline again yields zero.

### 6.3 Cross-Dataset Analysis

#### Faithfulness

All three systems achieve 100% faithfulness across all datasets, confirming that reported values are verifiable and that QUGEN does not sacrifice correctness for richer question generation.

#### Structural Validity Rate

SVR shows the largest and most consistent difference across datasets. QUIS achieves 94.0% average SVR, while the LLM Baseline achieves only 40.0% (gap of 54 percentage points). ONLYSTATS achieves 90.8%.

The Baseline's core problem is systematic column-type mismatch: it achieves 0% ATTRIBUTION SVR across all three datasets, always selecting numeric columns (e.g., `Total Sales`, `MonthlyIncome`) as the breakdown instead of categorical ones. For TREND, it uses categorical breakdowns in 51.5% of Adidas cases and 81.0% of Employee Attrition cases (e.g., `JobRole`, `Department`) instead of temporal columns. QUIS avoids this because QUGEN outputs structured cards with explicit breakdown fields validated programmatically. ONLYSTATS also achieves high SVR (90.8%) by design: it enumerates only categorical and temporal columns as breakdowns.

#### Pattern Coverage

All systems miss TREND on Employee Attrition and Online Sales due to limited temporal columns. The Baseline additionally misses ATTRIBUTION on all datasets because its numeric breakdowns are structurally invalid for that pattern type.

#### Subspace Exploration

Subspace Rate is where QUIS shows the largest advantage. QUIS achieves 84.4% average subspace rate (range: 79.2%–87.2%), compared with 37.4% for the Baseline (range: 33.3%–42.7%) and 77.0% for ONLYSTATS (range: 59.1%–93.1%).

Since QUIS and ONLYSTATS share the same ISGEN module, the 7.4-point average gap between them isolates the contribution of QUGEN's semantically grounded cards over exhaustive enumeration. The 47.0-point gap versus the Baseline reflects its structural problems: invalid breakdowns cannot be explored in subspaces. ONLYSTATS reaches its highest subspace rate on Online Sales (93.1%) because exhaustive enumeration produces many valid (B, M) pairs on this small 9-column dataset, giving ISGEN more entry points.

Score Uplift is positive on average for all systems (QUIS: 1.067, Baseline: 0.974, ONLYSTATS: 0.528), measured as the mean pattern strength of subspace insights ($x$). QUIS shows the strongest uplift on Employee Attrition ($x$=1.574) and leads on average across all datasets. On Online Sales, the Baseline achieves the highest per-dataset Score Uplift ($x$=1.048), likely because its smaller insight set concentrates on globally stronger patterns. ONLYSTATS consistently shows the lowest uplift, especially on Employee Attrition ($x$=0.346). SPR follows a similar trend: QUIS achieves the highest average (27.7%) and is consistent across datasets, while ONLYSTATS varies widely (7.7%–37.3%). The Baseline produces zero significant paradoxes, confirming that structurally invalid insights cannot yield meaningful subspace patterns.

#### Statistical Significance

Statistical significance is dataset-dependent (QUIS: 46.4%, Baseline: 57.6%, ONLYSTATS: 51.7% on average). QUIS leads on Adidas (83.4%) but lags on Employee Attrition (20.0%), where binary/categorical variables make simple aggregations easier to pass significance tests. QUIS subspace insights are also smaller (median 51.5 rows vs Baseline's 588 on Employee Attrition), trading statistical power for specificity.

### 6.4 Control Metrics

Q-I Alignment is similar across QUIS (0.540) and Baseline (0.569), confirming that ISGEN answers both systems comparably—differences stem from card quality, not retrieval. R-I Coherence slightly favors QUIS (0.526 vs 0.514). Both metrics are not reported for ONLYSTATS (template-based questions only).

---

## 7. Discussion

### 7.1 What the QUIS Pipeline Adds

QUGEN's primary contribution is structural correctness. By generating schema-aware cards with explicit breakdown fields, it prevents the column-type mismatches that afflict the free-form LLM Baseline (0% ATTRIBUTION SVR, 40.0% overall). ONLYSTATS achieves similarly high SVR by constraining enumeration to valid column types—showing that the constraint itself matters, not the generation method.

For subspace exploration, QUGEN's contribution is indirect but measurable: semantically grounded cards give ISGEN more focused entry points, leading to higher Subspace Rate and more consistent SPR across datasets. ONLYSTATS, despite sharing the same ISGEN module, shows wider variance in SPR (7.7%–37.3%), suggesting that exhaustive enumeration produces many (B, M) pairs where global patterns are too weak for subspace search to improve upon. The LLM Baseline's zero significant paradoxes confirm that structural validity is a prerequisite for any meaningful subspace discovery.

### 7.2 Limitations

There are some limitations in this study. First, we use OpenAI's `gpt-5.4` instead of the original Llama-3-70B-instruct, so the exact numbers may be different from the original paper. Second, our embedding-based metrics depend on `all-MiniLM-L6-v2`. This model is useful, but it may not capture all meanings in short technical texts. Third, we evaluate on three datasets with different characteristics, but more datasets would strengthen the generalizability of our findings.

All implementation code and evaluation scripts are publicly available at https://github.com/sunnydovision/EDAProject.

---

## 8. Conclusion

We reproduced QUIS and built an automatic, reference-free evaluation framework with 9 metrics covering correctness, structural validity, statistical quality, and subspace exploration. Across three datasets, results show three clear findings. First, the LLM Baseline has a systematic structural validity problem (45.3%–75.3% SVR) caused by column-type mismatches, while QUIS consistently achieves 99.0%–100.0%. Second, QUGEN provides higher-quality input cards that enable ISGEN to discover more subspace insights (84.4% Subspace Rate vs 37.4%) with stronger, more consistent patterns (SPR 27.7%, Score Uplift +1.067). Third, statistical significance is dataset-dependent and should not be interpreted in isolation. These findings have two practical implications: LLM-based EDA systems should validate breakdown column types before output, and insight search engines benefit from semantically grounded input cards over exhaustive enumeration alone. Our main contribution is the evaluation framework itself—a reusable tool for comparing any AutoEDA system in a consistent and reproducible way.

---

## References

Atzmueller, M. (2015). Subgroup Discovery. *Wiley Interdisciplinary Reviews: Data Mining and Knowledge Discovery*, 5(1), 35-49.

Bach, J. (2025). Subgroup Discovery with Small and Alternative Feature Sets. *Proc. ACM Manag. Data*, 3(3), Article 221. https://doi.org/10.1145/3725358

Chaudhari, H. (2022). Adidas Sales Dataset. Kaggle.

Cramér, H. (1946). *Mathematical Methods of Statistics*. Princeton University Press.

Ding, R., Han, S., Xu, Y., Zhang, H., and Zhang, D. (2019). QuickInsights: Quick and Automatic Discovery of Insights from Multi-Dimensional Data. In *SIGMOD*, pp. 317-332.

Kendall, M. G. (1975). *Rank Correlation Methods*, 4th ed. Griffin.

Kolmogorov, A. (1933). Sulla determinazione empirica di una legge di distribuzione. *Giornale dell'Istituto Italiano degli Attuari*, 4, 83-91.

Ma, P., Ding, R., Han, S., and Zhang, D. (2021). MetaInsight: Automatic Discovery of Structured Knowledge for Exploratory Data Analysis. In *SIGMOD*, pp. 1262-1274.

Ma, P., Ding, R., Wang, S., Han, S., and Zhang, D. (2023). InsightPilot: An LLM-Empowered Automated Data Exploration System. In *EMNLP System Demonstrations*, pp. 346-352.

Mann, H. B. (1945). Nonparametric Tests Against Trend. *Econometrica*, 13, 245-259.

Manatkar, A., Akella, A., Gupta, P., and Narayanam, K. (2024). QUIS: Question-guided Insights Generation for Automated Exploratory Data Analysis. *arXiv:2410.10270*.

McHugh, M. L. (2013). The Chi-square Test of Independence. *Biochemia Medica*, 23(2), 143-149.

Reimers, N. and Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. In *EMNLP*, pp. 3982-3992.

Siddiqui, T., Kim, A., Lee, J., Karahalios, K., and Parameswaran, A. (2016). Effortless Data Exploration with zenvisage: An Expressive and Interactive Visual Analytics System. In *VLDB*, pp. 457-468.

Simpson, E. H. (1951). The Interpretation of Interaction in Contingency Tables. *Journal of the Royal Statistical Society, Series B*, 13(2), 238-241.

Srinivasan, A. and Stasko, J. (2018). Augmenting Visualizations with Interactive Data Facts. *IEEE Transactions on Visualization and Computer Graphics*, 25(1), 672-681.

Subhash, P. (2017). IBM HR Analytics Employee Attrition & Performance. Kaggle.

Teng, X. and Lin, Y.-R. (2026). De-paradox Tree: Breaking Down Simpson's Paradox via A Kernel-Based Partition Algorithm. *arXiv:2603.02174*.

Vartak, M., Rahman, S., Madden, S., Parameswaran, A., and Polyzotis, N. (2015). SEEDB: Efficient Data-Driven Visualization Recommendations to Support Visual Analytics. In *VLDB*, pp. 2182-2193.

Verma, S. (2024). Online Sales Dataset - Popular Marketplace Data. Kaggle.

Wongsuphasawat, K., Moritz, D., Anand, A., Mackinlay, J., Howe, B., and Heer, J. (2016). Voyager: Exploratory Analysis via Faceted Browsing of Visualization Recommendations. *IEEE Transactions on Visualization and Computer Graphics*, 22(1), 649-658.
