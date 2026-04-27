# Selected Metrics — Rationale & Role of QuGen

Tài liệu này giải thích **tại sao** bộ metrics được chọn cho paper, logic đằng sau thiết kế so sánh 3 chiều, và vai trò của **QuGen** trong hệ thống Auto EDA.

---

## 1. Tại sao cần so sánh 3 chiều?

Paper so sánh ba pipeline:

| Pipeline | Mô tả |
|----------|-------|
| **QUIS** | QuGen (iterative question generation) + IsGen |
| **Baseline** | LLM agentic 5-step, không có question generation |
| **ONLYSTATS** | IsGen trực tiếp từ schema enumeration, không có QuGen |

So sánh **QUIS vs Baseline** trả lời câu hỏi: *Có QuGen tốt hơn không có không?*  
So sánh **QUIS vs ONLYSTATS** trả lời câu hỏi: *QuGen có tốt hơn chỉ liệt kê hết schema không?*

ONLYSTATS là **ablation** quan trọng nhất — nó tách biệt contribution của QuGen (iterative, reasoning-driven question generation) khỏi contribution của IsGen engine. Nếu QUIS chỉ thắng Baseline mà không thắng ONLYSTATS, thì QuGen không thêm giá trị nào so với schema enumeration đơn thuần.

---

## 2. Logic chọn metrics

Bộ 11+ metrics đầy đủ quá rộng để đưa vào paper. Metrics được chọn dựa trên **vai trò trong paper narrative** — mỗi metric trả lời một câu hỏi cụ thể về QuGen.

### 2.1 Faithfulness — Điều kiện tiên quyết

```
faithfulness_score = verified_count / total_count
```

**Tại sao cần:** Trước khi so sánh bất kỳ thứ gì, phải đảm bảo cả 3 pipeline đều không hallucinate. Nếu một pipeline bịa số liệu, mọi metric khác đều vô nghĩa. Kết quả 100%/100%/100% xác nhận: *chênh lệch ở các metric sau phản ánh chất lượng intent/question, không phải lỗi tính toán.*

**Vai trò:** Sanity floor — loại trừ hypothesis "QUIS tốt hơn vì hallucinate ít hơn."

---

### 2.2 Statistical Significance — Chất lượng hypothesis

```
significance_rate = Σ 1(p_i < 0.05) / N

Pattern-specific tests:
  OUTSTANDING_VALUE : z-test,         score = z / (z + 1)
  TREND             : Mann-Kendall τ
  ATTRIBUTION       : Cramér's V
  DISTRIBUTION_DIFF : KS statistic
```

**Tại sao cần:** Insight là một *hypothesis* về data. Một hypothesis vô nghĩa thống kê (p ≥ 0.05) không cung cấp bằng chứng — nó chỉ là noise. Metric này đo xem QuGen có đặt ra những hypothesis có căn cứ thống kê hay không.

**Lưu ý về ONLYSTATS:** ONLYSTATS đạt 92% là *expected upper bound* — exhaustive enumeration tìm được tất cả (B,M) pair, kể cả những pair significant nhất. Điều này không nói lên chất lượng phân tích, chỉ cho thấy systematic search luôn tìm được nhiều significant pattern hơn. QUIS +14.4pp vs Baseline là con số có ý nghĩa thực sự.

**Vai trò:** So sánh QUIS vs Baseline — evidence QuGen sinh hypothesis có chất lượng thống kê cao hơn.

---

### 2.3 Pattern Coverage — Độ phủ analytical

```
pattern_coverage = len(covered_patterns) / 4

covered = patterns có ≥1 structurally valid insight
ALL_PATTERNS = {TREND, OUTSTANDING_VALUE, ATTRIBUTION, DISTRIBUTION_DIFFERENCE}
```

**Tại sao cần:** Bốn pattern đại diện cho bốn loại phân tích khác nhau — temporal trend, outlier detection, category attribution, group comparison. Một hệ thống tốt phải *biết đặt câu hỏi* cho tất cả 4 loại, không tập trung vào một loại quen thuộc. Baseline 3/4 vì toàn bộ ATTRIBUTION insights dùng numeric breakdown — tức Baseline không thực sự hiểu ATTRIBUTION cần gì.

**Vai trò:** Complement cho Significance — không chỉ "nhiều insight significant" mà còn "đặt câu hỏi đa dạng."

---

### 2.4 Structural Validity Rate (SVR) — Core evidence

```
SVR = valid_total / total

valid = breakdown type đúng với pattern:
  TREND                  → Temporal (datetime)
  ATTRIBUTION            → Categorical hoặc ID
  DISTRIBUTION_DIFFERENCE → Categorical hoặc ID
  OUTSTANDING_VALUE      → không ràng buộc
```

**Tại sao cần:** SVR là metric có gap lớn nhất trong toàn bộ evaluation: **QUIS 100% vs Baseline 43%** (+57pp). Đây là bằng chứng trực tiếp nhất cho vấn đề cốt lõi của Baseline — LLM không có cấu trúc không hiểu *breakdown column phải thuộc loại nào* cho từng pattern.

Ví dụ cụ thể:
- **SVR-ATTRIBUTION:** Baseline 0/11 (0%). LLM luôn chọn `Total Sales` hoặc `Units Sold` làm breakdown cho ATTRIBUTION — đây là numeric measure, không phải categorical descriptor. Kết quả là 11/11 insights ATTRIBUTION đều sai về mặt ngữ nghĩa.
- **SVR-TREND:** Baseline 15/39 (38%). 24 insights dùng `Retailer Region` (categorical) làm trục thời gian cho trend analysis.

**Vai trò:** Core evidence cho QuGen vs Baseline — metric *mới* chứng minh schema-awareness là điều kiện cần thiết cho Auto EDA có chất lượng.

---

### 2.5 BM Actionability — Chất lượng intent

```
actionability = len(cat_pairs) / len(pairs)

cat_pairs = (B, M) pairs có B là Categorical, Temporal, hoặc ID
```

**Tại sao cần:** Subgroup discovery — mục tiêu cốt lõi của EDA — chỉ có ý nghĩa khi Breakdown là một categorical descriptor (`Region`, `Category`, `Gender`...). Nếu B là numeric (`Total Sales`), insight không "actionable" theo nghĩa không cho phép so sánh giữa các nhóm. Metric này đo xem QuGen có sinh (B, M) pair đúng hướng không.

QUIS và ONLYSTATS đều đạt 100%. Baseline 67.7% vì LLM sinh numeric breakdown. Điều này cho thấy *bất kỳ approach nào tôn trọng schema classification đều đạt actionability cao* — QuGen không phải cách duy nhất nhưng đạt chuẩn.

**Vai trò:** Complement cho SVR — SVR kiểm tra semantic constraint theo pattern, Actionability kiểm tra constraint chung theo subgroup discovery.

---

### 2.6 Question–Insight Alignment — Control metric

```
Align(Q, I) = mean_i cosine(Embed(q_i), Embed(insight_string_i))

insight_string = "breakdown | measure | pattern | condition"
```

**Tại sao cần:** Nếu QUIS thắng nhiều metrics, có thể có giải thích thay thế: *IsGen của QUIS tốt hơn, không phải QuGen.* Metric này kiểm tra hypothesis đó bằng cách đo xem IsGen có thực sự trả lời câu hỏi QuGen đặt ra không — nếu cả QUIS và Baseline đều có IsGen execute faithfully, thì chênh lệch đến từ QuGen.

Gap QUIS–Baseline chỉ 0.013 (Tie) → xác nhận: **IsGen execute câu hỏi trung thực ở cả hai pipeline.**

**Vai trò:** Control — loại trừ giải thích thay thế, củng cố kết luận rằng QuGen là nguồn cải thiện.

---

### 2.7 Reason–Insight Coherence — QuGen reasoning quality

```
Coh(R, I) = mean_i cosine(Embed(reason_i), Embed(insight_string_i))
```

**Tại sao cần:** `reason` là output *đặc trưng* của QuGen — trường lý giải *tại sao* câu hỏi này đáng khám phá. ONLYSTATS không có reason thực sự (template artifact). Metric này đo xem reason của QuGen có *grounded* với slice/pattern cụ thể hay chỉ là mô tả chung.

QUIS +0.061 vs Baseline: reason của QuGen bám sát context cụ thể (`"Sales in Northeast region show seasonal peaks"`), không phải template (`"This analysis examines sales patterns"`).

**Vai trò:** Proxy cho *quality of reasoning* — khả năng mà neither Baseline nor ONLYSTATS có được.

---

### 2.8 Subspace Rate — Unique contribution của QuGen ★★★

```
subspace_rate = insights_with_subspace / total_insights

subspace = list of (column, value) filter conditions
           e.g., [("Region", "Northeast"), ("Category", "Electronics")]
```

**Tại sao cần:** Subspace Rate là metric **duy nhất** QUIS vượt cả Baseline lẫn ONLYSTATS:

| Pipeline | Subspace Rate |
|----------|--------------|
| QUIS     | 46.4% (45/97) |
| Baseline | 37.2% (32/86) |
| ONLYSTATS | 35.5% (33/93) |

**Đây là bằng chứng thực nghiệm quan trọng nhất cho QuGen.** Câu hỏi conditional của QuGen ("*Within the Northeast region, does the sales trend hold?*") mang *conditional context* vào IsGen — IsGen sau đó có starting point để đào sâu subspace hơn. ONLYSTATS dùng template question không mang conditional context, nên subspace search bắt đầu từ không gian rỗng.

**Vai trò:** Ablation key metric — QuGen unique contribution không thể replicate bởi simple schema enumeration.

---

## 3. Vai trò của QuGen trong Auto EDA

Auto EDA truyền thống có hai hướng:
1. **Rule-based enumeration**: Liệt kê tất cả (B, M) pair → test từng cái. Đảm bảo coverage nhưng không có *intent*.
2. **Unstructured LLM**: Dùng LLM như expert để phân tích. Có intent nhưng không có schema-awareness.

**QuGen là hybrid**: iterative LLM-guided question generation với schema-aware filtering.

### Cái QuGen làm mà hai hướng kia không làm được

**So với Rule-based (ONLYSTATS):**
- QuGen sinh câu hỏi *có lý do* (`reason`) — không chỉ "test xem B, M này có gì" mà "tôi nghĩ B, M này thú vị vì..."
- Câu hỏi conditional của QuGen ("*Within group X...*") → IsGen tìm được subspace insight nhiều hơn (+10.9pp Subspace Rate)
- Iterative in-context learning: càng nhiều vòng, câu hỏi càng focused và chất lượng cao hơn

**So với Unstructured LLM (Baseline):**
- QuGen enforce schema constraints: breakdown type phải đúng cho pattern → SVR 100% vs 43%
- QuGen cover đủ 4 analytical pattern → Pattern Coverage 100% vs 75%
- QuGen sinh hypothesis có significance thống kê cao hơn → +14.4pp

### Tóm lại

QuGen giải quyết *intent problem* của Auto EDA:

> Hệ thống không chỉ cần *tìm được* insight — cần *biết tìm gì* và *tìm đúng chỗ*.

- Rule-based tìm được nhiều thứ nhưng không biết thứ nào quan trọng
- Unstructured LLM biết quan trọng nhưng tìm sai chỗ (wrong breakdown type)
- **QuGen biết quan trọng VÀ tìm đúng chỗ VÀ đặt câu hỏi conditional để đào sâu**

---

## 4. Reading Order cho Paper Narrative

Metrics nên được present theo thứ tự sau để tạo narrative rõ ràng:

```
Faithfulness (sanity floor)
    ↓
SVR (core evidence: QuGen là schema-aware)
    ↓ breakdown sub-metrics
    SVR-ATTRIBUTION (0% vs 100% — extreme case)
    SVR-TREND (38% vs 100%)
    ↓
Significance (QuGen sinh better hypothesis: +14.4pp)
    ↓
Pattern Coverage (QuGen cover đủ 4 pattern)
    ↓
BM Actionability (complement: 100% vs 67.7%)
    ↓
Subspace Rate ★ (unique contribution: +10.9pp vs ablation)
    ↓
Q-I Alignment (control: gap nhỏ → differences từ QuGen, không phải IsGen)
    ↓
R-I Coherence (reasoning quality: QuGen grounded reasoning)
```

Logic: bắt đầu bằng correctness → chứng minh schema-awareness → chứng minh statistical quality → chứng minh unique contribution → loại trừ giải thích thay thế.

---

## 5. Metrics không đưa vào selected (và tại sao)

| Metric | Lý do không chọn |
|--------|-----------------|
| Diversity (semantic, value) | Không phân biệt được QUIS vs ONLYSTATS rõ ràng |
| Time to Insight | Efficiency metric, không liên quan đến quality narrative |
| Token Usage | Idem |
| Question Diversity | Redundant với SVR và Significance trong narrative |
| Question Specificity | Low signal for paper argument |
| Score Uplift | IsGen internal metric, không compare across pipelines |
| BM — NMI | High variance, signal weaker hơn Actionability |
| BM — Interestingness | Idem |
| Subspace Count | Subspace Rate đủ đại diện |

Nguyên tắc loại: giữ metrics có **largest gap** hoặc **clearest role** trong argument. Mỗi metric trong selected set phải trả lời một câu hỏi khác nhau về QuGen.
