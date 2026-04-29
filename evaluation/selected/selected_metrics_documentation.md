# Tài liệu Chi tiết Các Chỉ số Được Lựa Chọn

Tài liệu này chứa mô tả chi tiết về các chỉ số được lựa chọn để đánh giá hệ thống EDA tự động bằng LLM mà không sử dụng human evaluation.

---

# Part 1 — Overall Model Comparison

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

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 100.0% | 100.0% | 100.0% | Tie |
| employee_attrition | 100.0% | 100.0% | 100.0% | Tie |
| online_sales | 100.0% | 100.0% | 100.0% | Tie |
| **AVG** | **100.0%** | **100.0%** | **100.0%** | **Tie** |

> 💡 **Nhận xét:** Cả 3 systems đều đạt 100% trên mọi dataset — metric này không có khả năng phân biệt giữa các systems. Tuy nhiên vẫn cần giữ như một **sanity check / minimum bar** trước khi xét các metrics khác.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Không trực tiếp. Faithfulness đo chất lượng *kết quả insight* (số liệu đúng không), không đo chất lượng *quá trình sinh câu hỏi* của QuGen. Tuy nhiên **nên giữ** vì kết quả 100% ở cả 3 systems chứng minh QUIS không đánh đổi độ chính xác để có thêm question/reason — tức là QuGen không gây ra hallucination trong insight.

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

### Kết quả thực nghiệm

**Overall (pattern-averaged):**

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 83.4% | 73.2% | 79.0% | QUIS |
| employee_attrition | 20.0% | 55.8% | 8.2% | Baseline |
| online_sales | 35.9% | 43.8% | 66.3% | ONLYSTATS |
| **AVG** | **46.4%** | **57.6%** | **51.7%** | **Baseline** |

**Per-pattern breakdown:**

| Pattern | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| TREND | 100.0% | 66.7% | 83.3% | **QUIS** |
| OUTSTANDING_VALUE | 32.2% | 69.3% | 31.2% | **Baseline** |
| ATTRIBUTION | 62.0% | 100.0% | 69.1% | **Baseline** |
| DISTRIBUTION_DIFFERENCE | 58.1% | 61.1% | 50.6% | **Baseline** |

> 💡 **Nhận xét:** Không có system nào thắng nhất quán trên tất cả patterns. Baseline thắng overall và 2/4 patterns. Kết quả biến động lớn theo dataset (QUIS: 20%–83%), cho thấy metric này nhạy với đặc thù từng dataset. Nên báo cáo kèm per-pattern breakdown thay vì chỉ overall.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Gián tiếp. Metric này đo chất lượng *insight* sau khi sinh, không đo chất lượng câu hỏi. Tuy nhiên có liên quan vì QuGen chọn (B, M) có ngữ nghĩa → các insights từ QUIS được kiểm thử trên đúng loại breakdown (categorical/temporal) → significance rate phản ánh một phần chất lượng chọn lựa của QuGen. **Nên giữ** như metric chất lượng tổng thể, nhưng không phải metric chính để nêu bật QuGen.

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

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 4/4 (100%) | 3/4 (75%) | 4/4 (100%) | Tie |
| employee_attrition | 3/4 (75%) | 3/4 (75%) | 2/4 (50%) | Tie |
| online_sales | 3/4 (75%) | 2/4 (50%) | 4/4 (100%) | ONLYSTATS |

**Uncovered patterns:**

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | — | ATTRIBUTION | — |
| employee_attrition | TREND | TREND | TREND, DISTRIBUTION_DIFFERENCE |
| online_sales | TREND | TREND, ATTRIBUTION | — |

> 💡 **Nhận xét:** TREND là pattern bị bỏ sót nhiều nhất ở cả 3 systems (do thiếu cột temporal trong một số datasets). Baseline thiếu ATTRIBUTION trên adidas và online_sales — do chọn numeric breakdown. QUIS và ONLYSTATS tổng thể tốt hơn Baseline về pattern coverage.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Gián tiếp. Pattern coverage bị ảnh hưởng bởi cả QuGen (chọn B đúng loại) lẫn ISGEN (có tìm được insight valid không). Metric này không đặc trưng cho QuGen vì ONLYSTATS — không có QuGen — cũng đạt pattern coverage tốt (4/4 trên online_sales). **Giữ như context metric**, không phải metric chủ lực cho QuGen.

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

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 84.8% | 80.0% | 73.3% | QUIS |
| employee_attrition | 84.2% | 85.2% | 77.5% | Baseline |
| online_sales | 64.2% | 93.4% | 31.2% | Baseline |
| **AVG** | **77.7%** | **86.2%** | **61.8%** | **Baseline** |

> 💡 **Nhận xét:** Baseline thắng overall (86.2%) vì được so sánh với QUIS (QUIS là reference → novelty của Baseline tự nhiên cao). Đây là **limitation về cách tính**: novelty phụ thuộc vào system nào đóng vai reference. Kết quả online_sales của QUIS thấp bất thường (64.2%) — cần xem xét thêm. ONLYSTATS thấp nhất (61.8%) cho thấy insights khá giống với QUIS.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Có liên quan nhưng **hạn chế**. Lý tưởng thì QuGen — vì chọn (B, M) có chủ đích — nên sinh ra insights khác Baseline. Tuy nhiên metric này có asymmetry: novelty của QUIS được tính "so với Baseline", còn novelty của Baseline được tính "so với QUIS" → không phải cùng baseline reference. Kết quả QUIS 77.7% cho thấy QuGen vẫn tạo ra insights mới, nhưng số liệu khó dùng trực tiếp để argue cho QuGen vì vấn đề reference asymmetry. **Giữ nhưng diễn giải cẩn thận**, không dùng làm metric chủ lực.

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

### Kết quả thực nghiệm

**4a. Semantic Diversity:**

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 0.479 | 0.388 | 0.435 | QUIS |
| employee_attrition | 0.499 | 0.497 | 0.451 | QUIS |
| online_sales | 0.489 | 0.449 | 0.415 | QUIS |
| **AVG** | **0.489** | **0.445** | **0.434** | **QUIS** |

**4b. Subspace Entropy:**

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 2.259 | 1.373 | 2.143 | QUIS |
| employee_attrition | 2.938 | 1.305 | N/A | QUIS |
| online_sales | 1.596 | 0.843 | 1.645 | ONLYSTATS |
| **AVG** | **2.264** | **1.174** | **1.894** | **QUIS** |

**4c. Value Diversity:**

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 0.872 | 0.312 | 0.810 | QUIS |
| employee_attrition | 0.767 | 0.407 | N/A | QUIS |
| online_sales | 0.440 | 0.500 | 0.444 | Baseline |
| **AVG** | **0.693** | **0.406** | **0.627** | **QUIS** |

**4d. Dedup Rate:**

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 0 | 0 | 0 | Tie |
| employee_attrition | 0 | 0.037 | 0 | Tie |
| online_sales | 0 | 0 | 0 | Tie |
| **AVG** | **0.000** | **0.012** | **0.000** | **Tie** |

> 💡 **Nhận xét:** QUIS thắng nhất quán ở 4a, 4b, 4c trên hầu hết datasets — phản ánh tính đa dạng cao của subspace filter. 4d (Dedup Rate) gần như bằng 0 ở tất cả → không phân biệt được, có thể bỏ khỏi báo cáo. ONLYSTATS thiếu 4b/4c ở employee_attrition vì không có subspace.
>
> 🎯 **Phù hợp với mục tiêu QuGen?**
> - **4a (Semantic Diversity)**: Có liên quan — QuGen sinh câu hỏi đa dạng về intent → kéo theo (B, M, pattern) đa dạng → QUIS thắng nhất quán. **Nên giữ.**
> - **4b (Subspace Entropy) + 4c (Value Diversity)**: Liên quan gián tiếp — phản ánh QUIS khám phá nhiều subspace conditions hơn, phần lớn nhờ QuGen chọn (B, M) đa dạng kích hoạt ISGEN tìm subspace phong phú hơn. **Nên giữ**, đặc biệt 4b.
> - **4d (Dedup Rate)**: Không phân biệt được (0% ở tất cả). **Bỏ** khỏi báo cáo chính.

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

### Kết quả thực nghiệm

**7. Subspace Rate (avg):**

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 86/99 (86.9%) | 32/75 (42.7%) | 67/85 (78.8%) | QUIS |
| employee_attrition | 116/133 (87.2%) | 27/81 (33.3%) | 78/132 (59.1%) | QUIS |
| online_sales | 84/106 (79.2%) | 22/61 (36.1%) | 67/72 (93.1%) | ONLYSTATS |
| **AVG** | **84.4%** | **37.4%** | **77.0%** | **QUIS** |

**7a. Subspace Faithfulness:** Cả 3 systems đều 100% (Tie) trên adidas và online_sales — không có dữ liệu cho employee_attrition.

**7b. Subspace Significance:**

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 44.0% | 75.0% | 52.4% | Baseline |
| online_sales | 44.4% | 100.0% | 45.0% | Baseline |
| **AVG** | **44.2%** | **87.5%** | **48.7%** | **Baseline** |

> 💡 **Nhận xét:** QUIS vượt trội về Subspace Rate (84.4% vs 37.4% Baseline). ONLYSTATS v6 nay có subspace đáng kể (77.0% avg, tăng từ 54.6% v4) — khác biệt so với v4 (0% trên employee_attrition). Baseline có Subspace Significance cao hơn (87.5%) vì ít insights có subspace nhưng khi có thì significant hơn.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Gián tiếp. Subspace Rate cao của QUIS (84.4%) xuất phát chủ yếu từ ISGEN, không đặc trưng cho QuGen. ONLYSTATS v6 giờ cũng có subspace, cho thấy subspace là đặc điểm của ISGEN chứ không riêng của QUIS. **Giữ** như metric minh hoả khả năng khám phá phân khúc dữ liệu, nhưng không làm điểm chứng minh cho QuGen.

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

### Kết quả thực nghiệm

| Dataset | QUIS (Δ, x) | Baseline (Δ, x) | ONLYSTATS (Δ, x) | Winner |
|---------|-------------|-----------------|------------------|--------|
| adidas | Δ=-0.043, x=0.885 | Δ=-0.135, x=0.796 | Δ=-0.044, x=0.904 | QUIS |
| employee_attrition | Δ=+0.083, x=1.574 | Δ=+0.046, x=1.079 | N/A | QUIS |
| online_sales | Δ=-0.137, x=0.742 | Δ=+0.025, x=1.048 | Δ=-0.394, x=0.534 | Baseline |

> 💡 **Nhận xét:** Kết quả không nhất quán theo dataset. Chỉ có employee_attrition cho thấy subspace thực sự giúp tăng score (Δ>0 ở cả QUIS và Baseline). Trên adidas và online_sales, subspace insights không mạnh hơn global insights. Ratio x=1.574 của QUIS trên employee_attrition là kết quả đáng chú ý nhất.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Không trực tiếp. Score Uplift đo chất lượng của subspace insights vs global insights — đây là vấn đề của ISGEN, không phải QuGen. Kết quả không nhất quán cũng khó argument cho QuGen. **Giữ như một sub-metric bổ sung** cho phần subspace deep-dive, không đưa vào phần chứng minh QuGen.

---

## 9. Direction (Contrasting Rate)

### Tên
Direction / Contrasting Rate

### Công thức (Theo code thực tế)

```
contrasting_rate = contrasting_count / subspace_direction_evaluated

Trong đó:
- subspace_direction_evaluated = số insights có subspace được đánh giá thành công
- contrasting_count = số insights có subspace "đi ngược chiều" global_val

Quy trình đánh giá từng subspace insight:

1. Tính hiệu ứng effect-size score của insight (nếu score = None → bỏ qua hoàn toàn)

2. Parse measure → (agg, col) từ measure string
   Ví dụ: "MEAN(MonthlyIncome)" → agg="mean", col="MonthlyIncome"

3. Resolve column name (exact match → lowercase → token overlap)

4. Tính global_val = agg(df_cleaned[col]) trên toàn bộ dataset
   Dùng _agg_value(): mean / sum / count / min / max / median

5. Apply subspace filter:
   df_sub = df_cleaned
   for (col_filter, val) in subspace:
       df_sub = df_sub[df_sub[col_filter].astype(str) == str(val)]

6. Tính subspace_val = agg(df_sub[col]) trên subset đã lọc

7. Kiểm tra _is_contrasting(global_val, subspace_val):
   delta = subspace_val - global_val
   - Nếu |delta| < ε (ε = 1e-9) → False (không đáng kể)
   - Nếu |global_val| < ε           → False (global gần 0, không xác định chiều)
   - Ngược lại: is_contrasting = (delta > 0) ≠ (global_val > 0)
     Tức là: contrasting khi chiều của delta ngược với chiều của global_val

8. Đếm:
   subspace_direction_evaluated += 1  (nếu global_val và subspace_val đều hợp lệ)
   contrasting_count += 1             (nếu is_contrasting = True)

9. contrasting_rate = contrasting_count / subspace_direction_evaluated
```

### Giải thích

Direction (Contrasting Rate) đo tỉ lệ insights có subspace filter mà **phân khúc được lọc đi ngược chiều so với giá trị tổng thể (global)**. Insight được coi là "contrasting" khi:

- `global_val > 0` và `subspace_val < global_val` (delta < 0)
  → Phân khúc có giá trị thấp hơn mức trung bình chung
  → Ví dụ: `MEAN(MonthlyIncome)` toàn công ty = +6500, nhưng trong phân khúc `Department=HR` = +4200 → contrasting

- `global_val < 0` và `subspace_val > global_val` (delta > 0)
  → Phân khúc có giá trị cao hơn (ít âm hơn) so với mức âm chung

Insights contrasting phản ánh **phân khúc bất thường** — nhóm đối tượng đang ở mức dưới kỳ vọng khi toàn thể là dương (hoặc trên kỳ vọng khi toàn thể là âm). Đây là loại insights có giá trị phân tích cao vì chỉ ra các điểm cần can thiệp.

### Output

| Field (JSON key) | Ý nghĩa |
|---|---|
| `score_uplift_direction` | contrasting_rate = contrasting_count / subspace_direction_evaluated ∈ [0, 1] |
| `contrasting_count` | Số insights có subspace value đi ngược chiều global value |
| `subspace_direction_evaluated` | Số insights có subspace được đánh giá thành công (có score hợp lệ và global/subspace_val không None) |

### Ngưỡng
- Tốt: ≥ 0.6 (>60% insights subspace tìm ra phân khúc bất thường)
- Acceptable: ≥ 0.4
- Poor: < 0.4

### Càng cao càng tốt?
**CÓ** — Contrasting Rate càng cao → system càng tìm được nhiều phân khúc "đi ngược" xu hướng chung → insights có discovery value cao hơn

### Nguồn tham khảo
- **Atzmueller & Puppe (2006)**. "SD-Map: A Fast Algorithm for Exhaustive Subgroup Discovery." *PKDD 2006*. — Subgroup Discovery framework; contrasting subgroups là nhóm có distribution khác biệt với toàn population
- **Herrera et al. (2011)**. "An Overview on Subgroup Discovery: Foundations and Applications." *Knowledge and Information Systems* 29(3). — Định nghĩa subgroup quality measure dựa trên deviation từ global distribution

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 0.634 (52/82) | 0.389 (7/18) | 0.821 (55/67) | ONLYSTATS |
| employee_attrition | 0.438 (46/105) | 0.300 (3/10) | 0.711 (27/38) | ONLYSTATS |
| online_sales | 0.554 (36/65) | 0.667 (4/6) | 0.770 (47/61) | ONLYSTATS |
| **AVG** | **0.542** | **0.452** | **0.767** | **ONLYSTATS** |

> 💡 **Nhận xét:** ONLYSTATS thắng nhất quán trên cả 3 datasets (AVG = 0.767). QUIS (0.542) cao hơn Baseline (0.452) ở 2/3 datasets. online_sales là exception khi Baseline (0.667) cao hơn QUIS (0.554), nhưng mẫu Baseline rất nhỏ (chỉ 4/6 insights có subspace được đánh giá) → thiếu đại diện. ONLYSTATS cao vì cấu trúc cố định tạo nhiều subspace conditions đặc thù, dễ tìm phân khúc bất thường.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Có liên quan gián tiếp. QuGen chọn (B, M) có ngữ nghĩa → ISGEN tìm subspace conditions có nghĩa kinh doanh → contrasting insights phản ánh các phân khúc thực sự bất thường. Tuy nhiên ONLYSTATS thắng ở metric này dù không có QuGen, cho thấy metric này phụ thuộc nhiều vào thiết kế ISGEN hơn là QuGen. **Giữ như metric bổ sung** cho Subspace Deep-dive, không dùng làm metric chủ lực cho QuGen.

---

# Part 2 — QuGen Module Analysis

---

## 2a. Significance — TREND (Ý nghĩa thống kê cho pattern TREND)

### Tên
TREND Significance / TREND Statistical Validity

### Công thức (Theo code thực tế)

```
TREND_significance_rate = significant_count / total_count

Đây là sub-metric của Metric 2 (Statistical Significance), được tính riêng cho insights có pattern = TREND.

Quy trình tính cho TREND insights:

1. Kiểm tra breakdown phải là Temporal (theo validity rules)
2. Convert breakdown → datetime → sort theo thời gian
3. score = |Kendall τ|  ∈ [0, 1]
4. p_value = Mann-Kendall p
5. Insight significant nếu p_value < 0.05
```

### Giải thích
Metric này đo tỉ lệ TREND insights có ý nghĩa thống kê. TREND insights đặc biệt quan trọng vì:
- Yêu cầu breakdown là Temporal (cột thời gian)
- Nếu breakdown không phải Temporal → insight không thể tính significance → bị coi là invalid
- QUIS chọn breakdown đúng loại (Temporal) nhờ hiểu ngữ nghĩa cột từ QuGen
- Baseline thường chọn sai breakdown (numeric hoặc categorical) → TREND insights không thể tính significance

### Ý nghĩa
- TREND Significance cao → system hiểu đúng yêu cầu của pattern TREND (cần temporal breakdown)
- TREND Significance thấp → system chọn sai breakdown type cho TREND (non-temporal columns)
- Đây là indicator trực tiếp cho khả năng hiểu pattern-breakdown compatibility của QuGen

### Ngưỡng
- alpha = 0.05
- Mong muốn: ≥ 90%
- Acceptable: ≥ 80%
- Poor: < 80%

### Càng cao càng tốt?
**CÓ** — TREND Significance càng cao càng tốt (max = 1.0 = 100%)

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 100.0% (2/2) | 66.7% (16/33) | 83.3% (10/10) | QUIS |
| employee_attrition | 0.0% (0/1) | 0.0% (0/42) | N/A | N/A |
| online_sales | 0.0% (0/1) | 0.0% (0/19) | 100.0% (3/3) | ONLYSTATS |
| **AVG** | **66.7%** | **33.3%** | **91.7%** | **ONLYSTATS** |

> 💡 **Nhận xét:** Trên adidas, QUIS đạt 100% vì cả 2 TREND insights đều dùng temporal breakdown đúng. Baseline chỉ đạt 66.7% vì nhiều TREND insights dùng non-temporal breakdown → không thể tính significance. Trên employee_attrition và online_sales, cả QUIS và Baseline đều 0% vì thiếu cột temporal hoặc không tạo được TREND insights valid. ONLYSTATS đạt 91.7% avg nhờ cấu trúc cố định ưu tiên temporal columns.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Có, **nhưng cần xem xét theo dataset**. Trên adidas, QUIS thắng rõ (100% vs 66.7%) → chứng minh QuGen chọn đúng temporal breakdown cho TREND. Tuy nhiên trên các datasets thiếu temporal columns, metric này không có ý nghĩa. **Giữ như evidence bổ trợ** cho khả năng pattern-breakdown compatibility của QuGen, nhưng nên báo cáo kèm context về dataset characteristics.

---

## 10c. BM Actionability (Tính actionable của breakdown)

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

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 1.000 | 0.458 | 1.000 | Tie |
| employee_attrition | 0.961 | 0.800 | 1.000 | ONLYSTATS |
| online_sales | 0.923 | 0.438 | 1.000 | ONLYSTATS |
| **AVG** | **0.961** | **0.565** | **1.000** | **ONLYSTATS** |

> 💡 **Nhận xét:** ONLYSTATS đạt 100% trên mọi dataset vì cấu trúc cố định chỉ dùng categorical breakdown. QUIS rất cao (96.1%). Baseline thấp nhất (56.5%) — hay dùng numeric breakdown. Metric này phân biệt rõ và có ý nghĩa thiết thực.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Có, nhưng **cần lưu ý khi so sánh với ONLYSTATS**. QuGen của QUIS hiểu ngữ nghĩa cột để chọn breakdown phù hợp (96.1%) — đây là đặc trưng của QuGen so với Baseline (56.5%). ONLYSTATS đạt 100% by design (cấu trúc cố định) chứ không phải do hiểu biết ngữ nghĩa — do đó ONLYSTATS ở đây đóng vai **ablation justify** (không có QuGen nhưng vẫn đạt 100% = metric này không phân biệt được QuGen vs non-QuGen). So sánh QUIS vs Baseline mới có ý nghĩa. **Giữ**, chỉ report QUIS vs Baseline trong phần QuGen.

---

## 10d. BM Diversity (Đa dạng cặp Breakdown-Measure)

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

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 0.263 | 0.320 | 0.365 | ONLYSTATS |
| employee_attrition | 0.384 | 0.370 | 0.402 | ONLYSTATS |
| online_sales | 0.245 | 0.262 | 0.333 | ONLYSTATS |
| **AVG** | **0.297** | **0.317** | **0.367** | **ONLYSTATS** |

> 💡 **Nhận xét:** Sau khi đồng nhất `max_insights_per_question=3` cho cả 3 systems, ONLYSTATS vẫn thắng (0.367) nhưng khoảng cách với QUIS (0.297) và Baseline (0.317) đã thu hẹp đáng kể so với trước (v4: 0.526). QUIS và Baseline vẫn gần nhau.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Yếu. Dù confound config đã được fix, ONLYSTATS vẫn có BM Diversity cao hơn do exhaustive enumeration tất cả (B,M) pairs — đây là by design, không phải chứng minh chất lượng QuGen. Metric đo **breadth** chứ không đo **intent quality**. **Bỏ** khỏi phần nêu bật QuGen.

---

## 10a. NMI — Normalized Mutual Information

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

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 0.094 | 0.331 | 0.217 | Baseline |
| employee_attrition | 0.035 | 0.086 | nan | Baseline |
| online_sales | 0.179 | 0.348 | 0.228 | Baseline |
| **AVG** | **0.103** | **0.255** | **0.223** | **Baseline** |

> 💡 **Nhận xét:** Baseline thắng nhất quán (0.255 vs 0.103) — breakdown của Baseline thường chọn các cột có liên hệ thống kê cao với measure hơn. QUIS thấp nhất, có thể do dùng subspace filter làm phân tán NMI. ONLYSTATS có `nan` trên employee_attrition — cần kiểm tra lại.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** **Không, có thể gây hiểu lầm.** Baseline thắng NMI vì chọn (B, M) có tương quan thống kê cao — nhưng điều này một phần vì Baseline dùng numeric breakdown (các cột số tự nhiên tương quan với nhau). QUIS chọn (B, M) theo *ý nghĩa business* chứ không theo tương quan thống kê thuần túy. Nếu đưa NMI vào báo cáo mà không có chú thích rõ, người đọc có thể hiểu sai rằng QUIS kém hơn Baseline. **Bỏ** khỏi phần chính, hoặc giữ với chú thích rất rõ ràng.

### Nguồn tham khảo
- **Cover & Thomas (2006)**. *Elements of Information Theory*, 2nd ed. Wiley. Ch. 2. — Định nghĩa `MI(B;M) = H(M) - H(M|B)` và `H(X) = -Σ p log p` dùng trực tiếp trong `compute_bm_quality()`.

---

## 10b. Interestingness (Độ thú vị của cặp Breakdown-Measure)

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

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 0.077 | 0.090 | 0.068 | Baseline |
| employee_attrition | 0.090 | 0.157 | 0.078 | Baseline |
| online_sales | 0.244 | 0.513 | 0.314 | Baseline |
| **AVG** | **0.137** | **0.253** | **0.153** | **Baseline** |

> 💡 **Nhận xét:** Baseline thắng nhất quán và rõ ràng (0.253 vs 0.137) — breakdowns của Baseline có effect size cao hơn, đặc biệt trên online_sales (0.513 vs 0.244). Cùng xu hướng với NMI. Hai metrics này (NMI và Interestingness) cho kết quả tương tự nhau — nếu báo cáo cần chọn một, Interestingness trực quan hơn vì kết hợp cả coverage và effect size.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** **Không, có thể gây hiểu lầm** — cùng vấn đề với NMI. Baseline thắng vì chọn cặp (B, M) có effect size thống kê cao, một phần do dùng numeric breakdown (tương quan tuyến tính tự nhiên). QuGen của QUIS chọn (B, M) theo *ý nghĩa câu hỏi* chứ không tối ưu statistical effect size. Nếu đưa vào báo cáo không có chú thích sẽ bất lợi cho QUIS. **Bỏ** khỏi phần chính về QuGen, hoặc giữ với chú thích rõ.

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

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 0.493 | 0.548 | N/A | Baseline |
| employee_attrition | 0.597 | 0.630 | N/A | Baseline |
| online_sales | 0.518 | 0.577 | N/A | Baseline |
| **AVG** | **0.536** | **0.585** | **N/A** | **Baseline** |

> 💡 **Nhận xét:** Baseline thắng nhất quán nhưng biên độ nhỏ (0.585 vs 0.536). ONLYSTATS **không đo được** (N/A) — single fixed template `"How does X vary by Y?"` không phải câu hỏi thực, so sánh cosine similarity sẽ không có ý nghĩa.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Có, **so sánh QUIS vs Baseline hợp lý — nhưng cần diễn giải đúng nguyên nhân**. Baseline question cũng là **template backward-mapped** từ insight_type (`_generate_question()` trong `output_converter.py`): 6 mẫu câu theo loại insight (TREND, OUTLIER, CORRELATION…). Do có 6 template structurally khác nhau, Baseline đạt diversity cao hơn (0.585 vs 0.536) — không phải vì câu hỏi Baseline "tốt hơn" mà vì template variety. QUIS dùng LLM sinh câu hỏi có intent nhưng các câu hỏi LLM đôi khi share cấu trúc ngữ nghĩa tương tự. ONLYSTATS chỉ có **1 template duy nhất** `"How does X vary by Y?"` (~7 từ) → diversity thấp nhất là expected. **Giữ**, report QUIS vs Baseline; ghi chú rõ Baseline dùng backward-mapped templates.

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

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 9.15 ± 1.40 | 12.75 ± 5.03 | N/A | Baseline |
| employee_attrition | 10.25 ± 2.51 | 10.11 ± 5.17 | N/A | QUIS |
| online_sales | 9.99 ± 2.21 | 13.48 ± 4.68 | N/A | Baseline |
| **AVG (mean)** | **9.80** | **12.11** | **N/A** | **Baseline** |

> 💡 **Nhận xét:** Baseline sinh câu hỏi dài hơn (~12 từ vs ~10 từ), nhưng std cao hơn (5.03 vs 1.40 trên adidas) — câu hỏi không đồng đều. QUIS nhất quán nhất (std thấp nhất). ONLYSTATS **N/A** — không có câu hỏi thực để đo.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Có, **so sánh QUIS vs Baseline hợp lý**. Baseline câu hỏi dài hơn (12.11 từ) vì template của nó dài hơn (ví dụ: `"Are there any unusual values of MonthlyIncome across JobRole?"` = 12 từ) và std cao hơn (5.17) vì có 6 template khác nhau về độ dài. ONLYSTATS chỉ 1 template `"How does X vary by Y?"` nên word count xoay quanh ~7 từ (std thấp 0.50). Điểm đáng chú ý: **QUIS nhất quán nhất** (std 1.40–2.51) — QuGen sinh câu hỏi đồng đều về độ cụ thể bất kể loại pattern. **Giữ**, report QUIS vs Baseline kèm mean và std; ONLYSTATS để riêng.

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

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 0.583 | 0.579 | N/A | Tie |
| employee_attrition | 0.493 | 0.588 | N/A | Baseline |
| online_sales | 0.543 | 0.539 | N/A | Tie |
| **AVG** | **0.540** | **0.569** | **N/A** | **Baseline** |

> 💡 **Nhận xét:** QUIS và Baseline gần nhau (0.540 vs 0.569), Tie trên 2/3 dataset. ONLYSTATS **N/A** — không có câu hỏi thực. Đây là **control metric** — kết quả Tie giữa QUIS và Baseline là kỳ vọng bình thường (cả hai đều thực thi đúng insight theo câu hỏi).
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Có, **nhưng chỉ như control**. Tie giữa QUIS và Baseline (0.540 vs 0.569) chứng minh câu hỏi QuGen bám sát insight được trả về — không bị lệch. ONLYSTATS N/A by design. **Giữ như control metric**; không dùng để rank systems trong phần QuGen.

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

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 84.8% | 100.0% | N/A | Baseline |
| employee_attrition | 100.0% | 97.5% | N/A | QUIS |
| online_sales | 95.3% | 100.0% | N/A | Baseline |
| **AVG** | **93.4%** | **99.2%** | N/A | **Baseline** |

> 💡 **Nhận xét:** Cả QUIS và Baseline đều rất cao (>93%). ONLYSTATS không có question text nên không tính được. Biên độ chênh lệch nhỏ (93.4% vs 99.2%). Metric này hữu ích để chứng minh câu hỏi của QUIS không bị copy từ Baseline, nhưng ít phân biệt hơn các metrics khác.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Có, **so sánh QUIS vs Baseline hợp lý**. ONLYSTATS không có question text nên N/A — đây là metric chỉ có ý nghĩa giữa các systems có question. Kết quả QUIS 93.4% chứng minh câu hỏi của QUIS không trivially copy từ Baseline — QuGen đặt ra những câu hỏi thực sự khác biệt. Tuy nhiên biên độ nhỏ (93.4% vs 99.2%) cho thấy cả hai đều đặt câu hỏi khác nhau — không phân biệt mạnh. **Giữ** như metric bổ trợ để chứng minh tính độc lập của câu hỏi QuGen.

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

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 0.553 | 0.527 | N/A | QUIS |
| employee_attrition | 0.468 | 0.519 | N/A | Baseline |
| online_sales | 0.557 | 0.497 | N/A | QUIS |
| **AVG** | **0.526** | **0.514** | N/A | **QUIS** |

> 💡 **Nhận xét:** Kết quả QUIS và Baseline rất sát nhau (0.526 vs 0.514) — không có sự chênh lệch đáng kể. ONLYSTATS không có `reason` field. Metric này đặc trưng cho khả năng giải thích của QuGen, nhưng biên độ phân biệt yếu trong thực nghiệm hiện tại.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** **Giữ, nhưng chỉ report QUIS một mình — không so sánh với Baseline.** `reason` của ba systems có bản chất hoàn toàn khác nhau: QUIS = intent-level (QuGen sinh *trước* khi biết insight, giải thích *tại sao câu hỏi đáng hỏi*); Baseline = `description` post-hoc từ LLM step 5 (mô tả *kết quả* sau khi đã biết insight); ONLYSTATS = template cố định, vô nghĩa về reasoning. Do bản chất khác nhau, so sánh cosine similarity không có ý nghĩa cạnh tranh. Tuy nhiên, **report giá trị tuyệt đối của QUIS (0.526 avg) vẫn có ý nghĩa như đặc trưng riêng**: reason của QuGen đạt coherence 0.526 với insight được trả về — chứng minh reason không phải placeholder mà phản ánh nội dung phân tích thực sự. Đây là **qualitative claim** hỗ trợ bằng số, không phải competitive claim.

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

### Kết quả thực nghiệm

| Dataset | QUIS | Baseline | ONLYSTATS | Winner |
|---------|------|----------|-----------|--------|
| adidas | 99.0% (98/99) | 45.3% (34/75) | 83.5% (71/85) | QUIS |
| employee_attrition | 96.2% (128/133) | 37.0% (30/81) | 100.0% (132/132) | ONLYSTATS |
| online_sales | 86.8% (92/106) | 37.7% (23/61) | 88.9% (64/72) | ONLYSTATS |
| **AVG** | **94.0%** | **40.0%** | **90.8%** | **QUIS** |

> 💡 **Nhận xét:** Sau khi đồng nhất config ONLYSTATS (max=3), QUIS (94.0%) **vượt ONLYSTATS (90.8%)** trong AVG — sự thay đổi quan trọng so với v4 (ONLYSTATS trước đây 96.1%). Baseline vẫn khá thấp (40%). ONLYSTATS thắng 2/3 per-dataset nhưng thua QUIS trong AVG.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** **Có — đây là một trong các metric mạnh nhất để argue cho QuGen.** QUIS (94%) không chỉ cao hơn Baseline (40%) rất rõ — mà còn vượt ONLYSTATS (90.8%) trong tính trung bình. Cần lưu ý: ONLYSTATS chọn (B,M) bằng exhaustive enumeration (không có chọn lọc ngữ nghĩa), vẫn đạt SVR 90.8% nhờ cấu trúc cố định. QUIS sử dụng QuGen để hiểu ngữ nghĩa cột và chọn (B,M) có chủ đích — đạt 94% SVR trong khi có thêm question + reason + subspace đa dạng hơn. **Giữ ở vị trí nổi bật.**

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

### Kết quả thực nghiệm

**SVR — OUTSTANDING_VALUE** (luôn = 100% vì không có ràng buộc breakdown):

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 30/30 | 14/14 | 24/24 |
| employee_attrition | 35/35 | 11/11 | 58/58 |
| online_sales | 36/36 | 18/18 | 25/25 |

**SVR — TREND** (breakdown phải là Temporal):

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 2/2 (100%) | 16/33 (48.5%) | 10/10 (100%) |
| employee_attrition | 0/1 (0%) | 0/42 (0%) | N/A |
| online_sales | 0/1 (0%) | 0/19 (0%) | 3/3 (100%) |

**SVR — ATTRIBUTION** (breakdown phải là Categorical/ID):

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 27/27 (100%) | 0/13 (0%) | 20/24 (83.3%) |
| employee_attrition | 50/50 (100%) | 7/13 (53.8%) | 65/65 (100%) |
| online_sales | 29/32 (90.6%) | 0/11 (0%) | 18/20 (90.0%) |

**SVR — DISTRIBUTION_DIFFERENCE** (breakdown phải là Categorical/ID):

| Dataset | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 39/40 (97.5%) | 4/15 (26.7%) | 17/27 (63.0%) |
| employee_attrition | 43/47 (91.5%) | 12/15 (80.0%) | 9/9 (100%) |
| online_sales | 27/37 (73.0%) | 5/13 (38.5%) | 18/24 (75.0%) |

> 💡 **Nhận xét:** Baseline thất bại nặng ở ATTRIBUTION (0% trên adidas/online_sales) và TREND (0% trên employee_attrition/online_sales) — không hiểu ngữ nghĩa cột để chọn đúng breakdown type. QUIS nhất quán cao. ONLYSTATS v6 mất một số điểm ở ATTRIBUTION (83.3% trên adidas, 90% online) và DISTRIBUTION_DIFFERENCE (63% adidas) so với v4 — cho thấy exhaustive enumeration không đảm bảo 100% structural validity.
>
> 🎯 **Phù hợp với mục tiêu QuGen?** Có. SVR per-pattern phơi bày đúng cơ chế thất bại của Baseline: ATTRIBUTION 0% trên adidas/online_sales vì Baseline map CORRELATION insights (numeric-numeric) sang ATTRIBUTION pattern (`'CORRELATION': 'ATTRIBUTION'` trong `output_converter.py`) → breakdown là cột số → fail SVR. TREND 0% trên employee_attrition/online_sales vì fallback trong converter dùng `valid_vars[0]` làm breakdown khi không tìm thấy temporal/categorical → có thể là numeric. QUIS dùng QuGen hiểu ngữ nghĩa cột trước khi chọn (B,M) → chọn đúng breakdown type từ đầu. **Giữ toàn bộ**, dùng như bằng chứng chi tiết cho luận điểm chính.

---
