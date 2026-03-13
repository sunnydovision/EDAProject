# Báo cáo: Module ISGEN – Insight Generation

**Tham chiếu:** QUIS (arXiv:2410.10270), Section 3.2, Figure 1 (ISGen), Appendix A (scoring), Appendix B (plotting).

---

## 1. Mục tiêu

Module **ISGEN** nhận **Insight Cards** (từ QUGEN) và **bảng dữ liệu**, tìm các insight thống kê (pattern) trên view (breakdown B, measure M, subspace S), rồi sinh **mô tả ngôn ngữ tự nhiên** và **đồ thị** theo từng loại pattern. Không cần huấn luyện trước; tham số scoring và ngưỡng theo bài báo.

---

## 2. Pipeline ISGEN (theo sơ đồ và bài báo)

1. **Insight Cards DB** (Reason, Question, Breakdown, Measure) + **DataFrame** → input.
2. **Basic insight:** Với mỗi card, tính view(D, B, M), áp dụng pattern (Trend, Outstanding Value, Attribution); nếu score > ngưỡng → Insight(B, M, φ, P).
3. **Subspace search (Algorithm 1):** Beam search: mở rộng subspace bằng bộ lọc (cột X, giá trị y). Cột X có thể do LLM gợi ý (w_LLM); y lấy mẫu theo P(y) ∝ log(1+N(y)). Chỉ giữ subspace có score > ngưỡng.
4. **If interesting:** Chỉ các insight đạt ngưỡng được đưa sang bước sau.
5. **LLM (NL explanation):** Mô tả bằng ngôn ngữ tự nhiên (trong code: template theo pattern).
6. **Plotting (rule-based):** Trend → scatter + trend line; Outstanding Value / Attribution → bar; Distribution Difference → pie (Appendix B).
7. **Insight Summary:** Danh sách insight kèm explanation và đường dẫn file đồ thị (nếu dùng `--plot-dir`).

---

## 3. Định nghĩa Insight và Scoring

- **Insight(B, M, S, P):** B = breakdown, M = measure (agg(C)), S = subspace (bộ lọc), P = pattern.
- **Scoring (Appendix A):** Trend = 1 − p_value(Mann-Kendall), ngưỡng 0,95; Outstanding Value = vmax1/vmax2, ngưỡng 1,4; Attribution = max/Σ, ngưỡng 0,5; Distribution Difference = JSD, ngưỡng 0,2 (chỉ khi measure = COUNT).

---

## 4. Triển khai và cách chạy

- **Code:** `quis/isgen/` (models, views, scoring, basic_insight, subspace_search, llm_filter_columns, nl_explanation, plotting, pipeline).
- **CLI:** `run_isgen.py --csv ... --insight-cards insight_cards.json --output insights_summary.json [--plot-dir plots] [--no-subspace]`.
- **Input:** CSV + file JSON Insight Cards (output của QUGEN).
- **Output:** File JSON Insight Summary; tùy chọn thư mục chứa đồ thị PNG.

Tài liệu chi tiết: [ISGEN_PIPELINE.md](ISGEN_PIPELINE.md), [ISGEN_INPUT_OUTPUT.md](ISGEN_INPUT_OUTPUT.md).
