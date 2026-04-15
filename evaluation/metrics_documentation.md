# Evaluation Metrics Documentation

This document describes how each evaluation metric is calculated based on the actual code implementation.

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

---

## 2. Statistical Significance (Ý nghĩa thống kê)

### Tên
Statistical Significance / Validity

### Công thức (Theo code thực tế)

```
significant_rate = significant_count / total_evaluated

Trong đó:
- significant_count = số insights với p_value < alpha (alpha = 0.05)
- total_evaluated = tổng số insights có thể tính p-value

Quy trình tính p-value cho từng insight dựa trên pattern:

1. Parse measure string:
   - Ví dụ: "SUM(Operating Profit)" → agg="sum", col="Operating Profit"
   - Ví dụ: "COUNT(*)" → agg="count", col="*"

2. Resolve column names:
   - Tìm column thực tế trong dataframe matching với tên trong insight
   - Thử các phương án: exact match, lowercase match, space underscore conversion, token overlap

3. Compute p-value theo pattern type:

   a. TREND (Linear Regression):
      - Nếu breakdown là datetime/string:
        * Convert breakdown sang timestamp (numeric)
        * y = col (numeric)
      - Nếu col là string:
        * Aggregate: df.groupby(breakdown)[col].count()
        * x = breakdown index (numeric), y = count values
      - Nếu cả 2 đều numeric:
        * x = breakdown, y = col
      - Chạy linear regression: stats.linregress(x, y)
      - Return: p_value từ regression

   b. OUTSTANDING_VALUE (Z-test):
      - Nếu có breakdown:
        * Aggregate: df.groupby(breakdown)[col].count()
        * values = grouped.values
      - Nếu không có breakdown:
        * values = df[col] (numeric, dropna)
      - Tính: mean_val = values.mean(), std_val = values.std()
      - Tính: extreme_val = values.max()
      - Tính: z_score = (extreme_val - mean_val) / std_val
      - Return: p_value = 1 - stats.norm.cdf(z_score)

   c. ATTRIBUTION (Chi-square test):
      - Nếu col là string/object:
        * contingency_table = pd.crosstab(df[breakdown], df[col])
      - Nếu col là numeric:
        * Binning col thành 5 bins (hoặc 3 bins nếu fail): pd.cut(col_numeric, bins=5)
        * contingency_table = pd.crosstab(df[breakdown], binned_col)
      - Chạy chi-square test: chi2_contingency(contingency_table)
      - Nếu > 20% cells có expected < 5 và table là 2x2:
        * Dùng Fisher's exact test thay thế
      - Return: p_value từ test

   d. DISTRIBUTION_DIFFERENCE (KS-test):
      - Lấy 2 categories đầu tiên từ breakdown
      - cat1_data = df[df[breakdown] == cat1][col] (numeric, dropna)
      - cat2_data = df[df[breakdown] == cat2][col] (numeric, dropna)
      - Chạy KS test: ks_2samp(cat1_data, cat2_data)
      - Return: p_value từ test

4. Convert p-values sang z-scores cho reporting:
   - z = stats.norm.ppf(1 - p/2)
   - avg_zscore = mean(|z| cho tất cả p-values)

5. Đánh giá significance:
   - Nếu p_value < alpha (0.05) → insight là significant
```

### Giải thích
Statistical Significance đo lường xem insights có phải là "signal" thực sự hay chỉ là "noise" ngẫu nhiên. Code thực hiện bằng cách:
- Tính p-value cho mỗi insight dựa trên pattern type
- Dùng các statistical test phù hợp với từng pattern
- Insight được coi là significant nếu p-value < 0.05 (5% significance level)

### Ý nghĩa
- Validity: insight có ý nghĩa thống kê không hay chỉ là ngẫu nhiên?
- Nếu significance thấp → insights có thể là noise, không đáng tin cậy
- Các pattern khác nhau dùng test khác nhau:
  * Trend: Linear regression (có xu hướng tăng/giảm không?)
  * Outstanding Value: Z-test (giá trị cực đại có bất thường không?)
  * Attribution: Chi-square test (có mối quan hệ giữa 2 biến không?)
  * Distribution Difference: KS-test (phân phối có khác nhau không?)

### Ngưỡng
- alpha = 0.05 (5% significance level)
- Thường mong muốn: ≥ 80% insights significant
- Acceptable: ≥ 70%
- Poor: < 70%

### Càng cao càng tốt?
**CÓ** - Statistical Significance càng cao càng tốt (max = 1.0 = 100%)

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

---

## 4. Insight Diversity (Đa dạng)

### Tên
Insight Diversity / Non-redundancy

### Công thức (Theo code thực tế)

```
diversity = 1 - avg_similarity

Trong đó:
- avg_similarity = total_similarity / (n * (n - 1))
- total_similarity = similarity_matrix.sum() - similarity_matrix.trace()
- n = số insights

Quy trình tính diversity cho một system:

1. Convert insights sang string representation:
   - Format: "{breakdown} | {measure} | {pattern} | {condition}"
   - Ví dụ: "Region | SUM(Operating Profit) | TREND | State=Iowa"
   - condition được tạo từ subspace: "k1=v1, k2=v2"

2. Embed insights sử dụng SentenceTransformer:
   - Model: all-MiniLM-L6-v2
   - embeddings = model.encode(representations)

3. Compute pairwise cosine similarity:
   - similarity_matrix = cosine_similarity(embeddings)
   - Kết quả: matrix n x n (n = số insights)
   - similarity_matrix[i][j] = cosine similarity giữa insight i và insight j

4. Calculate average similarity (excluding diagonal):
   - total_similarity = sum(similarity_matrix) - sum(diagonal)
   - avg_similarity = total_similarity / (n * (n - 1))
   - Diagonal = similarity của insight với chính nó = 1.0, nên bị loại bỏ

5. Calculate diversity:
   - diversity = 1 - avg_similarity
```

### Giải thích
Insight Diversity đo lường xem insights có "đa dạng" hay không (non-redundancy). Code thực hiện bằng cách:
- Convert mỗi insight sang string representation
- Embed strings sử dụng sentence transformer (all-MiniLM-L6-v2)
- Tính cosine similarity giữa tất cả cặp insights
- Tính average similarity (excluding self-similarity)
- Diversity = 1 - average similarity

### Ý nghĩa
- Non-redundancy: insights có trùng lặp không?
- Nếu diversity thấp → insights rất giống nhau, không đa dạng
- Diversity cao → insights đa dạng, không trùng lặp, bao phủ nhiều khía cạnh khác nhau
- Diversity khác novelty:
  * Novelty: so sánh với system khác (system A vs system B)
  * Diversity: so sánh nội bộ trong cùng một system (insight A vs insight B trong cùng system)

### Ngưỡng
- Thường mong muốn: ≥ 0.4
- Acceptable: ≥ 0.3
- Poor: < 0.3

### Càng cao càng tốt?
**CÓ** - Insight Diversity càng cao càng tốt (max = 1.0 = 100%)

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

## Nguồn tham khảo (References)

### 1. Faithfulness
- **Zhang et al. (2024)**. "A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions." ACM Computing Surveys. DOI: 10.1145/3703155
  - Survey về các phương pháp detection hallucination và metrics cho faithfulness evaluation
  - Link: https://dl.acm.org/doi/10.1145/3703155

### 2. Statistical Significance
- **Mann (1945)**. "Nonparametric Tests Against Trend." Econometrica.
  - Foundational work on nonparametric statistical tests, basis for Mann-Kendall trend test
- **Kendall (1938)**. "A New Measure of Rank Correlation." Biometrika.
  - Foundational work on rank correlation, basis for Kendall's tau
- **StatPearls (2023)**. "Statistical Significance." NCBI Bookshelf.
  - Giải thích khái niệm statistical significance và p-value trong hypothesis testing
  - Link: https://www.ncbi.nlm.nih.gov/books/NBK45

### 3. Insight Novelty
- **Merrill et al. (2024)**. "LLM generation novelty through the lens of semantic similarity." arXiv:2510.27313
  - Framework cho novelty detection sử dụng semantic similarity và embeddings
  - Link: https://arxiv.org/abs/2510.27313

### 4. Insight Diversity
- **Cosine Similarity** - Widely used metric in text mining and NLP (foundational concept)
  - Standard metric cho measuring similarity trong high-dimensional spaces
- **Reimers & Gurevych (2019)**. "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." EMNLP 2019.
  - Foundation cho sentence embeddings used trong diversity calculation (all-MiniLM-L6-v2 model)
