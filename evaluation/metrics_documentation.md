# Evaluation Metrics Documentation

This document describes how each evaluation metric is calculated based on the actual code implementation.

Metrics are organized into **3 groups** matching the evaluation pipeline output:

| Group | Metrics |
|---|---|
| **Group 1 — Core & Efficiency** | Faithfulness, Statistical Significance, Insight Novelty, Insight Diversity, Time to Insight, Token Usage |
| **Group 2 — Subspace Deep-dive** | Subspace Metrics (7), Score Uplift from Subspace (8), Direction Uplift (9) |
| **Group 3 — Breakdown\|Measure Deep-dive** | BM Quality — NMI, Interestingness, Actionability, BM Diversity (10) |

---

# Group 1 — Core Metrics & Efficiency

---

## 1. Faithfulness (Độ tin cậy)

### Tên
Faithfulness / Correctness

### Công thức (Theo code thực tế)

```
faithfulness_score = verified_count / total_count

Trong đó:
- verified_count = số insights pass kiểm tra
- total_count = tổng số insights được đánh giá

Quy trình kiểm tra từng insight:
1. Parse measure string để lấy aggregation type và column name
   - Ví dụ: "SUM(Operating Profit)" → agg="sum", col="Operating Profit"
   - Ví dụ: "COUNT(*)" → agg="count", col="*"

2. Kiểm tra subspace filter:
   - Với mỗi (col_filter, val) trong subspace:
     df_filtered = df_filtered[df_filtered[col_filter].astype(str) == str(val)]
   - Nếu df_filtered.empty → fail

3. Recompute values dựa trên aggregation type:
   - Nếu có breakdown:
     * MEAN/AVG: df.groupby(breakdown)[col].mean()
     * SUM: df.groupby(breakdown)[col].sum()
     * COUNT: df.groupby(breakdown).size() (nếu col="*") hoặc df.groupby(breakdown)[col].size()
     * MAX: df.groupby(breakdown)[col].max()
     * MIN: df.groupby(breakdown)[col].min()
   - Nếu không có breakdown:
     * MEAN/AVG: df[col].mean()
     * SUM: df[col].sum()
     * COUNT: len(df)
     * MAX: df[col].max()
     * MIN: df[col].min()

4. So sánh reported values vs recomputed values:
   - Normalize labels: "0" vs "0.0", "7.0" vs "7" → convert về int nếu float == int
   - Convert view_labels và recomputed.index về string
   - Với mỗi label trong view_labels:
     * Tìm label tương ứng trong recomputed.index
     * So sánh: abs(reported - recomputed_val) < epsilon (epsilon = 1e-6)
     * Nếu bất kỳ label nào fail → insight fail

5. Check duplicate labels trong view_labels:
   - Nếu len(view_labels) != len(set(view_labels)) → fail (groupby requires unique labels)
```

### Giải thích
Faithfulness đo lường xem insights có được "grounded" trong dữ liệu thực tế hay không. Code thực hiện bằng cách:
- Áp dụng subspace filter lên cleaned dataframe
- Recompute aggregated values từ dữ liệu thực
- So sánh từng reported value với recomputed value
- Insight được coi là faithful nếu tất cả các reported values match với recomputed values (sai số < 1e-6)

### Ý nghĩa
- Độ tin cậy của insights: insight có bị "hallucinate" không?
- Correctness: insight có đúng với dữ liệu thực tế không?
- Nếu faithfulness thấp → insights có thể chứa thông tin sai lệch, không tin cậy được

### Ngưỡng
- Thường mong muốn: ≥ 95%
- Acceptable: ≥ 90%
- Poor: < 90%

### Càng cao càng tốt?
**CÓ** - Faithfulness càng cao càng tốt (max = 1.0 = 100%)

### Nguồn tham khảo
- **Zhang et al. (2024)**. "A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions." *ACM Computing Surveys*. DOI: 10.1145/3703155

---

## 2. Statistical Significance (Ý nghĩa thống kê)

### Tên
Statistical Significance / Validity

### Công thức (Theo code thực tế)

```
significant_rate = significant_count / total_evaluated
avg_effect_size  = mean(effect_size_i)   cho các insights được đánh giá

Quy trình cho mỗi insight — gọi compute_insight_score() (source of truth):

1. Parse measure string → (agg, col)
   Ví dụ: "SUM(Operating Profit)" → agg="sum", col="Operating Profit"

2. Resolve column names: exact match → lowercase → token overlap

3. Validate EDA correctness từ profile.json:
   - Dùng data_type_class từ profile.json (LLM-generated semantic type)
   - TREND, ATTRIBUTION, DISTRIBUTION_DIFFERENCE yêu cầu breakdown là
     Categorical / Temporal / ID (không phải Numeric)
   - Nếu breakdown là Numeric → score=None, insight bị bỏ qua khỏi evaluation
   - OUTSTANDING_VALUE không yêu cầu vì nó group-by breakdown để tìm outlier

4. Tính effect-size score + p-value theo pattern:

   a. OUTSTANDING_VALUE
      - Aggregate df.groupby(breakdown)[col].<agg>()
      - z = (max − μ) / σ
      - score  = z / (z + 1)          ∈ [0, 1)   ← effect size (outlier strength)
      - p_value = 1 − Φ(z)            Z-test

   b. TREND  (breakdown phải là Temporal)
      - Convert breakdown → datetime → sort theo thời gian
      - score  = |Kendall τ|          ∈ [0, 1]   ← trend strength
      - p_value = Mann-Kendall p

   c. ATTRIBUTION  (breakdown phải là Categorical / ID)
      - Bin col thành 5 bins, crosstab(breakdown, binned_col)
      - score  = Cramér's V           ∈ [0, 1]   ← association strength
      - p_value = Chi-square p  (Fisher exact nếu table 2×2 sparse)

   d. DISTRIBUTION_DIFFERENCE  (breakdown phải là Categorical / ID)
      - Lấy 2 categories đầu tiên
      - score  = KS statistic         ∈ [0, 1]   ← distributional distance
      - p_value = KS p

5. Insight được tính là significant nếu p_value < 0.05
```

### Tại sao dùng effect-size thay vì z-score thuần?

Z-score kiểu `z = stats.norm.ppf(1 - p/2)` tăng theo n → với dataset lớn (n ≈ 9000) mọi p ≈ 0 → z → ∞, không phân biệt được insight mạnh hay yếu. Effect-size độc lập với n, đo **magnitude thực sự** của pattern.

### Giải thích
- `significant_rate`: tỉ lệ insights có p < 0.05 — đo "độ tin cậy thống kê"
- `avg_effect_size`: trung bình effect-size — đo "độ mạnh trung bình của pattern"
- Insights với numeric breakdown bị loại khỏi evaluation (EDA violation), không bị tính là "not significant" — đây là điểm khác biệt quan trọng: không phạt sai chỗ, chỉ không tính

### Ngưỡng
- alpha = 0.05
- Mong muốn: ≥ 80% significant
- Acceptable: ≥ 70%
- Poor: < 70%

### Càng cao càng tốt?
**CÓ** cho cả `significant_rate` và `avg_effect_size`

### Output

```python
{
  'significant_rate': float,      # tỉ lệ insights significant
  'significant_count': int,
  'total_evaluated': int,         # chỉ tính insights EDA-valid
  'avg_effect_size': float,       # mean effect-size của insights được đánh giá
  'max_effect_size': float,
  'by_pattern': {
    'TREND':                  {'significant_count', 'total_count', 'significant_rate', 'insights'},
    'OUTSTANDING_VALUE':      { ... },
    'ATTRIBUTION':            { ... },
    'DISTRIBUTION_DIFFERENCE':{ ... },
  }
}
```

### Nguồn tham khảo
- **Hollander, Wolfe & Chicken (2013)**. *Nonparametric Statistical Methods*, 3rd ed. Wiley. — Basis for Mann-Kendall trend test and KS-test
- **McHugh (2013)**. "The Chi-square Test of Independence." *Biochemia Medica* 23(2): 143–149. DOI: 10.11613/BM.2013.018

---

## 3. Insight Novelty (Tính mới)

### Tên
Insight Novelty / Usefulness

### Công thức (Theo code thực tế)

```
novelty = novel_count / total_count

Trong đó:
- novel_count = số insights với max_similarity < tau (tau = 0.85)
- total_count = tổng số insights của system A

Quy trình tính novelty cho system A so với system B:

1. Convert insights sang string representation:
   - Format: "{breakdown} | {measure} | {pattern} | {condition}"
   - Ví dụ: "Region | SUM(Operating Profit) | TREND | State=Iowa"
   - condition được tạo từ subspace: "k1=v1, k2=v2"

2. Embed insights sử dụng SentenceTransformer:
   - Model: all-MiniLM-L6-v2
   - a_embeddings = model.encode(a_strings)
   - b_embeddings = model.encode(b_strings)

3. Compute pairwise similarities:
   - similarities = cosine_similarity(a_embeddings, b_embeddings)
   - Kết quả: matrix N_A x N_B (N_A = số insights A, N_B = số insights B)

4. Với mỗi insight trong A, tìm max similarity với bất kỳ insight trong B:
   - max_similarities = similarities.max(axis=1)
   - Kết quả: array length N_A, mỗi element là max similarity của insight A với tất cả insights B

5. Đánh giá novelty:
   - novel_count = (max_similarities < tau).sum()
   - Insight là novel nếu max similarity với tất cả insights B < tau (0.85)
   - avg_max_similarity = mean(max_similarities)
```

### Giải thích
Insight Novelty đo lường xem insights của system A có "mới" so với system B không. Code thực hiện bằng cách:
- Convert mỗi insight sang string representation
- Embed strings sử dụng sentence transformer (all-MiniLM-L6-v2)
- Tính cosine similarity giữa mỗi insight A và tất cả insights B
- Insight A được coi là novel nếu nó không giống bất kỳ insight B nào (similarity < 0.85)

### Ý nghĩa
- Usefulness: insights có mang lại thông tin mới không?
- Nếu novelty thấp → insights có thể trùng lặp với baseline, không bổ sung giá trị mới
- Novelty cao → system A phát hiện insights mà baseline không phát hiện được
- Threshold tau = 0.85: nếu similarity < 0.85 → coi là khác nhau đủ để là novel

### Ngưỡng
- tau = 0.85 (similarity threshold)
- Thường mong muốn: ≥ 80% insights novel
- Acceptable: ≥ 70%
- Poor: < 70%

### Càng cao càng tốt?
**CÓ** - Insight Novelty càng cao càng tốt (max = 1.0 = 100%)

### Nguồn tham khảo
- **Reimers & Gurevych (2019)**. "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." *EMNLP 2019*. — Sentence embedding model (all-MiniLM-L6-v2)
- **Merrill et al. (2024)**. "LLM generation novelty through the lens of semantic similarity." *arXiv:2510.27313*

---

## 4. Insight Diversity (Đa dạng)

### Tên
Insight Diversity / Non-redundancy

### Công thức (Theo code thực tế)

`compute_diversity` thực ra gồm **4 sub-metrics** khác nhau:

#### 4a. Semantic Diversity (chính)

```
semantic_diversity = 1 - avg_similarity

Trong đó:
- avg_similarity = total_similarity / (n * (n - 1))
- total_similarity = similarity_matrix.sum() - similarity_matrix.trace()
- n = số insights

Quy trình:

1. Input là danh sách insight dicts. Với mỗi insight:
   - insight_data = ins.get('insight', ins)
   - Lấy: breakdown, measure, pattern, subspace từ insight_data

2. Convert sang string representation:
   - Format: "{breakdown} | {measure} | {pattern} | {condition}"
   - Ví dụ: "Region | SUM(Operating Profit) | Outstanding Value | Sales Method=Online"
   - condition = "k1=v1, k2=v2" từ subspace; rỗng nếu không có subspace

3. Embed strings (all-MiniLM-L6-v2):
   - embeddings = SentenceTransformer.encode(representations)

4. Compute pairwise cosine similarity:
   - similarity_matrix = cosine_similarity(embeddings)  → matrix n×n

5. Average similarity (exclude diagonal):
   - avg_similarity = (sum(matrix) - trace(matrix)) / (n*(n-1))

6. semantic_diversity = 1 - avg_similarity
```

#### 4b. Subspace Diversity (entropy)

```
subspace_diversity_entropy = -Σ (p_c × log(p_c))

Trong đó p_c = số lần column c xuất hiện trong subspace / tổng số subspace columns.
Chỉ tính khi có ít nhất 1 insight có subspace ≠ rỗng.
```

#### 4c. Value Diversity

```
value_diversity = |unique (column, value) pairs| / total_pairs

Đo mức độ khám phá các giá trị khác nhau trong subspace conditions.
Chỉ tính khi có ít nhất 1 insight có subspace ≠ rỗng.
```

#### 4d. Dedup Rate

```
dedup_rate = 1 - (unique_count / total_count)

Unique = distinct by (pattern, breakdown, measure, subspace)
dedup_rate = 0 nghĩa là không có insight nào trùng nhau (tốt).
```

### Ý nghĩa
- Non-redundancy: insights có trùng lặp về chiều phân tích không?
- Semantic diversity thấp → breakdown/measure rất giống nhau
- Subspace diversity cao → system khám phá nhiều columns/values khác nhau làm filter
- Dedup rate thấp (gần 0) → ít insight bị trùng cấu trúc
- Diversity khác novelty:
  * Novelty: so sánh với system khác (A vs B)
  * Diversity: so sánh nội bộ trong cùng một system

### Ngưỡng
- Thường mong muốn: ≥ 0.4
- Acceptable: ≥ 0.3
- Poor: < 0.3

### Càng cao càng tốt?
**CÓ** - Insight Diversity càng cao càng tốt (max = 1.0 = 100%)

### Nguồn tham khảo
- **Reimers & Gurevych (2019)**. "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." *EMNLP 2019*. — Sentence embedding model used in semantic diversity
- **Manning, Raghavan & Schütze (2008)**. *Introduction to Information Retrieval*. Cambridge University Press. Ch. 6. — Cosine similarity in vector space models

---

## 5. Time to Insight (Thời gian tạo insight)

### Tên
Time to Insight / Speed

### Công thức (Theo code thực tế)

```
time_per_insight_seconds = total_time_seconds / insights_generated

Trong đó:
- total_time_seconds = tổng thời gian pipeline chạy (giây)
- insights_generated = số insights được tạo ra

Quy trình tính time to insight cho mỗi system:

1. Load timing data từ timing.json:
   - Format JSON với keys: "baseline" và "ifq"
   - Mỗi key chứa:
     * total_time_seconds: tổng thời gian pipeline
     * insights_generated: số insights được tạo
     * step_times: chi tiết thời gian từng step (optional)

2. Extract system-specific data:
   - Nếu system == "baseline":
     * time_seconds = timing_data["baseline"]["total_time_seconds"]
     * insights_generated = timing_data["baseline"]["insights_generated"]
     * throughput = timing_data["baseline"]["throughput_insights_per_second"]
   - Nếu system == "ifq":
     * time_seconds = timing_data["ifq"]["total_time_seconds"]
     * insights_generated = timing_data["ifq"]["insights_generated"]
     * throughput = insights_generated / time_seconds (nếu không có trong file)

3. Compute time per insight:
   - time_per_insight = time_seconds / insights_generated
   - Nếu insights_generated == 0 → time_per_insight = 0

4. Return metrics:
   - total_time_seconds
   - insights_generated
   - time_per_insight_seconds
   - throughput_insights_per_second
```

### Giải thích
Time to Insight đo lường hiệu quả về mặt thời gian của system. Code thực hiện bằng cách:
- Đọc timing data từ timing.json file (được tạo bởi pipeline)
- Extract total time và insights count cho từng system
- Tính thời gian trung bình để tạo 1 insight
- Tính throughput (insights per second)

### Ý nghĩa
- Speed: system tạo insights nhanh hay chậm?
- Nếu time_per_insight thấp → system nhanh, hiệu quả
- Nếu time_per_insight cao → system chậm, không hiệu quả
- Metric quan trọng cho production deployment:
  * Fast system → có thể chạy thường xuyên, real-time analysis
  * Slow system → chỉ có thể chạy batch, offline analysis

### Ngưỡng
- Thường mong muốn: < 10s per insight
- Acceptable: < 30s per insight
- Poor: ≥ 30s per insight

### Càng cao càng tốt?
**KHÔNG** - Time to Insight càng thấp càng tốt (lower is better)
- Thời gian càng ngắn càng tốt
- Minimize time_per_insight_seconds

---

## 6. Token Usage (Sử dụng token)

### Tên
Token Usage / Cost

### Công thức (Theo code thực tế)

```
tokens_per_insight = total_tokens / insights_generated

Trong đó:
- total_tokens = tổng số tokens (input + output)
- insights_generated = số insights được tạo ra

Quy trình tính token usage cho mỗi system:

1. Load token data từ token.json:
   - Format JSON với keys: "baseline" và "ifq"
   - Mỗi key chứa:
     * input_tokens: số tokens input
     * output_tokens: số tokens output
     * total_tokens: tổng tokens (input + output)
     * requests: số API requests
     * model: tên model LLM

2. Load insights_generated từ timing.json (nếu có):
   - insights_generated = timing_data[system]["insights_generated"]
   - Nếu không có timing.json → dùng hardcoded values:
     * baseline: 133 insights
     * ifq: 80 insights

3. Extract system-specific token data:
   - Nếu system == "baseline":
     * total_tokens = token_data["baseline"]["total_tokens"]
     * input_tokens = token_data["baseline"]["input_tokens"]
     * output_tokens = token_data["baseline"]["output_tokens"]
     * requests = token_data["baseline"]["requests"]
     * model = token_data["baseline"]["model"]
   - Nếu system == "ifq":
     * total_tokens = token_data["ifq"]["total"]["total_tokens"]
     * input_tokens = token_data["ifq"]["total"]["input_tokens"]
     * output_tokens = token_data["ifq"]["total"]["output_tokens"]
     * requests = token_data["ifq"]["total"]["requests"]
     * model = token_data["ifq"]["total"]["model"]

4. Compute tokens per insight:
   - tokens_per_insight = total_tokens / insights_generated
   - Nếu insights_generated == 0 → tokens_per_insight = 0

5. Return metrics:
   - total_tokens
   - input_tokens
   - output_tokens
   - requests
   - insights_generated
   - tokens_per_insight
   - model
```

### Giải thích
Token Usage đo lường hiệu quả về mặt cost của system. Code thực hiện bằng cách:
- Đọc token data từ token.json file (được tạo bởi pipeline)
- Đọc insights_generated từ timing.json (nếu có)
- Extract total tokens cho từng system
- Tính tokens trung bình để tạo 1 insight

### Ý nghĩa
- Cost: system tốn bao nhiêu tokens để tạo insights?
- Nếu tokens_per_insight thấp → system tiết kiệm cost
- Nếu tokens_per_insight cao → system tốn nhiều cost
- Metric quan trọng cho production deployment:
  * Low token usage → cost-effective, có thể scale
  * High token usage → expensive, khó scale
- Token usage thường tỷ lệ thuận với thời gian (nếu dùng LLM)

### Ngưỡng
- Thường mong muốn: < 1000 tokens per insight
- Acceptable: < 2000 tokens per insight
- Poor: ≥ 2000 tokens per insight

### Càng cao càng tốt?
**KHÔNG** - Token Usage càng thấp càng tốt (lower is better)
- Tokens càng ít càng tốt
- Minimize tokens_per_insight

---

# Group 2 — Subspace Deep-dive

---

## 7. Subspace Metrics (Metrics riêng cho insights có subspace filter)

### Tên
Subspace Metrics / Conditional Insight Quality

### Công thức (Theo code thực tế)

```
Subspace Metrics = tập hợp các metrics được tính lại
                   CHỈ trên insights có subspace condition khác rỗng

Quy trình:

1. Lọc insights có subspace:
   - insights_with_subspace = [ins for ins in insights if ins['insight']['subspace']]
   - Chỉ giữ insights có ít nhất 1 (column, value) filter trong subspace

2. Với tập insights đã lọc, tính lại 4 metrics:
   - faithfulness:   như Section 1, nhưng chỉ trên subspace insights
   - significance:   như Section 2, nhưng chỉ trên subspace insights
   - novelty:        như Section 3, system A subspace vs system B subspace
   - diversity:      như Section 4, chỉ trên subspace insights

3. Output thêm:
   - total_with_subspace: số insights có subspace
   - total_original: tổng số insights của system
   - subspace_rate = total_with_subspace / total_original
```

### Giải thích
Subspace Metrics là một bộ metrics phụ để đánh giá **chất lượng riêng của insights có điều kiện lọc** (insights tìm thấy trong một phân khúc dữ liệu cụ thể). Code thực hiện bằng cách:
- Lọc chỉ lấy insights có `subspace` khác rỗng
- Chạy lại Faithfulness, Significance, Novelty, Diversity trên tập con này
- So sánh giữa hai systems chỉ trên tập subspace insights

### Ý nghĩa
- Đánh giá chất lượng của insights phân khúc (conditional insights), tách biệt với insights toàn bộ dữ liệu
- Phát hiện trường hợp một system có faithfulness/significance tốt trên global insights nhưng kém trên subspace insights hoặc ngược lại
- Subspace insights thường khó hơn (cần filter đúng + aggregation đúng + pattern có ý nghĩa)

### Ngưỡng
- Áp dụng ngưỡng tương tự từng metric thành phần (xem Section 1–4)
- `subspace_rate` càng cao → system khám phá nhiều phân khúc dữ liệu hơn

### Càng cao càng tốt?
**Phụ thuộc metric thành phần** — faithfulness, significance, diversity, novelty trong subspace đều higher is better

---

## 8. Score Uplift from Subspace

### Tên
Score Uplift / Subspace Score Uplift

### Công thức (Theo code thực tế)

```
score_i = compute_insight_score(pattern_i, df, breakdown, col, profile_path)
        = effect_size(pattern_i)   ∈ [0, 1]

  OUTSTANDING_VALUE : score = z / (z+1)    z = (max−μ)/σ          ∈ [0, 1)
  TREND             : score = |Kendall τ|  từ Mann-Kendall test    ∈ [0, 1]
  ATTRIBUTION       : score = Cramér's V   từ Chi-square test      ∈ [0, 1]
  DISTRIBUTION_DIFF : score = KS statistic từ KS test              ∈ [0, 1]

Insights với numeric breakdown (EDA violation theo profile.json) → score = None → bị loại

uplift_abs   = mean(score | subspace != []) − mean(score | subspace == [])
uplift_ratio = mean(score | subspace != []) / mean(score | subspace == [])
```

### Tại sao dùng effect-size thay vì (1 − p_value)?
- **`1 − p_value` bão hoà**: với dataset n ≥ 1000, hầu hết p_value ≈ 0 → mọi insight có score = 1.0, không phân biệt được
- **Effect-size độc lập với n**: z/(z+1), Kendall τ, Cramér's V, KS statistic đo **magnitude thực sự** của pattern
- **Cùng hệ quy chiếu**: cả QUIS lẫn Baseline đều được tính bằng cùng `compute_insight_score()`, không phụ thuộc internal score của từng system
- **EDA-correct**: insights dùng numeric breakdown bị loại trước khi tính (sai tinh thần EDA → không nên cho điểm)

Metric đo liệu insights trong phân khúc (subspace) có **effect-size cao hơn** so với insights toàn bộ dữ liệu hay không. `uplift_abs > 0` nghĩa là subspace giúp tìm ra các pattern mạnh hơn.

### Output

| Field | Ý nghĩa |
|---|---|
| `mean_score_with_subspace` | Mean score của insights có subspace filter |
| `mean_score_without_subspace` | Mean score của insights không có subspace filter |
| `score_uplift_abs` | Δ = mean_with − mean_without |
| `score_uplift_ratio` | mean_with / mean_without |
| `num_with_subspace_scored` | Số insights có subspace và có score hợp lệ |
| `num_without_subspace_scored` | Số insights không có subspace và có score hợp lệ |

### Càng cao càng tốt?
**CÓ** — `score_uplift_abs > 0` và `score_uplift_ratio > 1` là tốt (subspace insights được đánh giá cao hơn)

---

## 9. Direction Uplift

### Tên
Direction Uplift / Score Uplift Direction

### Công thức (Theo code thực tế)

```
direction = f(uplift_abs):
  uplift_abs > ε   → "up"    (subspace insights có score cao hơn)
  uplift_abs < -ε  → "down"  (subspace insights có score thấp hơn)
  |uplift_abs| ≤ ε → "flat"  (không có sự khác biệt)

  ε = 1e-9  (floating point tolerance)
```

### Giải thích
Direction Uplift là biểu diễn định tính của `score_uplift_abs` — cho phép so sánh nhanh bằng ranking:
- `up` > `flat` > `down`
- Trong comparison table, system có direction `up` thắng system có `flat` hoặc `down`

### Càng cao càng tốt?
**CÓ** — `up` > `flat` > `down`

---

# Group 3 — Breakdown|Measure Deep-dive

---

## 10. BM Quality (Chất lượng cặp Breakdown-Measure)

### Tên
Breakdown-Measure Quality / BM Quality

### Động lực
Module QUGEN của QUIS sinh ra insight cards có cấu trúc `(question, reason, breakdown, measure)` thông qua vòng lặp đào sâu dữ liệu. BM Quality đo liệu các cặp `(B, M)` được chọn có **actionable, đa dạng, và giải thích được data** hay không — không phụ thuộc vào loại pattern hay nội dung câu hỏi.

Theo Subgroup Discovery literature, một breakdown hợp lệ phải là **descriptor (categorical attribute)**, không phải numeric target. Dùng cột numeric làm B (ví dụ: Operating Profit làm breakdown) cho NMI/Interestingness cao một cách giả tạo vì hai cột numeric tương quan tuyến tính tự nhiên.

### Bốn sub-metrics

#### 8a. BM Actionability
```
Actionability = # pairs có categorical B / # tổng pairs

B là categorical nếu data_type_class trong profile.json
thuộc {"Categorical", "Temporal", "ID"}
```
- Đo liệu system có chọn breakdown **có nghĩa kinh doanh** không (Region, Product, Sales Method)
- Numeric breakdown (Total Sales, Operating Profit) không actionable → penalty
- **QUIS: 100%, Baseline: 42%** (Adidas dataset)

#### 8b. BM Diversity
```
BM Diversity = # unique (B, M) pairs / # tổng insights
```
- Đo breadth: system có khai thác nhiều góc nhìn khác nhau không?
- Giá trị cao → mỗi insight mang thêm chiều phân tích mới
- **QUIS: 0.454, Baseline: 0.247** (QUIS khám phá gấp đôi combinations)

#### 8c. NMI — Normalized Mutual Information
```
NMI(B; M) = MI(B; M) / sqrt(H(B) × H(M))

MI(B; M)  = H(M) - H(M|B)
H(M)      = entropy của M (binning sqrt(n) bins)
H(M|B)    = entropy có điều kiện: Σ P(B=k) × H(M | B=k)
H(B)      = entropy của B (categorical)
```
- Chỉ tính trên **categorical-B pairs**
- Không thiên vị số categories của B (khác η²)
- Bins tự động theo sqrt(n) rule để tránh under/over-smoothing

#### 8d. Interestingness = Coverage × Effect Size
```
Interestingness(B, M) = Coverage(B) × Effect_Size(B, M)

Coverage    = len(non-null rows) / len(df)
Effect_Size = Cohen's d  (nếu B có 2 groups)
            = η²         (nếu B có k > 2 groups)

Cohen's d   = |mean1 - mean2| / pooled_std  → map [0,∞) → [0,1) via d/(d+1)
η²          = SS_between / SS_total
```
- Chỉ tính trên **categorical-B pairs**
- Kết hợp coverage (bao nhiêu data được đại diện) với effect size (B giải thích M tốt đến đâu)

### Phát hiện categorical B
```
Dùng data_type_class từ profile.json (LLM-labeled):
  Categorical, Temporal, ID  → valid breakdown
  Numerical                  → excluded

Fallback khi không có profile.json: string/object dtype
```
`profile.json` được sinh bởi LLM profiling step của baseline:
- Adidas      : `baseline/auto_eda_agent/output_adidas/step1_profiling/profile.json`
- Transactions: `baseline/auto_eda_agent/output_transactions/step1_profiling/profile.json`

### Output

| Field | Ý nghĩa |
|---|---|
| `actionability` | % pairs có categorical B |
| `bm_diversity` | Unique pairs / total insights |
| `nmi_mean` | Mean NMI over categorical-B pairs |
| `int_mean` | Mean Interestingness over categorical-B pairs |
| `total_evaluated` | Unique (B,M) pairs được xử lý |
| `total_categorical` | Pairs có categorical B |
| `total_insights` | Tổng insights đầu vào |
| `pairs` | Per-pair chi tiết: categorical_b, nmi, interestingness |

### Ngưỡng
- **Actionability**: ≥ 0.9 là tốt
- **BM Diversity**: ≥ 0.4 là tốt
- **NMI / Interestingness**: so sánh tương đối giữa các systems

### Càng cao càng tốt?
**CÓ** — Tất cả 4 sub-metrics đều higher is better

### Nguồn tham khảo
- **Cover & Thomas (2006)**. *Elements of Information Theory*, 2nd ed. Wiley. — Mutual Information, Entropy
- **Atzmueller (2015)**. "Subgroup Discovery." *ACM Computing Surveys* 47(1). DOI: 10.1145/2737240 — Interestingness = Coverage × Effect Size; categorical descriptor requirement
- **Fayyad, Piatetsky-Shapiro & Smyth (1996)**. "From Data Mining to Knowledge Discovery in Databases." *AI Magazine* 17(3): 37–54. — EDA descriptor vs. target distinction
- **Cohen (1988)**. *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed. Lawrence Erlbaum. — Cohen's d effect size

---

# Pipeline Reference

---

## 11. Evaluation Pipeline (Tổng quan)

### Luồng chạy evaluation

```
Input:
  --data     CSV dataset (đã preprocessed)
  --path_a   insights_summary.json của system A
  --path_b   insights_summary.json của system B
  --timing_a / --timing_b  timing.json của mỗi system
  --token_a / --token_b    token usage file của mỗi system
  --profile  profile.json từ LLM profiling step (optional, cho BM Quality)
             Adidas      : baseline/auto_eda_agent/output_adidas/step1_profiling/profile.json
             Transactions: baseline/auto_eda_agent/output_transactions/step1_profiling/profile.json

Bước 1: Load & clean data
  - load_and_clean_data(csv_path) → (df_raw, df_cleaned)

Bước 2: Evaluate từng system độc lập
  Với mỗi system:
  - Faithfulness    (df_raw + df_cleaned)
  - Significance    (df_cleaned)
  - Diversity       (question cards)
  - BM Quality      (df_cleaned + profile.json)  [nếu --profile được cung cấp]
  - Time to Insight (timing file)
  - Token Usage     (token file + timing file)

Bước 3: Evaluate comparative metrics
  - Novelty A vs B  (insights_a, insights_b)
  - Novelty B vs A  (insights_b, insights_a)

Bước 4: Compute Subspace Metrics
  - Filter insights có subspace từ cả 2 systems
  - Tính lại Faithfulness, Significance, Novelty, Diversity
    trên tập subspace insights

Bước 5: Output
  - {system_a}_results.json
  - {system_b}_results.json
  - comparison_table.csv
  - comparison_report.md
  - evaluation plots (PNG)
```

### Input format — insights_summary.json

Mỗi entry trong file cần có cấu trúc:
```json
{
  "question": "...",
  "explanation": "...",
  "plot_path": "...",
  "insight": {
    "breakdown": "Region",
    "measure": "SUM(Operating Profit)",
    "subspace": [["Sales Method", "Online"]],
    "pattern": "Outstanding Value",
    "score": 2.34,
    "view_labels": ["Midwest", "Northeast", "Southeast", "South", "West"],
    "view_values": [1234.5, 2345.6, 3456.7, 4567.8, 5678.9]
  }
}
```

### Ghi chú về hai dataframes

- **df_raw**: dataframe gốc, load trực tiếp từ CSV (chỉ detect separator)
- **df_cleaned**: dataframe đã làm sạch currency/percentage strings thành float
- Faithfulness dùng cả hai: thử trên df_cleaned trước, fallback sang df_raw nếu cần
- Significance dùng df_cleaned

