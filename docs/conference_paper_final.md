# Evaluating Question-Guided Exploratory Data Analysis: A Reproducibility Study of QUIS with Automated Metrics

**Thi Bich Ngoc Do, Phu Thinh Nguyen, Hung Nghiep Tran**  
Faculty of Information Systems, University of Information Technology  
ngocdtb.19@grad.uit.edu.vn, thinhnp.19@grad.uit.edu.vn, nghiepth@uit.edu.vn

---

## Abstract

This paper presents a reproducibility study of QUIS, an automated Exploratory Data Analysis (EDA) system. QUIS uses a question generation module, called QUGEN, to create analysis questions before searching for insights. The original QUIS paper used human evaluation, but this is difficult to repeat and also takes much time. In this work, we build an automatic evaluation framework with 8 selected metrics. We compare our QUIS reproduction with two baselines: a rule-based baseline called ONLYSTATS and an LLM-based agentic baseline that we implemented. The main result is that QUGEN is useful for guiding subspace exploration. We also propose a simple metric called Structural Validity Rate (SVR). This metric checks whether an insight uses the correct column type for its pattern. In our Adidas dataset experiment, QUIS obtains 99.0% SVR, while the LLM baseline only obtains 45.3%, and ONLYSTATS obtains 83.5%. QUIS also produces more insights with subspace filters: 86.9%, compared with 78.8% for ONLYSTATS and 42.7% for the LLM baseline. These results show that structured question generation is helpful, but we also discuss cases where QUIS does not always get the best score.

---

## 1. Introduction

Exploratory Data Analysis (EDA) is an important step in data analysis. When analysts receive a new dataset, they often need to look for patterns, unusual values, and useful relationships. This process normally requires human knowledge and time. When datasets become larger, it is useful to have systems that can support this work automatically.

QUIS (Manatkar et al., 2024) is one recent system for automated EDA. The main idea of QUIS is simple. Instead of searching for insights directly, the system first generates questions. These questions then guide the insight generation step. In QUIS, the question generation module is called QUGEN, and the insight generation module is called ISGEN.

The original QUIS paper reports good results, but its evaluation is based on human ratings. Human evaluation is useful, but it is also hard to repeat. It is also not convenient when we want to compare many systems or run experiments again after changing the code. Because of this, we focus on automatic metrics that can be computed from the system outputs and the original dataset.

This paper tries to answer two questions:

1. Can we build an automatic evaluation framework for comparing automated EDA systems?
2. What does QUGEN contribute when compared with simpler baselines?

We reproduce QUIS on the Adidas US Sales dataset, which is one of the datasets used in the original paper. We then compare it with two baselines. The first baseline is ONLYSTATS, which removes QUGEN and creates cards by simple schema enumeration. The second baseline is an LLM-based agentic EDA pipeline. We use 8 metrics to study correctness, structure, statistical quality, subspace exploration, and question quality.

Our contributions are:

- We build an automatic and reference-free evaluation framework for EDA insights.
- We introduce Structural Validity Rate (SVR), a metric for checking wrong column-type usage.
- We compare QUIS, ONLYSTATS, and an LLM agentic baseline in the same setting.
- We give a practical analysis of when QUGEN helps and when it does not clearly win.

---

## 2. Related Work

### 2.1 Automated EDA Systems

Many automated EDA systems try to find interesting patterns from data. Some systems, such as QuickInsights (Ding et al., 2019) and MetaInsight (Ma et al., 2021), use rules to enumerate possible views and then score them. This kind of method is systematic, but it may check many combinations without knowing which questions are meaningful.

Another direction is to use large language models (LLMs). Systems such as InsightPilot (Ma et al., 2023) use LLMs to help decide what analysis to perform. LLMs can produce more natural analysis plans, but they can also make mistakes with schema constraints. For example, an LLM may ask for a trend but use a categorical column instead of a date column.

QUIS (Manatkar et al., 2024) combines both ideas. It uses an LLM to generate questions, but the output is structured as Insight Cards. This structure helps the system connect the question with the correct breakdown and measure columns.

### 2.2 Evaluation of EDA Systems

Evaluating EDA systems is still not easy. Some papers use human ratings, while others use only quantitative scores such as the number of insights. Human ratings are useful, but they are expensive and difficult to reproduce. Pure quantitative scores are easier to compute, but they may miss semantic errors. For example, an insight may have a good score but still use the wrong type of column.

Our work follows the second direction, but we try to include both statistical metrics and simple semantic checks. In particular, SVR checks whether each insight has a valid structure for its pattern.

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

We selected 8 metrics from a larger list of candidates. We group them as follows.

**Group 1: Correctness**

*Faithfulness* checks whether the numbers in an insight can be recomputed from the dataset. For example, if an insight reports a total sales value for one region, we recompute the aggregation from the CSV file. If a system has low faithfulness, then other metrics are less meaningful.

**Group 2: Structural Quality**

*Structural Validity Rate (SVR)* checks whether the breakdown column type matches the pattern type. For example, a TREND insight should use a date or time column as the breakdown. An ATTRIBUTION insight should use a categorical breakdown, not a numeric measure column.

The formula is:

> SVR = number of insights with correct breakdown type / total insights

We report SVR overall and also by pattern type.

*BM Actionability* checks whether the selected breakdown and measure pair is useful for subgroup analysis. If the breakdown is a numeric measure such as `Total Sales`, then the comparison is not very meaningful. In our metric, categorical, temporal, and ID-type breakdowns are considered actionable.

*Pattern Coverage* counts how many of the four patterns appear at least once with a valid structure. A system that only produces one pattern is not doing broad EDA.

**Group 3: Statistical and Exploration Quality**

*Statistical Significance* checks the percentage of insights that pass a statistical test at p < 0.05. We use pattern-specific tests: Mann-Kendall for trends (Mann, 1945), z-test for outstanding values, Chi-square test for attribution, and Kolmogorov-Smirnov test for distribution differences. For attribution, Cramer's V is used as the effect-size score.

*Subspace Rate* measures how many insights contain at least one subspace filter. A high value means the system does not only give global insights, but also explores conditional cases, such as "within Region = West".

**Group 4: Question and Reasoning Quality**

*Question-Insight Alignment* measures how close the question text is to the final insight text. We compute cosine similarity using sentence embeddings. This is used as a control metric. If QUIS and Baseline have similar alignment, then the difference between them is more likely caused by the quality of the generated intent, not by ISGEN answering one system better.

*Reason-Insight Coherence* measures how close the reason field is to the final insight. This metric is only used for QUIS and the LLM Baseline because ONLYSTATS only uses template reasons.

---

## 5. Experimental Setup

We use the Adidas US Sales dataset (Chaudhari, 2022). It has 9,648 rows. The columns are Retailer, Retailer ID, Invoice Date, Region, State, City, Product, Price per Unit, Units Sold, Total Sales, Operating Profit, Operating Margin, and Sales Method. This dataset is suitable for this experiment because it has a date column for TREND and several categorical columns for ATTRIBUTION and DISTRIBUTION_DIFFERENCE.

We use OpenAI's `gpt-5.4` through the OpenAI Responses API for QUIS and the LLM Baseline. The original QUIS paper used Llama-3-70B-instruct. We use a hosted OpenAI model because it is easier for our experiment. This may change some exact numbers, but the main comparison is still useful because all systems are evaluated using the same framework.

For ISGEN, we set `beam_width = 20` instead of 100 because the original setting is slower to run. ONLYSTATS does not use an LLM when generating cards. It only uses the LLM in the subspace-search step inside ISGEN, the same as QUIS. For text similarity metrics, we use the `all-MiniLM-L6-v2` model from Sentence-BERT (Reimers and Gurevych, 2019).

---

## 6. Results

Table 1 shows the main results on the Adidas dataset.

**Table 1: Evaluation Results on Adidas US Sales Dataset**  
(QUIS = 99 insights, Baseline = 75 insights, ONLYSTATS = 85 insights)

| Group | Metric | QUIS | Baseline | ONLYSTATS |
|-------|--------|------|----------|-----------|
| Correctness | Faithfulness | **100.0%** | **100.0%** | **100.0%** |
| Structure | SVR (Overall) | **99.0%** (98/99) | 45.3% (34/75) | 83.5% (71/85) |
| Structure | SVR - ATTRIBUTION | **100%** (27/27) | 0% (0/13) | 83.3% (20/24) |
| Structure | SVR - TREND | **100%** (2/2) | 48.5% (16/33) | **100%** (10/10) |
| Structure | BM Actionability | **1.000** | 0.458 | **1.000** |
| Coverage | Pattern Coverage | **4/4** | 3/4 | **4/4** |
| Statistics | Statistical Significance | **83.4%** | 73.2% | 76.2% |
| Exploration | Subspace Rate | **86.9%** (86/99) | 42.7% (32/75) | 78.8% (67/85) |
| Control | Q-I Alignment | **0.583** | 0.579 | N/A |
| Reasoning | R-I Coherence | **0.553** | 0.527 | N/A |

### 6.1 Faithfulness

All three systems get 100% faithfulness. This means that the numeric values in the insights can be verified from the dataset. This is important because it shows that the main differences in other metrics are not caused by wrong arithmetic or hallucinated values.

### 6.2 Structural Validity Rate

The largest difference is in SVR. QUIS gets 99.0%, while the LLM Baseline only gets 45.3%. This is a large gap of about 54 percentage points.

The main problem of the LLM Baseline is column-type mismatch. For ATTRIBUTION, the Baseline gets 0% (0/13). All 13 ATTRIBUTION insights use columns such as `Total Sales` or `Units Sold` as the breakdown. These columns are numerical measures, not groups. So the insight is not answering the intended question. For example, it is like asking "which region contributes more sales?" but using sales amount itself as the group.

For TREND, the Baseline gets 48.5% (16/33). Some trend insights use the correct date column, but many use categorical columns such as `Retailer` or `Region`. This shows that the LLM can write a trend question in natural language, but it does not always map the question to the correct schema column.

QUIS almost avoids this problem because QUGEN outputs a structured card: reason, question, breakdown, and measure. This structure makes the breakdown choice more explicit. ONLYSTATS also has a high SVR of 83.5%, but it is not perfect. Its TREND insights are all valid because ISGEN only allows TREND on temporal columns. However, ATTRIBUTION and DISTRIBUTION_DIFFERENCE do not have the same strict rule in the pipeline, so some invalid pairs can still pass.

### 6.3 Pattern Coverage and Actionability

QUIS and ONLYSTATS cover all 4 patterns. The LLM Baseline covers only 3 patterns because it has no valid ATTRIBUTION insight. This is the same issue as in SVR. The Baseline produces ATTRIBUTION outputs, but their breakdown columns are not valid.

BM Actionability also supports this result. QUIS and ONLYSTATS both get 1.000, while Baseline gets only 0.458. This means that many Baseline insights use a breakdown that is not good for subgroup comparison.

### 6.4 Subspace Rate

Subspace Rate is where QUIS is clearly better than both baselines. QUIS gets 86.9% (86/99), ONLYSTATS gets 78.8% (67/85), and Baseline gets 42.7% (32/75).

The comparison with ONLYSTATS is important because both systems use the same ISGEN module. The main difference is the source of the cards. QUIS cards come from QUGEN questions, while ONLYSTATS cards come from templates. QUGEN can generate more conditional questions, for example questions that already mention a specific subgroup or business context. This gives ISGEN a better starting point for subspace search.

The difference between QUIS and ONLYSTATS is 8.1 percentage points. The difference between QUIS and the LLM Baseline is 44.2 percentage points. This suggests that QUGEN helps the system find more subspace-based insights.

We also check Score Uplift from subspace search. QUIS has a smaller score drop (Delta = -0.043, ratio = 0.885) than ONLYSTATS (Delta = -0.126, ratio = 0.726) and the LLM Baseline (Delta = -0.135, ratio = 0.796). This means the subspaces found from QUIS cards keep more of the original insight strength.

### 6.5 Cases Where QUIS Does Not Always Win

QUIS performs well on the Adidas dataset, but it does not win every metric on every dataset. For example, on the `employee_attrition` dataset, QUIS gets only 20.0% overall statistical significance, while the LLM Baseline gets 55.8%.

This does not necessarily mean QUGEN is worse. Statistical significance depends on the dataset. Some datasets contain simple categorical or binary variables, so simple aggregations can easily become significant. QUIS often creates more conditional questions. These questions may be more specific, but they can also be harder to pass a statistical test, especially when the subspace has fewer rows.

Also, the Baseline's invalid insights are excluded from some significance calculations because they cannot be tested correctly. This can make the Baseline score look better on the remaining valid insights. Therefore, significance should not be read alone. It should be read together with SVR, pattern coverage, and subspace metrics.

On Adidas, ONLYSTATS gets 76.2% statistical significance, which is below QUIS (83.4%) but above Baseline (73.2%). This is reasonable because ONLYSTATS enumerates many schema combinations. It can find many statistically valid pairs, but it does not create the same kind of conditional questions as QUGEN.

### 6.6 Control Metrics

Question-Insight Alignment is almost the same for QUIS and the LLM Baseline. QUIS gets 0.583 and Baseline gets 0.579. The gap is only 0.004. This suggests that ISGEN is not simply better for QUIS. Instead, the main difference comes from the input cards created by QUGEN.

Reason-Insight Coherence is also higher for QUIS. QUIS gets 0.553, while Baseline gets 0.527. This means the reason field from QUGEN is slightly more related to the final insight. We do not report these two metrics for ONLYSTATS because its questions and reasons are simple templates.

---

## 7. Discussion

### 7.1 What QUGEN Adds

From the results, QUGEN does not explain everything. It is not the reason for high faithfulness, because all three systems get 100%. It is also not the only way to cover all patterns, because ONLYSTATS also covers 4/4 patterns by enumeration.

However, QUGEN is very useful for structural validity. QUIS gets 99.0% SVR, while the LLM Baseline gets only 45.3%. ONLYSTATS is in the middle with 83.5%. This shows that schema-aware generation is important. A free-form LLM pipeline can produce text that sounds correct, but still use the wrong column type.

The most special contribution of QUGEN is subspace exploration. QUIS produces more subspace-filtered insights than both baselines. Since QUIS and ONLYSTATS share the same ISGEN module, the difference mainly comes from the cards. QUGEN's questions provide more useful context for finding subspaces.

### 7.2 Limitations

There are some limitations in this study. First, we report full results mainly for the Adidas dataset. We also ran experiments on `employee_attrition` and `online_sales`, but the detailed discussion in this paper focuses on Adidas. Second, we use OpenAI's `gpt-5.4` instead of the original Llama-3-70B-instruct, so the exact numbers may be different from the original paper. Third, our embedding-based metrics depend on `all-MiniLM-L6-v2`. This model is useful, but it may not capture all meanings in short technical texts.

### 7.3 Practical Implications

Our results suggest two practical points for automated EDA systems. First, if an LLM is used to generate analysis specifications, the system should validate the breakdown column type. Without this check, many insights can look reasonable but have the wrong structure. Second, if a system wants to find more subspace insights, it should not only enumerate columns. It should also generate questions with some context or condition.

---

## 8. Conclusion

In this paper, we reproduced QUIS on the Adidas US Sales dataset and built an automatic evaluation framework with 8 metrics. We compared QUIS with ONLYSTATS and an LLM agentic baseline.

The results show three main points. First, the LLM Baseline has a serious structural validity problem. It gets only 45.3% SVR, while QUIS gets 99.0%. Second, QUGEN helps subspace exploration. QUIS gets 86.9% Subspace Rate, compared with 78.8% for ONLYSTATS and 42.7% for the LLM Baseline. Third, statistical significance should be interpreted carefully. A system may get a high significance score by finding simple patterns, but this does not always mean it produces better EDA insights.

Overall, our study shows that structured question generation is useful in automated EDA. QUGEN helps the system ask better analysis questions and also reduces schema-related mistakes.

---

## References

Chaudhari, H. (2022). Adidas Sales Dataset. Kaggle.

Ding, R., Han, S., Xu, Y., Zhang, H., and Zhang, D. (2019). QuickInsights: Quick and Automatic Discovery of Insights from Multi-Dimensional Data. In *SIGMOD*, pp. 317-332.

Ma, P., Ding, R., Han, S., and Zhang, D. (2021). MetaInsight: Automatic Discovery of Structured Knowledge for Exploratory Data Analysis. In *SIGMOD*, pp. 1262-1274.

Ma, P., Ding, R., Wang, S., Han, S., and Zhang, D. (2023). InsightPilot: An LLM-Empowered Automated Data Exploration System. In *EMNLP System Demonstrations*, pp. 346-352.

Mann, H. B. (1945). Nonparametric Tests Against Trend. *Econometrica*, 13, 245-259.

Manatkar, A., Akella, A., Gupta, P., and Narayanam, K. (2024). QUIS: Question-guided Insights Generation for Automated Exploratory Data Analysis. *arXiv:2410.10270*.

Reimers, N. and Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. In *EMNLP*, pp. 3982-3992.
