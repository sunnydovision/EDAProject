# Evaluation Metrics Documentation

This document describes how each evaluation metric is calculated based on the actual code implementation.

Metrics are organized into **4 groups** matching the evaluation pipeline output (`compare3.py`):

| Group | Metrics |
|---|---|
| **Group 1 — Core & Efficiency** | Faithfulness (1), Statistical Significance (2, 2a), Pattern Coverage (2b), Insight Novelty (3), Insight Diversity (4a–4d), Time to Insight (5), Token Usage (6) |
| **Group 2 — Subspace Deep-dive** | Subspace Rate & Metrics (7, 7a–7b), Score Uplift from Subspace (8), Direction Uplift (9) |
| **Group 3 — Breakdown\|Measure Deep-dive** | BM Quality — NMI (10a), Interestingness (10b), Actionability (10c), BM Diversity (10d) |
| **Group 4 — Intent Layer Quality** | Question Semantic Diversity (11a), Question Specificity (11b), Question–Insight Alignment (11c), Question Novelty (11d), Reason–Insight Coherence (11e), Structural Validity Rate (12, 12a) |

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
- **Mann (1945)**. "Nonparametric Tests Against Trend." *Econometrica* 13(3): 245–259. — Định nghĩa Mann-Kendall S-statistic, dùng trực tiếp qua `pymannkendall.original_test()` trong TREND
- **Kendall (1975)**. *Rank Correlation Methods*, 4th ed. Griffin. — Định nghĩa Kendall τ (tau) dùng làm effect size cho TREND: `score = |τ| ∈ [0, 1]`
- **Kolmogorov (1933)**. "Sulla determinazione empirica di una legge di distribuzione." *Giornale dell'Istituto Italiano degli Attuari* 4: 83–91. — KS statistic dùng làm effect size cho DISTRIBUTION_DIFFERENCE: `score = KS_stat ∈ [0, 1]`
- **McHugh (2013)**. "The Chi-square Test of Independence." *Biochemia Medica* 23(2): 143–149. DOI: 10.11613/BM.2013.018 — Chi-square test dùng cho ATTRIBUTION qua `scipy.stats.chi2_contingency()`
- **Cramér (1946)**. *Mathematical Methods of Statistics*. Princeton University Press. — Cramér's V = √(χ²/(n·(min(r,c)−1))) dùng làm effect size cho ATTRIBUTION

---

## 2b. Pattern Coverage (Độ phủ pattern)

### Tên
Pattern Coverage / Structural Coverage

### Công thức (Theo code thực tế)

```
pattern_coverage = covered_count / total_patterns

Trong đó:
- total_patterns = 4  (TREND, OUTSTANDING_VALUE, ATTRIBUTION, DISTRIBUTION_DIFFERENCE)
- covered_count  = số patterns có ít nhất 1 insight structurally valid

Quy trình tính structural validity cho từng insight:
1. Lấy pattern và breakdown từ insight
2. Load data_type_class từ profile.json:
   - Temporal      → phù hợp TREND
   - Categorical/ID → phù hợp ATTRIBUTION, DISTRIBUTION_DIFFERENCE
   - Bất kỳ        → phù hợp OUTSTANDING_VALUE (không ràng buộc)
3. is_valid = True nếu breakdown type khớp yêu cầu của pattern

Validity rules:
  OUTSTANDING_VALUE     — không ràng buộc breakdown type → luôn valid
  TREND                 — breakdown phải là Temporal
  ATTRIBUTION           — breakdown phải là Categorical hoặc ID
  DISTRIBUTION_DIFFERENCE — breakdown phải là Categorical hoặc ID

Fallback khi không có profile.json:
  Temporal  → thử pd.to_datetime(), valid nếu ≥ 3 bản ghi parse được
  Categorical/ID → dtype là object / string
```

### Sub-metric kèm theo

#### 2b1. Uncovered Patterns
```
uncovered_patterns = [p for p in ALL_PATTERNS if valid_count(p) == 0]
```
Danh sách các pattern không có insight nào structurally valid — giúp chẩn đoán nhanh.

### Output

| Field | Ý nghĩa |
|---|---|
| `pattern_coverage` | covered_count / 4 |
| `covered_count` | Số patterns có ≥1 valid insight |
| `total_patterns` | Luôn = 4 |
| `covered_patterns` | Danh sách patterns đã được phủ |
| `uncovered_patterns` | Danh sách patterns không có insight valid nào |
| `by_pattern[p].valid_count` | Số insights valid cho pattern p |
| `by_pattern[p].total_count` | Tổng insights của pattern p |
| `by_pattern[p].valid_rate` | valid_count / total_count cho pattern p |

### Ý nghĩa
- **Breadth**: system có sử dụng đa dạng các loại pattern EDA không?
- Pattern Coverage = 1.0 (4/4) → system khai thác đủ cả 4 góc nhìn phân tích
- Uncovered patterns thường do QuGen chọn sai breakdown type (numeric thay vì categorical)

### Ngưỡng
- Tốt: 4/4 (100%)
- Acceptable: 3/4 (75%)
- Poor: ≤ 2/4 (50%)

### Càng cao càng tốt?
**CÓ** — Pattern Coverage càng cao càng tốt (max = 1.0 = 4/4)

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
- **Reimers & Gurevych (2019)**. "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." *EMNLP 2019*. — Model `all-MiniLM-L6-v2` dùng để encode insight strings; cosine similarity threshold τ = 0.85 áp dụng trực tiếp trong `compute_novelty()`.

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
- **Reimers & Gurevych (2019)**. "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." *EMNLP 2019*. — Model `all-MiniLM-L6-v2` dùng để encode insight strings; `semantic_diversity = 1 - avg_cosine_similarity` áp dụng trực tiếp trong `compute_diversity()`.

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
   - Format JSON với keys: "baseline" và "quis"
   - Mỗi key chứa:
     * total_time_seconds: tổng thời gian pipeline
     * insights_generated: số insights được tạo
     * step_times: chi tiết thời gian từng step (optional)

2. Extract system-specific data:
   - Nếu system == "baseline":
     * time_seconds = timing_data["baseline"]["total_time_seconds"]
     * insights_generated = timing_data["baseline"]["insights_generated"]
     * throughput = timing_data["baseline"]["throughput_insights_per_second"]
   - Nếu system == "quis":
     * time_seconds = timing_data["quis"]["total_time_seconds"]
     * insights_generated = timing_data["quis"]["insights_generated"]
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

### Nguồn tham khảo

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
   - Format JSON với keys: "baseline" và "quis"
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
     * quis: 80 insights

3. Extract system-specific token data:
   - Nếu system == "baseline":
     * total_tokens = token_data["baseline"]["total_tokens"]
     * input_tokens = token_data["baseline"]["input_tokens"]
     * output_tokens = token_data["baseline"]["output_tokens"]
     * requests = token_data["baseline"]["requests"]
     * model = token_data["baseline"]["model"]
   - Nếu system == "quis":
     * total_tokens = token_data["quis"]["total"]["total_tokens"]
     * input_tokens = token_data["quis"]["total"]["input_tokens"]
     * output_tokens = token_data["quis"]["total"]["output_tokens"]
     * requests = token_data["quis"]["total"]["requests"]
     * model = token_data["quis"]["total"]["model"]

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

### Nguồn tham khảo

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

# Group 3 — Breakdown|Measure Deep-dive (Intent Layer Quality)

---

## 10a. BM Actionability (Tính actionable của breakdown)

### Tên
BM Actionability / Breakdown Categorical Rate

### Công thức (Theo code thực tế)

```
Actionability = total_categorical / total_evaluated

Trong đó:
- total_categorical = # unique (B, M) pairs có B là Categorical/Temporal/ID
- total_evaluated   = # tổng unique (B, M) pairs

B được xác định là categorical nếu data_type_class trong profile.json
thuộc {"Categorical", "Temporal", "ID"}.
Fallback khi không có profile.json: dtype string/object → categorical.
```

### Giải thích
Đo tỉ lệ cặp (Breakdown, Measure) mà breakdown là một cột có nghĩa kinh doanh (categorical, temporal, ID) thay vì cột số. Theo Subgroup Discovery literature, breakdown hợp lệ phải là **descriptor**, không phải numeric target — dùng cột numeric làm breakdown (ví dụ: Operating Profit) cho kết quả giả tạo vì hai cột số tương quan tuyến tính tự nhiên.

### Ý nghĩa
- Actionability cao → system chọn breakdown có nghĩa kinh doanh (Region, Product, Sales Method)
- Actionability thấp → system dùng numeric breakdown (Total Sales, Operating Profit) → insight khó hành động
- Metric này phân biệt rõ QUIS (100%) vs Baseline (42%) trên Adidas dataset

### Output

| Field | Ý nghĩa |
|---|---|
| `actionability` | total_categorical / total_evaluated ∈ [0, 1] |
| `total_categorical` | Số pairs có categorical breakdown |
| `total_evaluated` | Tổng unique (B, M) pairs được xử lý |

### Ngưỡng
- Tốt: ≥ 0.9 (90%)
- Acceptable: ≥ 0.7
- Poor: < 0.7

### Càng cao càng tốt?
**CÓ** — Actionability càng cao càng tốt (max = 1.0)

### Nguồn tham khảo
- **Atzmueller (2015)**. "Subgroup Discovery." *WIREs Data Mining and Knowledge Discovery* 5(1). DOI: 10.1002/widm.1144 — Categorical descriptor requirement
- **Fayyad, Piatetsky-Shapiro & Smyth (1996)**. "From Data Mining to Knowledge Discovery in Databases." *AI Magazine* 17(3): 37–54. — EDA descriptor vs. target distinction

---

## 10b. BM Diversity (Đa dạng cặp Breakdown-Measure)

### Tên
BM Diversity / Breakdown-Measure Combination Breadth

### Công thức (Theo code thực tế)

```
BM Diversity = total_evaluated / total_insights

Trong đó:
- total_evaluated = # unique (B, M) pairs trong tập insights
- total_insights  = tổng số insights đầu vào
```

### Giải thích
Đo mức độ system khai thác nhiều cặp (Breakdown, Measure) khác nhau. Nếu mọi insight đều dùng cùng vài cặp (B, M), BM Diversity thấp dù có nhiều insights. Nếu mỗi insight mang một góc nhìn (B, M) mới, BM Diversity cao.

### Ý nghĩa
- BM Diversity cao → system khám phá nhiều chiều phân tích khác nhau (breadth)
- BM Diversity thấp → insights tập trung vào vài cặp (B, M), thiếu đa dạng góc nhìn
- Giá trị tối đa = 1.0 khi mọi insight có (B, M) duy nhất

### Output

| Field | Ý nghĩa |
|---|---|
| `bm_diversity` | unique (B,M) pairs / total insights ∈ [0, 1] |
| `total_evaluated` | Số unique (B, M) pairs |
| `total_insights` | Tổng insights đầu vào |

### Ngưỡng
- Tốt: ≥ 0.4
- Acceptable: ≥ 0.25
- Poor: < 0.25

### Càng cao càng tốt?
**CÓ** — BM Diversity càng cao càng tốt (max = 1.0)

### Nguồn tham khảo
- **Atzmueller (2015)**. "Subgroup Discovery." *WIREs Data Mining and Knowledge Discovery* 5(1). DOI: 10.1002/widm.1144 — Breadth of subgroup descriptors

---

## 10c. NMI — Normalized Mutual Information

### Tên
NMI / Breakdown-Measure Information Association

### Công thức (Theo code thực tế)

```
NMI(B; M) = MI(B; M) / sqrt(H(B) × H(M))

MI(B; M)  = H(M) - H(M|B)
H(M)      = entropy của M  (binning int(sqrt(n)) bins)
H(M|B)    = Σ_k P(B=k) × H(M | B=k)
H(B)      = entropy của B (categorical)

Chỉ tính trên categorical-B pairs.
nmi_mean = mean(NMI) over all categorical-B pairs.
```

### Giải thích
Đo mức độ breakdown B chứa thông tin về measure M. NMI được chuẩn hoá về [0, 1] nên không thiên vị số categories của B (khác η²). Bins tự động theo sqrt(n) rule để tránh under/over-smoothing khi dataset có kích thước khác nhau.

### Ý nghĩa
- NMI cao → biết B giúp dự đoán M tốt hơn đáng kể (breakdown giải thích được measure)
- NMI thấp → B và M gần như độc lập nhau (breakdown không liên quan tới measure)
- Chỉ tính trên **categorical-B pairs** — numeric breakdown bị loại để tránh tương quan giả tạo

### Output

| Field | Ý nghĩa |
|---|---|
| `nmi_mean` | Mean NMI over categorical-B pairs ∈ [0, 1] |
| `pairs[i].nmi` | NMI của từng (B, M) pair |
| `total_categorical` | Số pairs categorical-B được tính |

### Ngưỡng
- So sánh tương đối giữa các systems
- NMI ≥ 0.3 thường cho thấy mối liên hệ đáng kể

### Càng cao càng tốt?
**CÓ** — NMI càng cao càng tốt

### Nguồn tham khảo
- **Cover & Thomas (2006)**. *Elements of Information Theory*, 2nd ed. Wiley. Ch. 2. — Định nghĩa `MI(B;M) = H(M) - H(M|B)` và `H(X) = -Σ p log p` dùng trực tiếp trong `compute_bm_quality()`.

---

## 10d. Interestingness (Độ thú vị của cặp Breakdown-Measure)

### Tên
BM Interestingness / Coverage × Effect Size

### Công thức (Theo code thực tế)

```
Interestingness(B, M) = Coverage(B) × Effect_Size(B, M)

Coverage(B)    = len(non-null rows of B) / len(df)

Effect_Size(B, M):
  Nếu B có 2 groups  → Cohen's d = |mean1 - mean2| / pooled_std
                        → map [0, ∞) → [0, 1) via d/(d+1)
  Nếu B có k > 2 groups → η² = SS_between / SS_total

Chỉ tính trên categorical-B pairs.
int_mean = mean(Interestingness) over all categorical-B pairs.
```

### Giải thích
Kết hợp hai chiều: **coverage** (breakdown có đại diện đủ data không?) và **effect size** (B giải thích được sự phân tán của M đến đâu?). Metric này xuất phát từ Subgroup Discovery literature (Atzmueller 2015) — một cặp (B, M) tốt phải vừa bao phủ rộng vừa có hiệu ứng mạnh.

### Ý nghĩa
- Interestingness cao → breakdown bao phủ nhiều data VÀ giải thích tốt sự khác biệt trong measure
- Coverage thấp → breakdown chỉ áp dụng cho một phần nhỏ data → ít hữu ích
- Effect size thấp → breakdown không tạo ra sự khác biệt đáng kể trong measure
- Chỉ tính trên **categorical-B pairs**

### Output

| Field | Ý nghĩa |
|---|---|
| `int_mean` | Mean Interestingness over categorical-B pairs ∈ [0, 1] |
| `pairs[i].interestingness` | Interestingness của từng (B, M) pair |
| `total_categorical` | Số pairs categorical-B được tính |

### Ngưỡng
- So sánh tương đối giữa các systems
- Interestingness ≥ 0.3 thường cho thấy cặp (B, M) có giá trị thực tế

### Càng cao càng tốt?
**CÓ** — Interestingness càng cao càng tốt

### Nguồn tham khảo
- **Atzmueller (2015)**. "Subgroup Discovery." *WIREs Data Mining and Knowledge Discovery* 5(1). DOI: 10.1002/widm.1144 — Interestingness = Coverage × Effect Size
- **Cohen (1988)**. *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed. Lawrence Erlbaum. — Cohen's d effect size

---

# Group 4 — Intent Layer Quality (Question & Structural)

---

## 11a. Question Semantic Diversity (Đa dạng câu hỏi)

### Tên
Question Semantic Diversity / Within-system Question Diversity

### Công thức (Theo code thực tế)

```
D_q = 1 - avg_similarity

Trong đó:
- avg_similarity = Σ_{i≠j} cos(q_i, q_j) / (n × (n-1))
- q_i = embedding của câu hỏi thứ i (chỉ dùng question text thuần)
- Embedding model: SentenceTransformer all-MiniLM-L6-v2
```

### Giải thích
Metric đo mức độ đa dạng về ngữ nghĩa trong tập câu hỏi của một system. Khác metric 4a (Insight Semantic Diversity) ở chỗ 4a dùng chuỗi `breakdown|measure|pattern|subspace` còn 11a chỉ dùng *question text* thuần — phơi bày trực tiếp đa dạng intent của QuGen, không bị pha trộn với cấu trúc insight.

### Ý nghĩa
- D_q cao → QuGen sinh ra nhiều câu hỏi khác nhau về ngữ nghĩa, không lặp lại ý tưởng
- D_q thấp → câu hỏi na ná nhau dù có thể có breakdown/measure khác nhau
- D_q = 1.0 → tất cả câu hỏi khác hẳn nhau

### Output

| Field | Ý nghĩa |
|---|---|
| `question_diversity` | Giá trị D_q ∈ [0, 1] |
| `avg_similarity` | Mean pairwise cosine similarity của các câu hỏi |
| `num_questions` | Số câu hỏi được tính |

### Ngưỡng
- Tốt: ≥ 0.5
- Acceptable: ≥ 0.4
- Poor: < 0.4

### Càng cao càng tốt?
**CÓ** — D_q càng cao càng tốt (max = 1.0)

### Nguồn tham khảo
- **Reimers & Gurevych (2019)**. "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." *EMNLP 2019*. — Model `all-MiniLM-L6-v2` dùng để encode question strings; `D_q = 1 - avg_cosine_similarity` áp dụng trực tiếp trong `compute_question_diversity()`.

---

## 11b. Question Specificity (Độ cụ thể câu hỏi)

### Tên
Question Specificity / Question Detail Level

### Công thức (Theo code thực tế)

```
Specificity_mean = mean( len(q_i.split()) )
Specificity_std  = std( len(q_i.split()) )

Trong đó:
- len(q_i.split()) = số tokens (words) trong câu hỏi thứ i
```

### Giải thích
Đo độ dài trung bình (theo số từ) của các câu hỏi. Câu hỏi dài hơn thường chứa nhiều ràng buộc semantic hơn (column, value, time window, scope), chứng tỏ QuGen sinh câu hỏi chuyên biệt thay vì chung chung.

### Ý nghĩa
- `Specificity_mean` cao → câu hỏi cụ thể, đặc thù cho dữ liệu (ví dụ: "What is the trend of Operating Profit in the West region for Online sales?")
- `Specificity_mean` thấp → câu hỏi chung chung (ví dụ: "What is the trend?")
- `Specificity_std` thấp → độ cụ thể đồng đều; `std` cao → có sự phân hoá giữa câu hỏi ngắn và dài

### Output

| Field | Ý nghĩa |
|---|---|
| `question_specificity_mean` | Mean số từ trên mỗi câu hỏi |
| `question_specificity_std` | Std số từ trên mỗi câu hỏi |
| `num_questions` | Số câu hỏi được tính |

### Ngưỡng
- Tốt: mean ≥ 10 từ/câu hỏi
- Acceptable: mean ≥ 7 từ/câu hỏi
- Poor: mean < 7 từ/câu hỏi

### Càng cao càng tốt?
**CÓ** (mean) — câu hỏi càng dài càng cụ thể (lower is better cho std nếu muốn đồng đều)

### Nguồn tham khảo

---

## 11c. Question–Insight Alignment (Độ bám insight)

### Tên
Question–Insight Alignment / Semantic Faithfulness

### Công thức (Theo code thực tế)

```
Align_{Q-I} = mean_i cos( Embed(q_i), Embed(insight_string_i) )

Trong đó:
- insight_string_i = "{breakdown} | {measure} | {pattern} | {subspace_condition}"
- Embedding model: SentenceTransformer all-MiniLM-L6-v2
- Chỉ lấy diagonal của cosine similarity matrix (q_i vs insight_i của cùng card)
```

### Giải thích
Đo mức độ câu hỏi và insight trong cùng một card thực sự bám vào nhau về mặt ngữ nghĩa. Đây là *faithfulness ở tầng ngữ nghĩa* — bổ sung cho metric 1 (Faithfulness) vốn chỉ kiểm tra số liệu, không kiểm tra xem câu hỏi có liên quan tới insight không.

### Ý nghĩa
- Alignment cao → câu hỏi và insight trong cùng card nhất quán về chủ đề
- Alignment thấp → QuGen sinh câu hỏi không khớp với insight được trả về
- Trong so sánh hệ thống: hai hệ thường cho Alignment gần bằng nhau (**control metric**) → Tie là bình thường và kỳ vọng

### Output

| Field | Ý nghĩa |
|---|---|
| `question_insight_alignment` | Mean cosine(Embed(q_i), Embed(insight_string_i)) |
| `question_insight_alignment_std` | Std của alignment scores |
| `num_pairs` | Số cặp (câu hỏi, insight) được đánh giá |

### Ngưỡng
- So sánh tương đối giữa các systems (Tie thường là bình thường)
- Mong muốn: ≥ 0.4

### Càng cao càng tốt?
**CÓ** — tuy nhiên metric này thường dùng như control, Tie giữa các hệ là kết quả kỳ vọng

### Nguồn tham khảo
- **Reimers & Gurevych (2019)**. "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." *EMNLP 2019*. — Model `all-MiniLM-L6-v2` dùng để encode question và insight strings; diagonal cosine similarity áp dụng trực tiếp trong `compute_question_insight_alignment()`.

---

## 11d. Question Novelty (Tính mới của câu hỏi — cross-system)

### Tên
Question Novelty / Cross-system Question Novelty

### Công thức (Theo code thực tế)

```
Q-Novelty(A | B) = novel_count / total_count_A

Trong đó:
- novel_count = # câu hỏi trong A có max_j cos(q_i^A, q_j^B) < tau
- tau = 0.85
- Chỉ so sánh trên question text, không kèm breakdown|measure
- ONLYSTATS không có câu hỏi → trả về None
```

### Giải thích
Đo tỉ lệ câu hỏi của system A mà không có câu hỏi nào trong system B tương tự (cosine similarity < 0.85). Khác metric 3 (Insight Novelty) ở chỗ metric 3 so sánh chuỗi insight đầy đủ (breakdown|measure|pattern|subspace), còn 11d chỉ so sánh *ý tưởng câu hỏi* — tách "góc hỏi" khỏi kết quả phân tích.

### Ý nghĩa
- Q-Novelty cao → QUIS đặt ra những câu hỏi mà baseline không nghĩ đến
- Hai hệ có thể cùng (B, M, pattern) nhưng đặt câu hỏi theo hướng khác → vẫn novel ở góc QuGen
- ONLYSTATS không có `question` field → metric này bị bỏ qua (trả về `None`)

### Output

| Field | Ý nghĩa |
|---|---|
| `question_novelty` | Tỉ lệ câu hỏi novel ∈ [0, 1] |
| `novel_count` | Số câu hỏi novel |
| `total_count` | Tổng câu hỏi của system A |
| `avg_max_similarity` | Mean max cosine sim của từng câu hỏi A với tất cả câu hỏi B |
| `tau` | Ngưỡng similarity (= 0.85) |
| `compared_against` | Tên system B được so sánh |

### Ngưỡng
- Tốt: ≥ 0.5 (50% câu hỏi novel)
- Acceptable: ≥ 0.35
- Poor: < 0.35

### Càng cao càng tốt?
**CÓ** — Q-Novelty càng cao càng tốt (max = 1.0)

### Nguồn tham khảo
- **Reimers & Gurevych (2019)**. "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." *EMNLP 2019*. — Model `all-MiniLM-L6-v2` dùng để encode question strings; cosine similarity threshold τ = 0.85 áp dụng trực tiếp trong `compute_question_novelty()`.

---

## 11e. Reason–Insight Coherence (Độ bám của lý do)

### Tên
Reason–Insight Coherence / Reason Grounding

### Công thức (Theo code thực tế)

```
Coh_{R-I} = mean_i cos( Embed(reason_i), Embed(insight_string_i) )

Trong đó:
- reason_i    = lý do vì sao câu hỏi thứ i đáng hỏi (output của QuGen)
- insight_string_i = "{breakdown} | {measure} | {pattern} | {subspace_condition}"
- Embedding model: SentenceTransformer all-MiniLM-L6-v2
- ONLYSTATS không có reason field → trả về None
```

### Giải thích
`reason` là output đặc trưng của QuGen: giải thích vì sao câu hỏi đó đáng được đặt ra. Metric này đo xem reason có thực sự *bám* vào insight được trả về hay chỉ là text template chung chung. Đây là khía cạnh QuGen hoàn toàn bị bỏ qua bởi các bộ metric truyền thống.

### Ý nghĩa
- Coherence cao → reason không phải template; reason phản ánh đúng insight phát hiện được (ví dụ: "West region shows significantly higher operating profit than other regions")
- Coherence thấp → reason chung chung, không liên quan tới insight cụ thể
- ONLYSTATS không có `reason` field → metric này bị bỏ qua (trả về `None`)

### Output

| Field | Ý nghĩa |
|---|---|
| `reason_insight_coherence` | Mean cosine(Embed(reason_i), Embed(insight_string_i)) |
| `reason_insight_coherence_std` | Std của coherence scores |
| `num_pairs` | Số cặp (reason, insight) được đánh giá |

### Ngưỡng
- Tốt: ≥ 0.4
- Acceptable: ≥ 0.3
- Poor: < 0.3

### Càng cao càng tốt?
**CÓ** — Coherence càng cao càng tốt

### Nguồn tham khảo
- **Reimers & Gurevych (2019)**. "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." *EMNLP 2019*. — Model `all-MiniLM-L6-v2` dùng để encode reason và insight strings; diagonal cosine similarity áp dụng trực tiếp trong `compute_reason_insight_coherence()`.

---

## 12. Structural Validity Rate — SVR (Tỉ lệ hợp lệ cấu trúc)

### Tên
Structural Validity Rate / QuGen Structural Understanding

### Công thức (Theo code thực tế)

```
SVR = valid_count / total_count

Trong đó:
- valid_count = số insights có breakdown type hợp lệ với pattern của nó
- total_count = tổng số insights có cả breakdown và pattern

Validity rules:
  OUTSTANDING_VALUE       — không ràng buộc breakdown type → luôn valid
  TREND                   — breakdown phải là Temporal
  ATTRIBUTION             — breakdown phải là Categorical hoặc ID
  DISTRIBUTION_DIFFERENCE — breakdown phải là Categorical hoặc ID

Nguồn data_type_class: profile.json (LLM-generated semantic type)
Fallback khi không có profile.json: dtype object/string → Categorical; pd.to_datetime() → Temporal
```

### Giải thích
Đo tỉ lệ insights mà breakdown type khớp đúng với yêu cầu của pattern. Một hệ có thể sinh đủ 4 loại pattern (Pattern Coverage = 100%) nhưng nhiều insights dùng sai breakdown type (SVR thấp). SVR đo ở cấp *từng insight*, trong khi Pattern Coverage đo ở cấp *loại pattern*.

### Ý nghĩa
- SVR cao → QuGen hiểu ngữ nghĩa cột dữ liệu, ghép đúng pattern với breakdown phù hợp
- SVR thấp → QuGen chọn breakdown sai loại (ví dụ: dùng numeric column làm breakdown cho TREND)
- Khác biệt so với Pattern Coverage:

| | Pattern Coverage (2b) | Structural Validity Rate (12) |
|---|---|---|
| **Đo gì** | Bao nhiêu *loại pattern* được phủ? | Bao nhiêu *insight* structurally valid? |
| **Đơn vị** | Pattern (4 patterns) | Insight (N insights) |
| **Mục đích** | Breadth — đa dạng pattern | Quality — từng insight đúng cấu trúc chưa |

### Output

| Field | Ý nghĩa |
|---|---|
| `structural_validity_rate` | SVR tổng = valid_count / total_count |
| `valid_count` | Số insights có breakdown type hợp lệ với pattern |
| `invalid_count` | Số insights có breakdown type sai |
| `total_count` | Tổng insights được đánh giá |
| `by_pattern[p].valid_count` | Số insights valid cho pattern p |
| `by_pattern[p].total_count` | Tổng insights của pattern p |
| `by_pattern[p].valid_rate` | valid_count / total_count cho pattern p |

### Ngưỡng
- Tốt: ≥ 0.9 (90%)
- Acceptable: ≥ 0.75 (75%)
- Poor: < 0.75

### Càng cao càng tốt?
**CÓ** — SVR càng cao càng tốt (max = 1.0 = 100%)

### Nguồn tham khảo
- **Atzmueller (2015)**. "Subgroup Discovery." *WIREs Data Mining and Knowledge Discovery* 5(1). DOI: 10.1002/widm.1144 — Categorical descriptor requirement for breakdown

---

## 12a. SVR per Pattern (Tỉ lệ hợp lệ theo từng pattern)

### Tên
SVR per Pattern / Pattern-level Structural Validity

### Công thức (Theo code thực tế)

```
SVR_pattern = valid_count(pattern) / total_count(pattern)

Tính riêng cho mỗi pattern trong:
  TREND, OUTSTANDING_VALUE, ATTRIBUTION, DISTRIBUTION_DIFFERENCE
```

### Giải thích
Phân rã SVR tổng (metric 12) xuống cấp từng pattern, cho phép chẩn đoán chính xác pattern nào đang bị dùng sai breakdown type. Kết quả được báo cáo dưới dạng `valid_count/total_count` trong comparison table.

### Ý nghĩa
- SVR thấp ở TREND → system thường dùng non-Temporal column làm breakdown cho TREND
- SVR thấp ở ATTRIBUTION/DISTRIBUTION_DIFFERENCE → system dùng numeric column thay vì Categorical
- OUTSTANDING_VALUE luôn SVR = 100% vì không có ràng buộc breakdown type

### Output

| Field | Ý nghĩa |
|---|---|
| `by_pattern[p].valid_count` | Số insights valid của pattern p |
| `by_pattern[p].total_count` | Tổng insights của pattern p |
| `by_pattern[p].valid_rate` | valid_count / total_count của pattern p |

### Ngưỡng
- Áp dụng ngưỡng tương tự SVR tổng (metric 12) cho từng pattern
- OUTSTANDING_VALUE kỳ vọng luôn = 1.0

### Càng cao càng tốt?
**CÓ** — Higher is better cho mọi pattern

### Nguồn tham khảo
- **Atzmueller (2015)**. "Subgroup Discovery." *WIREs Data Mining and Knowledge Discovery* 5(1). DOI: 10.1002/widm.1144 — Categorical descriptor requirement for breakdown

---

# Pipeline Reference

---

## Evaluation Pipeline (Tổng quan)

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

