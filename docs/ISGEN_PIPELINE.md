# ISGEN Pipeline – Theo bài báo QUIS (Section 3.2, Figure 1)

Tài liệu mô tả **Insight Generation (ISGEN)**: từ Insight Cards DB → Basic insight + Subspace search → LLM (NL explanation) → Plotting (rule-based) → Insight Summary.

---

## 1. Định nghĩa Insight (Section 2)

Một **insight** là bộ bốn thành phần **Insight(B, M, S, P)**:

| Thành phần | Ký hiệu | Mô tả |
|------------|---------|--------|
| **Breakdown** | B | Cột (chiều) để nhóm và so sánh. |
| **Measure** | M | Đại lượng agg(C): SUM, MEAN, COUNT, MIN, MAX trên cột C. |
| **Subspace** | S | Tập bộ lọc {(Xi, yi)}: chỉ giữ dòng có D[Xi] = yi. S = φ khi không lọc. |
| **Pattern** | P | Loại insight: Trend, Outstanding Value, Attribution, Distribution Difference. |

**View:** `view(D, B, M)` = GROUP BY B, tính M (tương đương SQL). Với subspace S: `view(DS, B, M)` trên dữ liệu đã lọc DS.

---

## 2. Luồng ISGEN (Figure 1)

1. **Input:** Insight Cards DB (mỗi card: Reason, Question, Breakdown B, Measure M).
2. **Basic insight:** Với mỗi card, tính v0 = view(D, B, M). Áp dụng pattern P phù hợp với kiểu B/M; nếu SCOREFUNC_P(v0) > T_P thì trả về Insight(B, M, φ, P).
3. **Subspace search (Algorithm 1):** Beam search mở rộng subspace: bắt đầu S0, mỗi bước thêm bộ lọc (cột X, giá trị y). Cột X được gợi ý bởi LLM (w_LLM), giá trị y lấy mẫu theo tần suất log(1+N(y)). Đánh giá mỗi subspace bằng SCOREFUNC_P(view(D_S, B, M)); giữ top-k beam. Chỉ xuất subspace có score > T_P.
4. **If interesting:** Chỉ các insight (basic hoặc từ subspace) đạt ngưỡng mới đưa tiếp.
5. **LLM (NL explanation):** Mô tả bằng ngôn ngữ tự nhiên (template hoặc LLM) theo từng pattern P.
6. **Plotting (rule-based):** Vẽ đồ thị theo pattern (Appendix B): Trend → scatter + trend line; Outstanding Value → bar; Attribution → bar (%); Distribution Difference → pie (trước/sau).
7. **Output:** Insight Summary (danh sách insight kèm mô tả NL và hình).

---

## 3. Scoring functions và ngưỡng (Appendix A)

Với view v = {v1, ..., vk} (các giá trị measure theo breakdown):

| Pattern | SCOREFUNC | Ngưỡng T |
|---------|-----------|----------|
| **Trend** | 1 − p_value(Mann-Kendall(v)) | T_Trend = 0.95 |
| **Outstanding Value** | vmax1 / vmax2 (hai giá trị lớn nhất) | T_OV = 1.4 |
| **Attribution** | max(v_i) / Σ v_i | T_Attr = 0.5 |
| **Distribution Difference** | Chỉ khi measure = COUNT(); JSD(phân phối vI, phân phối vF) | T_DD = 0.2 |

---

## 4. Plotting theo pattern (Appendix B)

| Pattern | Loại đồ thị |
|---------|-------------|
| Trend | Scatter + đường xu hướng |
| Outstanding Value | Bar chart |
| Attribution | Bar chart (% đóng góp) |
| Distribution Difference | Pie charts (trước / sau điều kiện) |

---

## 5. Tham số ISGEN (Appendix D.2)

- beam_width = 100  
- exp_factor = 100  
- max_depth = 1  
- w_LLM = 0.5 (khối lượng xác suất cho cột do LLM gợi ý)

---

## 6. Input / Output

| | Mô tả |
|--|--------|
| **Input** | Danh sách Insight Cards (từ QUGEN, file JSON hoặc list); DataFrame D (CSV). |
| **Output** | Insight Summary: danh sách insight (B, M, S, P) kèm mô tả NL và đồ thị (file hoặc object). |

---

## 7. File và module tương ứng (code)

- `quis/isgen/models.py` – Insight(B,M,S,P), Subspace.
- `quis/isgen/views.py` – view(D, B, M), parse measure, áp dụng S.
- `quis/isgen/scoring.py` – SCOREFUNC và T cho từng pattern.
- `quis/isgen/basic_insight.py` – Basic insight từ card.
- `quis/isgen/subspace_search.py` – Algorithm 1 (beam search).
- `quis/isgen/llm_filter_columns.py` – LLM gợi ý cột lọc.
- `quis/isgen/nl_explanation.py` – Mô tả NL (template / LLM).
- `quis/isgen/plotting.py` – Vẽ đồ thị theo pattern.
- `quis/isgen/pipeline.py` – Luồng đầy đủ ISGEN.
- `run_isgen.py` – CLI.
