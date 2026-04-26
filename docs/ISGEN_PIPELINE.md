# ISGEN Pipeline – Theo bài báo QUIS (Section 3.2, Figure 1)

Tài liệu mô tả **ISGEN (ISGEN)** trong project: từ Insight Cards + CSV → Basic insight + Subspace search → Deduplicate → NL explanation + Plotting → Insight Summary.

---

## 1. Định nghĩa Insight (Section 2)

Một **insight** là bộ bốn thành phần **Insight(B, M, S, P)**:

| Thành phần | Ký hiệu | Mô tả |
|------------|---------|--------|
| **Breakdown** | B | Cột (chiều) để nhóm và so sánh. |
| **Measure** | M | Đại lượng agg(C): SUM, MEAN, COUNT, MIN, MAX trên cột C. |
| **Subspace** | S | Tập bộ lọc {(Xi, yi)}: chỉ giữ dòng có D[Xi] = yi. S = φ khi không lọc. |
| **Pattern** | P | Loại insight: Trend, Outstanding Value, Attribution, Distribution Difference. |

**View:** `view(D, B, M)` = GROUP BY B, tính M (tương đương SQL). Với subspace S: `view(D_S, B, M)` trên dữ liệu đã lọc D_S.

---

## 2. Luồng ISGEN hiện tại (code)

1. **Input:** File Insight Cards (JSON từ QUGEN) + CSV (DataFrame). Mỗi card: `question`, `reason`, `breakdown`, `measure`.

2. **Column resolution:** Với mỗi card, map tên cột từ card (có thể có dấu cách, tiếng Việt) sang tên cột thực trong CSV qua `resolve_card_columns()` trong `views.py` (exact → normalized → token overlap). Card không map được thì bỏ qua.

3. **Thu thập candidate (chưa vẽ plot):**
   - **Basic insight:** Với mỗi card đã resolve, tính v0 = view(D, B, M). Áp dụng pattern P phù hợp (Trend, Outstanding Value, Attribution); nếu score > ngưỡng → thêm (insight_dict, question) vào danh sách candidate.
   - **Subspace search (Algorithm 1):** Nếu bật subspace, với mỗi card và mỗi pattern (Outstanding Value, Attribution), beam search mở rộng subspace; cột lọc có thể do LLM gợi ý (`llm_filter_columns.py`) thông qua API thật. Chỉ thêm subspace đạt ngưỡng vào candidate (tối đa 2 subspace per card/pattern). Mỗi candidate là (insight_dict, question).

4. **Deduplicate (trước khi vẽ plot):**
   - **Theo (question, breakdown, measure, pattern):** Mỗi nhóm giữ tối đa `max_overall_per_key` insight overall (subspace rỗng) và `max_subspace_per_key` insight subspace (chọn theo score).
   - **Theo question:** Mỗi question chỉ giữ tối đa `max_insights_per_question` insight (chọn theo score). Giảm trùng câu hỏi trong báo cáo.

5. **Chỉ với insight được giữ:** Với từng item trong danh sách đã dedup: tạo **NL explanation** (template theo pattern trong `nl_explanation.py`), **vẽ plot** (rule-based trong `plotting.py`), ghi file PNG vào `--plot-dir`, và đưa vào **Insight Summary**.

6. **Output:** File JSON Insight Summary (question, explanation, plot_path, insight) và thư mục đồ thị PNG (nếu dùng `--plot-dir`).

---

## 3. Scoring và ngưỡng (Appendix A)

Với view v = {v1, ..., vk} (các giá trị measure theo breakdown):

| Pattern | SCOREFUNC | Ngưỡng T |
|---------|-----------|----------|
| **Trend** | 1 − p_value(Mann-Kendall(v)) | T_Trend = 0.95 |
| **Outstanding Value** | vmax1 / vmax2 (hai giá trị lớn nhất) | T_OV = 1.4 |
| **Attribution** | max(v_i) / Σ v_i | T_Attr = 0.5 |
| **Distribution Difference** | Chỉ khi measure = COUNT(); JSD | T_DD = 0.2 |

Code: `ifq/isgen/scoring.py`.

---

## 4. Plotting theo pattern (Appendix B)

| Pattern | Loại đồ thị |
|---------|-------------|
| Trend | Scatter + đường xu hướng |
| Outstanding Value | Bar chart |
| Attribution | Pie chart (% đóng góp) |
| Distribution Difference | Pie charts (trước / sau điều kiện) |

Code: `ifq/isgen/plotting.py`.

---

## 5. Tham số ISGEN (hiện tại)

| Tham số | Mặc định | Mô tả |
|---------|----------|--------|
| beam_width | 20 | Beam width cho subspace search. |
| exp_factor | 20 | Số candidate mở rộng mỗi bước beam. |
| max_depth | 1 | Độ sâu tối đa subspace (số bộ lọc). |
| w_llm | 0.5 | Trọng số cho cột do LLM gợi ý (khi có LLM). |
| run_subspace_search | True | Bật/tắt subspace search. |
| max_insights_per_card | 3 | Số insight basic tối đa mỗi card. |
| max_overall_per_key | 1 | Mỗi (question, B, M, pattern) giữ tối đa N insight overall. |
| max_subspace_per_key | 2 | Mỗi nhóm giữ tối đa N insight subspace. |
| max_insights_per_question | 2 | Mỗi question chỉ xuất tối đa N insight (giảm trùng). |

---

## 6. CLI (run_isgen.py)

```bash
python run_isgen.py --csv <CSV> --insight-cards <JSON> --output <OUT> [--plot-dir <DIR>] [options]
```

| Option | Mặc định | Mô tả |
|--------|----------|--------|
| --csv | (bắt buộc) | Đường dẫn file CSV. |
| --insight-cards | insight_cards.json | File Insight Cards (output QUGEN). |
| --output | insights_summary.json | File output Insight Summary. |
| --plot-dir | None | Thư mục lưu đồ thị PNG. |
| --beam-width | 20 | Beam width. |
| --exp-factor | 20 | Expansion factor. |
| --max-depth | 1 | Max subspace depth. |
| --no-subspace | | Chỉ chạy basic insight, không subspace. |
| --max-overall-per-key | 1 | Giới hạn insight overall mỗi nhóm. |
| --max-subspace-per-key | 2 | Giới hạn insight subspace mỗi nhóm. |
| --max-insights-per-question | 2 | Giới hạn số insight mỗi question. |

**Ví dụ:** Chạy đầy đủ subspace (có gọi API), giảm trùng:

```bash
python run_isgen.py --csv data/transactions.csv --insight-cards insight_cards.json --output insights_summary.json --plot-dir plots
```

---

## 7. File và module (code)

| File | Chức năng |
|------|-----------|
| `ifq/isgen/models.py` | Insight(B,M,S,P), Subspace. |
| `ifq/isgen/views.py` | view(D,B,M), parse measure, apply S, **resolve_column**, **resolve_card_columns**. |
| `ifq/isgen/scoring.py` | SCOREFUNC và ngưỡng T cho từng pattern. |
| `ifq/isgen/basic_insight.py` | Basic insight từ card. |
| `ifq/isgen/subspace_search.py` | Algorithm 1 (beam search). |
| `ifq/isgen/llm_filter_columns.py` | LLM gợi ý cột lọc (gọi API thật). |
| `ifq/isgen/nl_explanation.py` | Mô tả NL theo template (không gọi LLM). |
| `ifq/isgen/plotting.py` | Vẽ đồ thị theo pattern. |
| `ifq/isgen/pipeline.py` | Luồng đầy đủ: collect → dedup → explain + plot. |
| `run_isgen.py` | CLI. |

---

## 8. Input / Output

| | Mô tả |
|--|--------|
| **Input** | CSV (delimiter/decimal tự detect); file JSON Insight Cards (question, reason, breakdown, measure). |
| **Output** | File JSON Insight Summary: danh sách `{ question, explanation, plot_path, insight }`; tùy chọn thư mục PNG. |

Chi tiết format: [ISGEN_INPUT_OUTPUT.md](ISGEN_INPUT_OUTPUT.md).
