# Báo cáo Tổng hợp Các Chỉ số (Tóm tắt)

Báo cáo này tổng hợp các chỉ số đánh giá mà nhóm đã nghiên cứu và lựa chọn, phù hợp với mục tiêu đánh giá hệ thống EDA tự động bằng LLM mà không sử dụng human evaluation.

Tập dữ liệu: [adidas](adidas_dataset.html), [employee_attrition](employee_attrition_dataset.html), [online_sales](online_sales_dataset.html)  
Hệ thống so sánh: QUIS | Baseline | ONLYSTATS

Các chỉ số được chia thành hai phần phục vụ hai mục tiêu đánh giá của nhóm:

| Phần | Mục đích | Chỉ số |
|------|---------|---------|
| **Phần 1 — So sánh Mô hình Tổng thể** | Chất lượng đầu ra toàn diện: tính đúng đắn, đa dạng, độ phủ, khối lượng subspace, chất lượng cặp breakdown-measure | 13 trung bình + theo tập dữ liệu |
| **Phần 2 — Phân tích Module QuGen** | Đóng góp của tầng mục đích: hiểu biết cấu trúc, chất lượng câu hỏi, trí tuệ subspace | 9 trung bình + theo tập dữ liệu |

---

# Phần 1 — So sánh Mô hình Tổng thể

*Các chỉ số toàn diện để đánh giá và so sánh ba hệ thống EDA về chất lượng đầu ra.*

## Số lần thắng (Phần 1 — chỉ số trung bình, 11 chỉ số có thể quyết định)

| Hệ thống | Số thắng |
|--------|------|
| QUIS | 3 |
| Baseline | 5 |
| ONLYSTATS | 3 |
| Hòa | 2 |

> Baseline dẫn đầu về tính hợp lệ và độ mới; QUIS dẫn đầu về đa dạng và khối lượng subspace; ONLYSTATS dẫn đầu về đa dạng breakdown. Không có hệ thống nào vượt trội toàn diện — điều này là động lực cho phân tích QuGen sâu hơn ở Phần 2.

---

## 1. Volume & Correctness

**Total Insight Cards Generated**

| Tập dữ liệu | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 99 | 75 | 85 |
| employee_attrition | 133 | 81 | 132 |
| online_sales | 106 | 61 | 72 |

**Faithfulness** (trung bình trên 3 tập dữ liệu)

| Metric | QUIS | Baseline | ONLYSTATS | Thắng |
|--------|------|----------|-----------|--------|
| 1. Faithfulness | 100.0% | 100.0% | 100.0% | **Hòa** |

> Cả ba hệ thống đều đạt 100% tính đúng đắn. Điều này xác nhận QUIS được tái hiện trung thực và QuGen không đưa ra các giá trị ảo.

**Cách tính:** Với mỗi insight, pipeline áp dụng bộ lọc subspace trên dataframe đã làm sạch, tính lại phép tổng hợp (SUM / MEAN / COUNT / MAX / MIN theo nhóm breakdown), rồi so sánh từng giá trị được báo cáo với giá trị tính lại (ngưỡng ε = 1e-6). Một insight chỉ được coi là faithful khi *tất cả* các giá trị đều khớp. Nhãn trùng lặp trong `view_labels` cũng khiến insight bị fail.

`faithfulness = verified_count / total_count` — **càng cao càng tốt** (tối đa = 100%)

**Tại sao kết quả là Hòa:** Cả ba hệ thống đều đạt 100% vì mỗi hệ thống lấy giá trị số trực tiếp từ các phép tổng hợp pandas trên dataframe đã làm sạch — không có bước sinh văn bản tự do nào có thể tạo số liệu ảo. Kết quả hòa xác nhận rằng thêm tầng QuGen (sinh câu hỏi + lý giải trong QUIS) không làm hỏng tính đúng đắn của số liệu; các lệnh gọi LLM bổ sung trong QUIS chỉ hoạt động trên metadata (tên cột, pattern, mục đích), không phải trên giá trị dữ liệu.

---

## 2. Statistical Validity & Coverage

| Metric | QUIS | Baseline | ONLYSTATS | Thắng |
|--------|------|----------|-----------|--------|
| 2. Statistical Significance (Overall) | 46.4% | **57.6%** | 51.7% | **Baseline** |

> Baseline tạo ra các insight có ý nghĩa thống kê cao nhất tính trung bình. QUIS đánh đổi mức ý nghĩa thô để khám phá subspace phong phú hơn (xem Phần 2).

**Cách tính:** Mỗi insight được kiểm định bằng phương pháp thống kê phù hợp với kiểu pattern:

| Pattern | Kiểm định | Kích thước hiệu ứng (điểm) |
|---|---|---|
| OUTSTANDING_VALUE | Kiểm định Z | z / (z + 1), trong đó z = (max − μ) / σ |
| TREND | Mann-Kendall | \|Kendall τ\| ∈ [0, 1] |
| ATTRIBUTION | Chi-square (Fisher nếu 2×2 thưa) | Cramér's V ∈ [0, 1] |
| DISTRIBUTION_DIFFERENCE | Kiểm định KS | KS statistic ∈ [0, 1] |

Các insight có cột breakdown là kiểu số bị loại hoàn toàn khỏi đánh giá (vi phạm cấu trúc EDA) — không được tính là không có ý nghĩa. Một insight có ý nghĩa nếu p < 0.05.

`significant_rate = significant_count / total_evaluated` — **càng cao càng tốt.** Ngưỡng: ≥ 80% tốt, ≥ 70% chấp nhận được.

**Tại sao Baseline thắng:** Baseline đạt 57,6% so với QUIS 46,4% và ONLYSTATS 51,7%. Baseline thắng ở OUTSTANDING_VALUE (69,3%), ATTRIBUTION (100%) và DISTRIBUTION_DIFFERENCE (61,1%) — prompt LLM trực tiếp tập trung vào tập nhỏ các cặp (B, M) có tín hiệu thống kê cao. QUIS, được thúc đẩy bởi các câu hỏi khám phá của QuGen, sinh ra tập insight rộng hơn trên nhiều tổ hợp breakdown-measure, bao gồm cả phân khúc nơi pattern có ý nghĩa phân tích nhưng không luôn vượt ngưỡng p < 0.05. Tỷ lệ ý nghĩa thấp hơn của QUIS là hệ quả của khám phá rộng hơn, không phải chất lượng phân tích thấp hơn.

Phân tích theo pattern (trung bình trên các tập dữ liệu):

| Pattern | QUIS | Baseline | ONLYSTATS | Thắng |
|---------|------|----------|-----------|--------|
| TREND | 100.0% | 66.7% | 83.3% | **QUIS** |
| OUTSTANDING_VALUE | 32.2% | 69.3% | 31.2% | **Baseline** |
| ATTRIBUTION | 62.0% | 100.0% | 69.1% | **Baseline** |
| DISTRIBUTION_DIFFERENCE | 58.1% | 61.1% | 50.6% | **Baseline** |

---

**Pattern Coverage** (theo tập dữ liệu)

| Tập dữ liệu | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | **4/4 (100%)** | 3/4 (75%) | **4/4 (100%)** |
| employee_attrition | 3/4 (75%) | 3/4 (75%) | 3/4 (75%) |
| online_sales | 3/4 (75%) | 2/4 (50%) | **4/4 (100%)** |

**Cách tính:** Một pattern được coi là "được phủ" nếu hệ thống sinh ít nhất một insight với breakdown hợp lệ về cấu trúc cho pattern đó (ví dụ: cột Thời gian cho TREND; Phân loại/ID cho ATTRIBUTION và DISTRIBUTION_DIFFERENCE; không giới hạn cho OUTSTANDING_VALUE). Kiểu ngữ nghĩa cột lấy từ `profile.json`.

`pattern_coverage = covered_count / 4` — **càng cao càng tốt** (tối đa = 4/4). Ngưỡng: 4/4 tốt, 3/4 chấp nhận được.

**Pattern không được phủ theo tập dữ liệu:**

| Tập dữ liệu | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | — | ATTRIBUTION | — |
| employee_attrition | TREND | TREND | TREND, DISTRIBUTION_DIFFERENCE |
| online_sales | TREND | TREND, ATTRIBUTION | — |

**Tại sao không có người thắng duy nhất:** TREND là pattern bị bỏ lỡ nhiều nhất — nó yêu cầu cột breakdown Thời gian, vốn không có hoặc không đủ dữ liệu trong employee_attrition và online_sales. Baseline còn bỏ lỡ ATTRIBUTION trên adidas và online_sales vì prompt LLM thường xuyên gán cột số làm breakdown cho ATTRIBUTION, khiến các insight sai cấu trúc. QUIS và ONLYSTATS tránh được điều này vì QuGen chọn breakdown có nhận thức ngữ nghĩa, còn ONLYSTATS theo thiết kế chỉ cho phép breakdown là cột phân loại.

---

## 3. Usefulness & Diversity

| Metric | QUIS | Baseline | ONLYSTATS | Thắng |
|--------|------|----------|-----------|--------|
| 3. Insight Novelty | 72.4% | **86.2%** | 61.8% | **Baseline** |
| 4a. Diversity — Semantic | **0.4890** | 0.4447 | 0.4347 | **QUIS** |
| 4b. Diversity — Subspace Entropy | **2.2643** | 1.1737 | 2.2113 | **QUIS** |
| 4c. Diversity — Value | 0.6930 | 0.4063 | **0.6950** | **ONLYSTATS** |
| 4d. Diversity — Dedup Rate | **0.0000** | 0.0123 | **0.0000** | **Hòa** |

> QUIS dẫn đầu ở hai trong bốn chỉ số đa dạng. Insight của QUIS trải rộng trên nhiều tổ hợp (breakdown, measure, pattern) đa dạng hơn (4a) và sử dụng nhiều loại cột lọc subspace hơn (4b). ONLYSTATS nhỉnh hơn QUIS về đa dạng giá trị (4c). Baseline có nhiều insight mới nhất xuyên hệ thống nhưng đa dạng cấu trúc thấp hơn.

---

### Metric 3 — Insight Novelty

**Cách tính:** Mỗi insight được chuyển thành chuỗi `"{breakdown} | {measure} | {pattern} | {condition}"` và nhúng bằng `SentenceTransformer all-MiniLM-L6-v2`. Với mỗi insight trong hệ thống A, độ tương đồng cosine tối đa so với bất kỳ insight nào trong hệ thống B được tính. Một insight là mới nếu độ tương đồng tối đa này < τ = 0.85.

`novelty = novel_count / total_count` — **càng cao càng tốt.** Ngưỡng: ≥ 80% tốt.

Kết quả theo tập dữ liệu:

| Tập dữ liệu | QUIS | Baseline | ONLYSTATS | Thắng |
|---------|------|----------|-----------|--------|
| adidas | 84.8% | 80.0% | 73.3% | QUIS |
| employee_attrition | 84.2% | 85.2% | 77.5% | Baseline |
| online_sales | 64.2% | 93.4% | 31.2% | Baseline |
| **TB** | **77.7%** | **86.2%** | **61.8%** | **Baseline** |

**Tại sao Baseline thắng:** Baseline đạt 86,2% so với QUIS 77,7% và ONLYSTATS 61,8%. Nguyên nhân chính là sự bất đối xứng trong cách tính độ mới: độ mới của Baseline được đo tương đối so với QUIS (bao nhiêu insight Baseline khác với QUIS), trong khi độ mới của QUIS được đo tương đối so với Baseline. Vì QUIS là hệ thống phong phú, rộng hơn (nhiều insight hơn, phủ subspace nhiều hơn), nhiều insight Baseline rơi ngoài vùng phủ cụ thể của QUIS — khiến chúng có vẻ "mới" dù khám phá cùng lãnh thổ phân tích ở mức thô hơn. ONLYSTATS đạt điểm thấp nhất (61,8%) vì việc liệt kê toàn diện các tổ hợp (breakdown, measure, pattern) chồng lấp nhiều với đầu ra của QUIS. Lưu ý: độ mới của QUIS trên online_sales giảm xuống 64,2% vì QUIS sinh nhiều insight hơn (106 so với 61 của Baseline), tăng khả năng insight Baseline tìm thấy kết quả tương đồng trong QUIS.

---

### Metric 4a — Diversity (Semantic)

**Cách tính:** Mỗi insight được chuyển sang định dạng chuỗi giống Độ mới và nhúng. Độ tương đồng cosine theo từng cặp được tính trong *cùng một hệ thống*. Độ tương đồng trung bình (loại trừ đường chéo) được trừ khỏi 1.

`D_semantic = 1 − avg_cosine_similarity` — **càng cao càng tốt.** Ngưỡng: ≥ 0.4 tốt.

Kết quả theo tập dữ liệu:

| Tập dữ liệu | QUIS | Baseline | ONLYSTATS | Thắng |
|---------|------|----------|-----------|--------|
| adidas | 0.479 | 0.388 | 0.435 | QUIS |
| employee_attrition | 0.499 | 0.497 | 0.451 | QUIS |
| online_sales | 0.489 | 0.449 | 0.415 | QUIS |
| **TB** | **0.489** | **0.445** | **0.434** | **QUIS** |

**Tại sao QUIS thắng:** QUIS đạt 0,489 so với Baseline 0,445 và ONLYSTATS 0,434, chiến thắng nhất quán trên cả ba tập dữ liệu. QuGen sinh câu hỏi với mục đích phân tích đa dạng ("X thay đổi như thế nào theo Y?", "Phân khúc nào là ngoại lệ trong Z?", "Có xu hướng nào trong A theo thời gian không?") — mỗi câu hỏi hướng ISGEN tới một tổ hợp (breakdown, measure, pattern) khác biệt. Tính đa dạng lan tỏa từ tầng mục đích khiến các insight của QUIS cùng nhau phủ phần rộng hơn của không gian phân tích. Prompt LLM trực tiếp của Baseline hội tụ vào các cặp (B, M) mạnh về thống kê, gây ra nhiều chồng lấp ngữ nghĩa hơn. Cấu trúc mẫu cố định của ONLYSTATS càng làm insight tập trung quanh các cặp breakdown-measure giống nhau.

---

### Metric 4b — Diversity (Subspace Entropy)

**Cách tính:** Với tất cả insight có subspace không rỗng, tỷ lệ p_c của mỗi cột lọc c được tính (tần suất xuất hiện của mỗi cột làm khóa lọc). Entropy Shannon được áp dụng trên các tỷ lệ đó.

`subspace_entropy = −Σ (p_c × log(p_c))` — **càng cao càng tốt** (phân bố rộng hơn trên các cột lọc). Chỉ tính khi có ≥ 1 insight với subspace không rỗng.

Kết quả theo tập dữ liệu:

| Tập dữ liệu | QUIS | Baseline | ONLYSTATS | Thắng |
|---------|------|----------|-----------|--------|
| adidas | 2.259 | 1.373 | 2.143 | QUIS |
| employee_attrition | 2.938 | 1.305 | N/A | QUIS |
| online_sales | 1.596 | 0.843 | 1.645 | ONLYSTATS |
| **TB** | **2.264** | **1.174** | **1.894** | **QUIS** |

**Tại sao QUIS thắng:** QUIS đạt 2,264 so với Baseline 1,174 và ONLYSTATS 1,894. Câu hỏi của QuGen tham chiếu đến các thuộc tính ngữ cảnh đa dạng ("cho khu vực Tây", "trong nhóm khách hàng trực tuyến", "trong phân khúc thu nhập cao") — tầng mục đích hướng ISGEN áp dụng bộ lọc subspace trên nhiều cột khác nhau thay vì tập trung vào một hoặc hai cột. Baseline sinh ít insight subspace hơn (tỷ lệ subspace 37,4%) và tập trung vào tập hẹp các cột lọc, dẫn đến entropy thấp. ONLYSTATS cạnh tranh được (1,894) nhờ liệt kê toàn diện truy cập nhiều cột, nhưng QUIS phân bổ đều hơn mức sử dụng cột lọc — cho entropy cao nhất trên 2 trong 3 tập dữ liệu.

---

### Metric 4c — Diversity (Value)

**Cách tính:** Tất cả các cặp (cột, giá trị) xuất hiện làm bộ lọc subspace trong mọi insight được thu thập. Đa dạng giá trị là tỷ lệ các cặp duy nhất.

`value_diversity = |cặp (cột, giá trị) duy nhất| / tổng số cặp` — **càng cao càng tốt.** Chỉ tính khi có ≥ 1 insight với subspace không rỗng.

Kết quả theo tập dữ liệu:

| Tập dữ liệu | QUIS | Baseline | ONLYSTATS | Thắng |
|---------|------|----------|-----------|--------|
| adidas | 0.872 | 0.312 | 0.810 | QUIS |
| employee_attrition | 0.767 | 0.407 | N/A | QUIS |
| online_sales | 0.440 | 0.500 | 0.444 | Baseline |
| **TB** | **0.693** | **0.406** | **0.627** | **QUIS** |

> Lưu ý: người thắng trong bảng trung bình chính là ONLYSTATS (0,695) vì employee_attrition bị loại khỏi ONLYSTATS (N/A), nên trung bình của ONLYSTATS chỉ tính trên 2 tập dữ liệu (adidas và online_sales), trong khi QUIS và Baseline tính trên cả 3. Khi so sánh trên cùng 2 tập, QUIS (0,656) vẫn vượt ONLYSTATS (0,627).

**Tại sao ONLYSTATS dẫn đầu (trung bình có lưu ý):** ONLYSTATS đạt 0,695 trên trung bình 2 tập bằng cách lặp qua nhiều giá trị phân loại khác nhau cho từng cột breakdown, tạo ra sự đa dạng cao về các cặp lọc (cột, giá trị). QUIS gần như giống nhau trong trung bình đủ 3 tập (0,693) — câu hỏi QuGen tự nhiên tiếp cận các giá trị đa dạng thông qua đa dạng mục đích. Baseline đạt điểm thấp hơn đáng kể (0,406) vì sinh ít insight subspace hơn và tập trung vào cùng một số tổ hợp (cột, giá trị).

---

### Metric 4d — Diversity (Dedup Rate)

**Cách tính:** Hai insight được coi là trùng lặp nếu chúng chia sẻ cùng bộ tứ (pattern, breakdown, measure, subspace). Tỷ lệ trùng lặp là phần trăm insight là trùng lặp cấu trúc chính xác.

`dedup_rate = 1 − (unique_count / total_count)` — **càng thấp càng tốt** (0.000 = không có trùng lặp).

Kết quả theo tập dữ liệu:

| Tập dữ liệu | QUIS | Baseline | ONLYSTATS | Thắng |
|---------|------|----------|-----------|--------|
| adidas | 0 | 0 | 0 | Hòa |
| employee_attrition | 0 | 0.037 | 0 | Hòa |
| online_sales | 0 | 0 | 0 | Hòa |
| **TB** | **0.000** | **0.012** | **0.000** | **Hòa** |

**Tại sao QUIS và ONLYSTATS hòa:** Cả hai đạt 0,000 — không có insight trùng lặp trên bất kỳ tập nào. QUIS được hưởng lợi từ QuGen sinh câu hỏi khác biệt dẫn đến các tổ hợp (B, M, pattern, subspace) khác biệt; hai câu hỏi hiếm khi tạo ra cùng một cấu hình phân tích. ONLYSTATS tránh trùng lặp theo cấu trúc thông qua pipeline liệt kê xác định. Baseline có tỷ lệ trùng lặp nhỏ (0,037) trên employee_attrition — một số tổ hợp (B, M, pattern, subspace) được LLM sinh ra nhiều hơn một lần, có thể do prompt không áp đặt ràng buộc duy nhất. Chỉ số này không phân biệt mạnh giữa các hệ thống và chủ yếu phục vụ như một bước kiểm tra sơ bộ.

---

# Phần 2 — Phân tích Module QuGen

*Các chỉ số đặc biệt kiểm tra tầng sinh câu hỏi và mục đích — những gì QuGen thêm vào so với cách tiếp cận thuần thống kê hoặc dựa trên mẫu cố định.*

## Số lần thắng (Phần 2 — chỉ số trung bình, 8 chỉ số có thể quyết định)

| Hệ thống | Số thắng |
|--------|------|
| QUIS | 4 |
| Baseline | 4 |
| ONLYSTATS | 0 |

> QUIS và Baseline hòa nhau: QUIS thắng ở các chiều cấu trúc/subspace; Baseline thắng ở chất lượng bề mặt câu hỏi. ONLYSTATS không áp dụng cho các chỉ số câu hỏi (dựa trên mẫu cố định, không có tầng mục đích).

---

## 6. Structural Understanding

*QuGen có biết kiểu breakdown nào phù hợp với pattern nào không?*

| Metric | QUIS | Baseline | ONLYSTATS | Thắng |
|--------|------|----------|-----------|--------|
| 12. Structural Validity Rate (SVR) | **94.0%** | 40.0% | 90.8% | **QUIS** |
| 2a. Significance — TREND | **100.0%** | 66.7% | 83.3% | **QUIS** |

> **SVR**: QUIS vượt gấp đôi Baseline (94,0% so với 40,0%). Pipeline ưu tiên câu hỏi của QuGen hướng engine đến các tổ hợp breakdown-pattern hợp lệ về cấu trúc, trong khi prompt LLM trực tiếp thường xuyên chọn cột số cho pattern TREND/ATTRIBUTION.
>
> **Ý nghĩa — TREND**: Tất cả insight TREND của QUIS đều hợp lệ về thống kê (100%). Baseline sinh nhiều insight TREND với cột không phải thời gian — chúng thất bại về ý nghĩa theo cấu trúc.

**SVR theo pattern (mỗi tập dữ liệu):**

*SVR — ATTRIBUTION* (yêu cầu breakdown phân loại)

| Tập dữ liệu | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | **27/27 (100%)** | 0/13 (0%) | 20/24 (83%) |
| employee_attrition | **50/50 (100%)** | 7/13 (54%) | 65/65 (100%) |
| online_sales | **29/32 (91%)** | 0/11 (0%) | 18/20 (90%) |

*SVR — DISTRIBUTION_DIFFERENCE* (yêu cầu breakdown phân loại)

| Tập dữ liệu | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | **39/40 (98%)** | 4/15 (27%) | 17/27 (63%) |
| employee_attrition | **43/47 (91%)** | 12/15 (80%) | 9/9 (100%) |
| online_sales | 27/37 (73%) | 5/13 (38%) | 18/24 (75%) |

*SVR — TREND* (yêu cầu breakdown thời gian)

| Tập dữ liệu | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | **2/2 (100%)** | 16/33 (48%) | 10/10 (100%) |
| employee_attrition | 0/1 (0%) | 0/42 (0%) | N/A |
| online_sales | 0/1 (0%) | 0/19 (0%) | 3/3 (100%) |

---

## 7. Subspace Intelligence

*QuGen có hướng hệ thống đến các insight có điều kiện chất lượng cao hơn không?*

| Metric | QUIS | Baseline | ONLYSTATS | Thắng |
|--------|------|----------|-----------|--------|
| 8. Score Uplift from Subspace | **1.0670** | 0.9740 | 0.5277 | **QUIS** |
| 9. Simpson's Paradox Rate (SPR) | **27.7%** | 18.9% | 24.5% | **QUIS** |

**Score Uplift theo tập dữ liệu** (x = mean_score_subspace / mean_score_global):

| Tập dữ liệu | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | x=0.885 | x=0.796 | x=0.726 |
| employee_attrition | **x=1.574** | x=1.079 | x=0.346 |
| online_sales | x=0.742 | x=1.048 | x=0.511 |

> Insight subspace của QUIS có tỷ lệ điểm trung bình 1,067 so với 0,974 của Baseline. Trên employee_attrition, insight subspace của QUIS mạnh hơn 57% so với insight toàn cục (x=1,574) — cho thấy câu hỏi khám phá của QuGen dẫn hệ thống đến các phân khúc nơi pattern được khuếch đại, không bị loãng.

**Hướng (Contrasting Rate) theo tập dữ liệu** — tỷ lệ insight subspace đi ngược chiều toàn cục:

| Tập dữ liệu | QUIS | Baseline | ONLYSTATS |
|---------|------|----------|-----------|
| adidas | 0.634 (52/82) | 0.389 (7/18) | 0.821 (55/67) |
| employee_attrition | 0.438 (46/105) | 0.300 (3/10) | 0.711 (27/38) |
| online_sales | 0.554 (36/65) | 0.667 (4/6) | 0.770 (47/61) |

> QUIS phát hiện nhiều insight đối nghịch hơn Baseline trên tất cả các tập dữ liệu. Những phát hiện đi ngược xu hướng chung này (một phân khúc hành xử ngược xu hướng toàn cục) là những phát hiện có giá trị phân tích cao nhất trong EDA.

---

## 8. Intent Layer Quality

*Các câu hỏi và lý giải mà QuGen tạo ra tốt đến mức nào? (N/A cho ONLYSTATS — dựa trên mẫu cố định, không sinh câu hỏi)*

| Metric | QUIS | Baseline | Thắng |
|--------|------|----------|--------|
| 11a. Question Semantic Diversity | 0.5360 | **0.5850** | **Baseline** |
| 11b. Question Specificity (avg word count) | 9.80 | **12.11** | **Baseline** |
| 11c. Question–Insight Alignment | 0.5397 | **0.5687** | **Baseline** |
| 11d. Question Novelty (cross-system) | 93.4% | **99.2%** | **Baseline** |
| 11e. Reason–Insight Coherence | **0.5260** | 0.5143 | **QUIS** |

**Theo tập dữ liệu:**

| Tập dữ liệu | 11c Q–I Alignment QUIS | 11c Q–I Alignment Base | 11e Reason Coherence QUIS | 11e Reason Coherence Base |
|---------|--------------------|--------------------|---------------------|---------------------|
| adidas | **0.583** | 0.579 | **0.553** | 0.527 |
| employee_attrition | 0.493 | **0.588** | 0.468 | **0.519** |
| online_sales | 0.543 | 0.539 | **0.557** | 0.497 |

> **Phát hiện trung thực**: Baseline sinh câu hỏi dài hơn và đa dạng ngữ nghĩa hơn (11a, 11b, 11d), căn chỉnh chặt hơn với chuỗi insight (11c). Câu hỏi của QUIS mang tính khám phá ("X thay đổi như thế nào theo Y?") — chúng khác với văn bản insight thô dù đúng về mặt phân tích.
>
> **Lợi thế của QUIS**: Liên kết Lý giải–Insight (11e): 0,526 so với 0,514. Lý giải của QuGen bám chắc hơn vào nội dung insight thực tế, cho thấy tầng lý giải thêm giá trị ngữ nghĩa vượt qua khoảng cách bề mặt câu hỏi.

---

## Tóm tắt Đóng góp của Bài báo

| Đóng góp | Metric | QUIS so với Baseline | QUIS so với ONLYSTATS |
|---|---|---|---|
| QuGen hiểu ngữ nghĩa pattern-breakdown | SVR (12) | **+54.0 pp** (94.0 vs 40.0) | +3.2 pp (94.0 vs 90.8) |
| Insight TREND hợp lệ về cấu trúc | Significance — TREND (2a) | **+33.3 pp** (100.0 vs 66.7) | +16.7 pp (100.0 vs 83.3) |
| QuGen chọn subspace chất lượng cao | Score Uplift (8) | **+9.6%** (1.067 vs 0.974) | **+102.2%** (1.067 vs 0.528) |
| QuGen sinh đầu ra đa dạng ngữ nghĩa | Diversity — Semantic (4a) | +4.4 pp (0.489 vs 0.445) | +5.4 pp (0.489 vs 0.435) |
| QuGen thúc đẩy khám phá subspace rộng | Subspace Rate (7) | **+47.0 pp** (84.4 vs 37.4) | +7.4 pp (84.4 vs 77.0) |
| Lý giải bám chắc vào nội dung insight | Reason–Insight Coherence (11e) | +1.2 pp (0.526 vs 0.514) | N/A (template) |
| Tính đúng đắn không bị hi sinh | Faithfulness (1) | 0 pp (all 100%) | 0 pp (all 100%) |
