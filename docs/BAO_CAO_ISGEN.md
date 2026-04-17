# Báo cáo: Module ISGEN – Insight Generation

**Tham chiếu:** QUIS (arXiv:2410.10270), Section 3.2, Figure 1 (ISGen), Appendix A (scoring), Appendix B (plotting).

---

## 1. Mục tiêu

Module **ISGEN** nhận **Insight Cards** (từ QUGEN) và **bảng dữ liệu (CSV)**, tìm các insight thống kê (pattern) trên view (breakdown B, measure M, subspace S), **loại bỏ trùng lặp**, rồi sinh **mô tả ngôn ngữ tự nhiên** và **đồ thị** theo từng loại pattern. Không cần huấn luyện trước; tham số scoring và ngưỡng theo bài báo.

---

## 2. Pipeline ISGEN (khớp code hiện tại)

1. **Input:** Insight Cards (JSON) + DataFrame (từ CSV). Mỗi card: Reason, Question, Breakdown, Measure.

2. **Column resolution:** Map tên cột từ card sang tên cột thực trong CSV (`resolve_card_columns` trong `views.py`: exact → normalized → token overlap). Card không map được thì bỏ qua.

3. **Thu thập candidate (chưa vẽ plot):**
   - **Basic insight:** Với mỗi card, tính view(D, B, M), áp dụng pattern (Trend, Outstanding Value, Attribution); nếu score > ngưỡng → thêm vào danh sách candidate.
   - **Subspace search (Algorithm 1):** Beam search mở rộng subspace (bộ lọc cột/giá trị). Cột có thể do LLM gợi ý qua API thật. Chỉ giữ subspace có score > ngưỡng. Pattern dùng: Outstanding Value, Attribution.

4. **Deduplicate (trước khi vẽ plot):**
   - Theo **(question, breakdown, measure, pattern):** mỗi nhóm giữ tối đa 1 overall + 2 subspace (cấu hình được).
   - Theo **question:** mỗi câu hỏi chỉ giữ tối đa N insight (mặc định 2), chọn theo score → giảm trùng câu hỏi trong báo cáo.

5. **Chỉ với insight được giữ:** NL explanation (template), plotting (rule-based), ghi PNG vào `--plot-dir`, đưa vào Insight Summary.

6. **Output:** File JSON Insight Summary (question, explanation, plot_path, insight) và thư mục đồ thị (nếu có `--plot-dir`).

---

## 3. Định nghĩa Insight và Scoring

- **Insight(B, M, S, P):** B = breakdown, M = measure (agg(C)), S = subspace (bộ lọc), P = pattern.
- **Scoring (Appendix A):** Trend = 1 − p_value(Mann-Kendall), ngưỡng 0,95; Outstanding Value = vmax1/vmax2, ngưỡng 1,4; Attribution = max/Σ, ngưỡng 0,5; Distribution Difference = JSD, ngưỡng 0,2 (khi measure = COUNT).

---

## 4. Triển khai và cách chạy

- **Code:** `quis/isgen/` (models, views, scoring, basic_insight, subspace_search, llm_filter_columns, nl_explanation, plotting, pipeline).
- **CLI:**  
  `run_isgen.py --csv <CSV> --insight-cards insight_cards.json --output insights_summary.json [--plot-dir plots] [--no-subspace] [--max-overall-per-key 1] [--max-subspace-per-key 2] [--max-insights-per-question 2]`
- **Input:** CSV + file JSON Insight Cards (output của QUGEN).
- **Output:** File JSON Insight Summary; tùy chọn thư mục đồ thị PNG.

Tài liệu chi tiết pipeline và tham số: [ISGEN_PIPELINE.md](ISGEN_PIPELINE.md), [ISGEN_INPUT_OUTPUT.md](ISGEN_INPUT_OUTPUT.md).
