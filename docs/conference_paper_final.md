# Evaluating Question-Guided Exploratory Data Analysis: A Reproducibility Study of QUIS with Automated Metrics

**Thi Bich Ngoc Do, Phu Thinh Nguyen, Hung Nghiep Tran**  
Faculty of Information Systems, University of Information Technology  
ngocdtb.19@grad.uit.edu.vn, thinhnp.19@grad.uit.edu.vn, nghiepth@uit.edu.vn

---

## Abstract

This paper presents a reproducibility study of QUIS, an automated Exploratory Data Analysis (EDA) system. QUIS uses a question generation module, called QUGEN, to create analysis questions before searching for insights. The original QUIS paper used human evaluation, but this is difficult to repeat and also takes much time. In this work, we build an automatic evaluation framework with 7 metrics. We compare our QUIS reproduction with two baselines: a rule-based baseline called ONLYSTATS and an LLM-based agentic baseline that we implemented. We evaluate all three systems across three datasets: Adidas US Sales, IBM Employee Attrition, and Online Sales. The main result is that QUGEN helps avoid column-type errors and improves subspace exploration. We find that the LLM baseline has a structural validity problem: it uses wrong column types in many insights. Across all datasets, QUIS obtains 94.0% average structural validity, while the LLM baseline obtains only 40.0%. QUIS also produces more insights with subspace filters: 84.4% on average, compared with 37.4% for the LLM baseline. These results show that structured question generation is helpful, but we also discuss cases where QUIS does not always get the best score.

---

## 1. Introduction

Exploratory Data Analysis (EDA) is an important step in data analysis. When analysts receive a new dataset, they often need to look for patterns, unusual values, and useful relationships. This process normally requires human knowledge and time. When datasets become larger, it is useful to have systems that can support this work automatically.

QUIS (Manatkar et al., 2024) is one recent system for automated EDA. The main idea of QUIS is simple. Instead of searching for insights directly, the system first generates questions. These questions then guide the insight generation step. In QUIS, the question generation module is called QUGEN, and the insight generation module is called ISGEN.

The original QUIS paper reports good results, but its evaluation is based on human ratings. Human evaluation is useful, but it is also hard to repeat. It is also not convenient when we want to compare many systems or run experiments again after changing the code. Because of this, we focus on automatic metrics that can be computed from the system outputs and the original dataset.

This paper tries to answer two questions:

1. Can we build an automatic evaluation framework for comparing automated EDA systems?
2. What does QUGEN contribute when compared with simpler baselines?

We reproduce QUIS and compare it with two baselines across three datasets: Adidas US Sales, IBM Employee Attrition, and Online Sales. The first baseline is ONLYSTATS, which removes QUGEN and creates cards by simple schema enumeration. The second baseline is an LLM-based agentic EDA pipeline. We use 7 metrics to study correctness, structure, statistical quality, subspace exploration, and question quality.

Our contributions are:

- We build an automatic and reference-free evaluation framework with 7 metrics for AutoEDA systems.
- We compare QUIS, ONLYSTATS, and an LLM agentic baseline across three datasets.
- We identify a systematic problem in LLM-based EDA: column-type mismatches. The LLM baseline gets only 40.0% structural validity on average, while QUIS gets 94.0%.
- We show that QUGEN helps subspace exploration. QUIS gets 84.4% subspace rate on average, compared with 37.4% for the LLM baseline.

---

## 2. Related Work

### 2.1 Evolution of Evaluation Methods in AutoEDA

Early AutoEDA systems used **deviation-based metrics** to measure interestingness. SEEDB (Vartak et al., 2015) evaluates visualizations by computing distribution distance between target and reference data. QuickInsights (Ding et al., 2019) combines impact and significance into a composite score. These metrics enable automatic ranking without human input, but they only measure statistical deviation, not correctness. A system can achieve high deviation scores even when using wrong column types—for example, computing a trend over categorical `Region` instead of temporal `Invoice Date` still produces non-zero deviation.

**Visualization-focused evaluation** shifted to perceptual effectiveness. Voyager (Wongsuphasawat et al., 2016) ranks views using visual channel effectiveness based on perceptual principles. MetaInsight (Ma et al., 2021) evaluates pattern organization by measuring precision in extracting structured knowledge. These methods assess visualization design quality but do not validate schema correctness. They cannot detect if a TREND insight uses a categorical breakdown or if an ATTRIBUTION insight uses a numeric measure instead of categorical grouping.

Recent **LLM-based systems** rely on human evaluation as the primary assessment method. QUIS (Manatkar et al., 2024) uses human raters to score relevance, comprehensibility, and informativeness on a 1-5 scale. InsightPilot (Ma et al., 2023) evaluates completeness through user studies. While human evaluation captures subjective quality, it has critical limitations: expensive (requires expert time), time-consuming (cannot scale to hundreds of insights), subjective (inter-rater variability), and not reproducible (results vary across studies and evaluators).

### 2.2 Research Gap

No prior evaluation method systematically checks **structural validity (SVR)**—whether the breakdown column type matches the pattern requirements. When a system generates a TREND insight, existing metrics cannot verify if it uses a temporal column (correct) or a categorical column (incorrect). When it generates ATTRIBUTION, they cannot check if it uses categorical breakdown (correct) or numeric measure (incorrect). These column-type mismatches are invisible to deviation metrics (only measure distance), visualization metrics (only assess design), and human evaluation (focuses on interestingness, not schema correctness).

**Our work.** We address this gap with automatic, reproducible metrics that validate structural correctness. We introduce Structural Validity Rate (SVR) to check column-type matching, pattern-specific statistical tests (Mann-Kendall for trends, Chi-square for attribution, KS test for distribution differences) to verify significance, and subspace exploration rate to measure depth of analysis. Our evaluation across three systems shows that LLM baselines have systematic structural errors (40% SVR) compared to 94% with structured generation.

---

## 3. System Overview

We compare three systems in this study.

### 3.1 QUIS (Our Reproduction)

QUIS has two main stages. First, QUGEN reads the dataset schema and basic statistics, then creates Insight Cards. Each card contains a question, a reason, a breakdown column, and a measure. Second, ISGEN takes these cards and searches the dataset for actual insights. ISGEN also searches for subspace filters, such as `Region = West`, when the pattern becomes stronger in a subset of the data.

We represent each insight as (B, M, S, P). Here, B is the breakdown column, M is the measure, S is the subspace filter, and P is the pattern type. The four pattern types are TREND, OUTSTANDING_VALUE, ATTRIBUTION, and DISTRIBUTION_DIFFERENCE.

### 3.2 ONLYSTATS (Ablation Baseline)

ONLYSTATS is the ablation baseline. It removes QUGEN and creates Insight Cards directly from the column profile. In our Adidas experiment, it uses every Categorical or Temporal column as a breakdown and pairs it with SUM or MEAN over every Numerical column. This creates 70 unique (B, M) pairs, because there are 7 breakdown columns, 5 numerical columns, and 2 aggregation functions. An example card is "How does SUM(Total Sales) vary by Region?" ONLYSTATS does not call an LLM for card generation and does not rank the cards before sending them to ISGEN.

### 3.3 LLM Agentic Baseline

The second baseline is an LLM-based agentic EDA pipeline that we implemented. It has five steps: column profiling, data quality checking, descriptive statistics, pattern discovery, and insight synthesis. This baseline is more free-form than QUIS. It does not force the model to output a strict Insight Card first. For evaluation, we convert its output into a QUIS-compatible insight format.

---

## 4. Evaluation Framework

### 4.1 Design Principles

Our evaluation framework follows four simple principles. First, the metrics should not require reference answers. They should use only the system output and the original data. Second, different metrics should measure different things. Third, all systems should be evaluated in the same way. Fourth, each metric should help answer a practical question about insight quality.

### 4.2 Selected Metrics

We selected 7 metrics from a larger list of candidates. We group them as follows.

**Group 1: Correctness**

*Faithfulness* checks whether the numbers in an insight can be recomputed from the dataset. For example, if an insight reports a total sales value for one region, we recompute the aggregation from the CSV file. If a system has low faithfulness, then other metrics are less meaningful.

The formula is:

$$\text{Faithfulness} = \frac{|\{i \in I : \text{verified}(i)\}|}{|I|}$$

where $I$ is the set of all insights, and $\text{verified}(i)$ returns true if for all reported values $v_r$ in insight $i$, the recomputed value $v_c$ satisfies $|v_r - v_c| < \epsilon$ with $\epsilon = 10^{-6}$.

**Group 2: Structural Quality**

*Structural Validity Rate (SVR)* checks whether the breakdown column type matches the pattern type. For example, a TREND insight should use a date or time column as the breakdown. An ATTRIBUTION insight should use a categorical breakdown, not a numeric measure column.

The formula is:

$$\text{SVR} = \frac{|\{i \in I : \text{valid\_breakdown}(i)\}|}{|I|}$$

where $\text{valid\_breakdown}(i)$ checks pattern-specific rules: for TREND, the breakdown $B_i$ must be temporal; for ATTRIBUTION and DISTRIBUTION_DIFFERENCE, $B_i$ must be categorical or ID-type; for OUTSTANDING_VALUE, any breakdown type is valid. We report SVR overall and also by pattern type. This also ensures that breakdown-measure pairs are actionable for subgroup analysis.

*Pattern Coverage* counts how many of the four patterns appear at least once with a valid structure. A system that only produces one pattern is not doing broad EDA.

The formula is:

$$\text{Pattern\_Coverage} = \frac{|\{p \in P : \exists i \in I, \text{pattern}(i) = p \land \text{valid}(i)\}|}{|P|}$$

where $P = \{\text{TREND, OUTSTANDING\_VALUE, ATTRIBUTION, DISTRIBUTION\_DIFFERENCE}\}$ is the set of all pattern types, and $\text{valid}(i)$ means the insight has correct structure (passes SVR check).

**Group 3: Statistical and Exploration Quality**

*Statistical Significance* checks the percentage of insights that pass a statistical test at p < 0.05. We use pattern-specific tests: Mann-Kendall for trends (Mann, 1945), z-test for outstanding values, Chi-square test for attribution (McHugh, 2013), and Kolmogorov-Smirnov test for distribution differences (Kolmogorov, 1933). Effect sizes are measured using Kendall's τ for trends (Kendall, 1975), z/(z+1) for outstanding values, Cramér's V for attribution (Cramér, 1946), and KS statistic for distribution differences.

The formula is:

$$\text{Statistical\_Significance} = \frac{|\{i \in I : p\text{-value}(i) < 0.05\}|}{|I|}$$

where $p\text{-value}(i)$ is computed using the pattern-specific test for insight $i$. Only structurally valid insights (SVR = 1) are included in this calculation.

*Subspace Rate* measures how many insights contain at least one subspace filter. A high value means the system does not only give global insights, but also explores conditional cases, such as "within Region = West".

The formula is:

$$\text{Subspace\_Rate} = \frac{|\{i \in I : |S_i| > 0\}|}{|I|}$$

where $S_i$ is the set of subspace filters for insight $i$. Each filter is a (column, value) pair that restricts the data to a subset.

**Group 4: Question and Reasoning Quality**

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

We use three datasets:

1. **Adidas US Sales** (Chaudhari, 2022): 9,648 rows with columns including Retailer, Invoice Date, Region, State, Product, Total Sales, Operating Profit, and Sales Method. This dataset has temporal and categorical columns suitable for all four pattern types.

2. **IBM Employee Attrition** (Subhash, 2017): Employee HR data with attributes such as Age, Monthly Income, Job Satisfaction, and Attrition status. This dataset tests the systems on binary and ordinal variables.

3. **Online Sales** (Verma, 2024): E-commerce transaction data with Product Category, Quantity, Price, Revenue, Region, and Payment Method. This dataset has diverse categorical breakdowns for attribution analysis.

We use OpenAI's `gpt-5.4` through the OpenAI Responses API for QUIS and the LLM Baseline. The original QUIS paper used Llama-3-70B-instruct. We use a hosted OpenAI model because it is easier for our experiment. This may change some exact numbers, but the main comparison is still useful because all systems are evaluated using the same framework.

For ISGEN, we set `beam_width = 20` instead of 100 because the original setting is slower to run. ONLYSTATS does not use an LLM when generating cards. It only uses the LLM in the subspace-search step inside ISGEN, the same as QUIS. For text similarity metrics, we use the `all-MiniLM-L6-v2` model from Sentence-BERT (Reimers and Gurevych, 2019).

---

## 6. Results

### 6.1 Overview

We evaluate all three systems across three datasets with different characteristics:

| Dataset | Rows | Columns | Key Features |
|---------|------|---------|-------------|
| Adidas US Sales | 9,648 | 13 | Temporal (Invoice Date), categorical (Region, Product, Sales Method), numerical measures |
| Employee Attrition | 1,470 | 35 | Binary (Attrition), ordinal (Satisfaction levels), many categorical attributes |
| Online Sales | 240 | 9 | Small dataset, categorical (Product Category, Region, Payment Method), numerical measures |

Table 1 summarizes the average results across all three datasets.

**Table 1: Average Evaluation Results Across Three Datasets**

| Group | Metric | QUIS    | Baseline | ONLYSTATS | Winner |
|-------|--------|---------|----------|-----------|--------|
| Correctness | 1. Faithfulness | **100.0%** | **100.0%** | **100.0%** | Tie |
| Structure | 2. SVR (Overall) | **94.0%** | 40.0% | 90.8% | **QUIS** |
| Coverage | 3. Pattern Coverage | 3/4     | 2.7/4 | 3.3/4 | ONLYSTATS |
| Statistics | 4. Statistical Significance | 46.4%   | **57.6%** | 51.7% | **Baseline** |
| Exploration | 5. Subspace Rate | **84.4%** | 37.4% | 77.0% | **QUIS** |
| Control | 6. Q-I Alignment | 0.540   | **0.569** | N/A | **Baseline** |
| Control | 7. R-I Coherence | **0.526** | 0.514 | N/A | **QUIS** |

### 6.2 Detailed Results by Dataset

**Table 2: Evaluation Results on Adidas US Sales Dataset**  
(QUIS = 99 insights, Baseline = 75 insights, ONLYSTATS = 85 insights)

| Group | Metric | QUIS | Baseline | ONLYSTATS |
|-------|--------|------|----------|-----------|
| Correctness | Faithfulness | **100.0%** | **100.0%** | **100.0%** |
| Structure | SVR (Overall) | **99.0%** (98/99) | 45.3% (34/75) | 83.5% (71/85) |
| Structure | SVR - ATTRIBUTION | **100%** (27/27) | 0% (0/13) | 83.3% (20/24) |
| Structure | SVR - TREND | **100%** (2/2) | 48.5% (16/33) | **100%** (10/10) |
| Coverage | Pattern Coverage | **4/4** | 3/4 | **4/4** |
| Statistics | Statistical Significance | **83.4%** | 73.2% | 76.2% |
| Exploration | Subspace Rate | **86.9%** (86/99) | 42.7% (32/75) | 78.8% (67/85) |
| Control | Q-I Alignment | **0.583** | 0.579 | N/A |
| Control | R-I Coherence | **0.553** | 0.527 | N/A |

**Table 3: Evaluation Results on IBM Employee Attrition Dataset**  
(QUIS = 133 insights, Baseline = 81 insights, ONLYSTATS = 132 insights)

| Group | Metric | QUIS | Baseline | ONLYSTATS |
|-------|--------|------|----------|-----------|
| Correctness | Faithfulness | **100.0%** | **100.0%** | **100.0%** |
| Structure | SVR (Overall) | **100.0%** | 75.3% | 97.7% |
| Coverage | Pattern Coverage | 3/4 (75%) | 3/4 (75%) | 2/4 (50%) |
| Statistics | Statistical Significance | 20.0% | **55.8%** | 8.2% |
| Exploration | Subspace Rate | **87.2%** | 33.3% | 59.1% |
| Control | Q-I Alignment | 0.493 | **0.588** | N/A |
| Control | R-I Coherence | 0.468 | **0.519** | N/A |

**Table 4: Evaluation Results on Online Sales Dataset**  
(QUIS = 106 insights, Baseline = 61 insights, ONLYSTATS = 72 insights)

| Group | Metric | QUIS | Baseline | ONLYSTATS |
|-------|--------|------|----------|-----------|
| Correctness | Faithfulness | **100.0%** | **100.0%** | **100.0%** |
| Structure | SVR (Overall) | **100.0%** | 60.7% | 94.4% |
| Coverage | Pattern Coverage | 3/4 (75%) | 2/4 (50%) | **4/4 (100%)** |
| Statistics | Statistical Significance | 35.9% | 43.8% | **66.3%** |
| Exploration | Subspace Rate | 79.2% | 36.1% | **93.1%** |
| Control | Q-I Alignment | **0.543** | 0.539 | N/A |
| Control | R-I Coherence | **0.557** | 0.497 | N/A |

### 6.3 Cross-Dataset Analysis

#### Faithfulness

All three systems achieve 100% faithfulness across all datasets. This confirms that the numeric values in the insights can be verified from the data. The main differences in other metrics are not caused by wrong arithmetic or hallucinated values. This is important because it shows that QUGEN does not sacrifice correctness for richer question generation.

#### Structural Validity Rate

SVR shows the largest and most consistent difference across datasets. QUIS achieves 94.0% average SVR, while the LLM Baseline achieves only 40.0% (gap of 54 percentage points). ONLYSTATS achieves 90.8%.

The main problem of the LLM Baseline is column-type mismatch. On the Adidas dataset, for ATTRIBUTION, the Baseline gets 0% (0/13). All 13 ATTRIBUTION insights use numerical columns such as `Total Sales` or `Units Sold` as the breakdown instead of categorical columns. For TREND, the Baseline gets 48.5% (16/33) on Adidas. Many trend insights use categorical columns such as `Retailer` or `Region` instead of the date column.

This pattern is consistent across datasets. The Baseline achieves 0% ATTRIBUTION SVR on all three datasets (0/13 on Adidas, 0/13 on Employee Attrition, 0/11 on Online Sales), always using numeric breakdowns like `Units Sold`, `MonthlyIncome`, or `Unit Price`. For TREND, the Baseline uses categorical breakdowns in 51.5% of cases on Adidas and 81.0% on Employee Attrition (e.g., `JobRole`, `Department`), violating the temporal requirement. On Online Sales, Baseline SVR is 60.7%.

QUIS avoids this problem because QUGEN outputs a structured card with explicit breakdown and measure fields. This structure makes the breakdown choice more explicit and schema-aware. The code validates breakdown types programmatically: TREND requires temporal columns, ATTRIBUTION requires categorical columns. ONLYSTATS also has high SVR (90.8% average) because it enumerates only categorical and temporal columns as breakdowns by design, never using numerical columns as breakdowns.

#### Pattern Coverage

Pattern coverage varies by dataset. QUIS covers 3/4 patterns on average, Baseline covers 2.7/4, and ONLYSTATS covers 3.3/4. The most commonly missing pattern is TREND, which requires a temporal breakdown column. Employee Attrition and Online Sales have limited temporal data, so all three systems miss TREND on these datasets.

The Baseline also frequently misses ATTRIBUTION due to the same SVR issue: it uses numerical breakdowns, producing structurally invalid ATTRIBUTION insights.

#### Subspace Exploration

Subspace Rate is where QUIS shows the largest advantage. QUIS achieves 84.4% average subspace rate (range: 79.2%–87.2%), compared with 37.4% for the Baseline (range: 33.3%–42.7%) and 77.0% for ONLYSTATS (range: 59.1%–93.1%).

The comparison with ONLYSTATS is important because both systems use the same ISGEN module. The main difference is the source of the cards. QUIS cards come from QUGEN questions, while ONLYSTATS cards come from schema enumeration templates. QUGEN can generate more conditional questions that already mention specific subgroups or business contexts, giving ISGEN a better starting point for subspace search.

The gap between QUIS and the Baseline is 47.0 percentage points on average (QUIS: 86.9%, 87.2%, 79.2% vs Baseline: 42.7%, 33.3%, 36.1% across the three datasets). The gap between QUIS and ONLYSTATS is smaller (7.4 percentage points on average), confirming that the difference comes from input cards, not the search algorithm. Interestingly, on the Online Sales dataset, ONLYSTATS achieves the highest subspace rate (93.1%). This small dataset has only 240 rows and 9 columns, making exhaustive enumeration very effective.

#### Statistical Significance

Statistical significance varies significantly by dataset. On average, the Baseline achieves 57.6%, ONLYSTATS achieves 51.7%, and QUIS achieves 46.4%.

However, this metric is dataset-dependent. On Adidas, QUIS achieves 83.4%, the highest among all systems. On Employee Attrition, the Baseline achieves 55.8% while QUIS achieves only 20.0%. On Online Sales, ONLYSTATS achieves 66.3%.

This variation does not necessarily mean QUGEN is worse. Employee Attrition contains many binary and categorical variables (e.g., Attrition, Gender, Department), so simple aggregations can easily become statistically significant. QUIS often creates more conditional questions, which may be harder to pass a statistical test when the subspace has fewer rows. Analysis shows that QUIS subspace insights have smaller median sizes (51.5 rows on Employee Attrition, 144 rows on Adidas) compared to Baseline (588 rows, 2448 rows), trading statistical power for more specific insights. The Baseline's invalid insights are also excluded from significance calculations, which can make its score look better on the remaining valid insights.

### 6.4 Control Metrics

Question-Insight Alignment is almost the same for QUIS and the LLM Baseline across datasets. On average, QUIS gets 0.540 and Baseline gets 0.569. This suggests that ISGEN is not simply better for QUIS. Instead, the main difference comes from the input cards created by QUGEN.

Reason-Insight Coherence is also higher for QUIS. QUIS gets 0.553, while Baseline gets 0.527. This means the reason field from QUGEN is slightly more related to the final insight. We do not report these two metrics for ONLYSTATS because its questions and reasons are simple templates.

---

## 7. Discussion

### 7.1 What QUGEN Adds

From the cross-dataset results, QUGEN does not explain everything. It is not the reason for high faithfulness, because all three systems get 100% across all datasets. It is also not the only way to cover all patterns, because ONLYSTATS covers 3.3/4 patterns on average through enumeration.

However, QUGEN is very useful for structural validity. QUIS achieves 94.0% average SVR, while the LLM Baseline achieves only 40.0% (gap of 54 percentage points). ONLYSTATS achieves 90.8%. This shows that schema-aware generation is important. A free-form LLM pipeline can produce text that sounds correct, but still use the wrong column type. The most extreme evidence is Baseline's ATTRIBUTION performance: 0% SVR across all three datasets, systematically selecting numeric columns as breakdown and violating the semantic constraint that ATTRIBUTION requires categorical grouping dimensions.

The most special contribution of QUGEN is subspace exploration. QUIS achieves 84.4% average subspace rate, compared with 37.4% for the Baseline (gap of 47 percentage points) and 77.0% for ONLYSTATS. Since QUIS and ONLYSTATS share the same ISGEN module, the difference mainly comes from the cards. QUGEN's questions provide more useful context for finding subspaces.

### 7.2 Limitations

There are some limitations in this study. First, we use OpenAI's `gpt-5.4` instead of the original Llama-3-70B-instruct, so the exact numbers may be different from the original paper. Second, our embedding-based metrics depend on `all-MiniLM-L6-v2`. This model is useful, but it may not capture all meanings in short technical texts. Third, we evaluate on three datasets with different characteristics, but more datasets would strengthen the generalizability of our findings.

### 7.3 Practical Implications

Our results suggest two practical points for automated EDA systems. First, if an LLM is used to generate analysis specifications, the system should validate the breakdown column type. Without this check, many insights can look reasonable but have the wrong structure. Second, if a system wants to find more subspace insights, it should not only enumerate columns. It should also generate questions with some context or condition.

---

## 8. Conclusion

In this paper, we reproduced QUIS and built an automatic evaluation framework with 7 metrics grounded in established statistical methods. We compared QUIS with ONLYSTATS and an LLM agentic baseline across three datasets.

The results show three main points. First, the LLM Baseline has a serious structural validity problem across all datasets. It gets 45.3%–75.3% SVR, while QUIS gets 99.0%–100.0%. Second, QUGEN helps subspace exploration. QUIS gets 79.2%–87.2% Subspace Rate, compared with 33.3%–42.7% for the LLM Baseline. Third, statistical significance should be interpreted carefully. A system may get a high significance score by finding simple patterns, but this does not always mean it produces better EDA insights.

Overall, our study shows that structured question generation is useful in automated EDA. QUGEN helps the system ask better analysis questions and also reduces schema-related mistakes.

---

## References

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

Subhash, P. (2017). IBM HR Analytics Employee Attrition & Performance. Kaggle.

Vartak, M., Huang, S., Siddiqui, T., Madden, S., and Parameswaran, A. (2015). SEEDB: Efficient Data-Driven Visualization Recommendations to Support Visual Analytics. In *VLDB*, pp. 2182-2193.

Verma, S. (2024). Online Sales Dataset - Popular Marketplace Data. Kaggle.

Wongsuphasawat, K., Moritz, D., Anand, A., Mackinlay, J., Howe, B., and Heer, J. (2016). Voyager: Exploratory Analysis via Faceted Browsing of Visualization Recommendations. *IEEE Transactions on Visualization and Computer Graphics*, 22(1), 649-658.
