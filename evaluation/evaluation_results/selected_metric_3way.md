# Selected Metrics: QUIS vs Baseline vs ONLYSTATS

## Core & Efficiency

- **1. Faithfulness**
  - Group: Core & Efficiency
  - QUIS: 100.0%
  - Baseline: 100.0%
  - ONLYSTATS: 100.0%
  - Winner vs Baseline: Tie
  - Winner vs ONLYSTATS: Tie
  - Vai trò trong paper: Sanity floor
  - Công thức: `faithfulness_score = verified_count / total_count`
  - Ý nghĩa khoa học: Tỷ lệ insight có view-values tính lại đúng với dữ liệu gốc.
  - Kết luận cho bài báo: Điều kiện tiên quyết: cả 3 pipeline đều grounded 100% → mọi chênh lệch ở metric khác phản ánh chất lượng intent/question.

- **2. Statistical Significance (Overall)**
  - Group: Core & Efficiency
  - QUIS: 74.7%
  - Baseline: 60.3%
  - ONLYSTATS: 92.0%
  - Winner vs Baseline: QUIS
  - Winner vs ONLYSTATS: ONLYSTATS†
  - Vai trò trong paper: QuGen vs Baseline
  - Công thức: `Significance Rate = (1/N) * Σ 1(p_i < alpha)` với alpha = 0.05; `pattern_avg_significance = mean(pattern_rates)`
  - Pattern-specific formulas:
    - OUTSTANDING_VALUE: `z = (max - μ) / σ`, `p = 1 - Φ(z)`, `score = z / (z + 1)`
    - TREND: `score = |Kendall τ|` từ Mann-Kendall test
    - ATTRIBUTION: `Cramér's V = sqrt(χ² / (n * (min(r,c) - 1)))`
    - DISTRIBUTION_DIFFERENCE: KS statistic
  - Ý nghĩa khoa học: Pattern-averaged significance (trung bình 4 pattern) để loại bias pattern-mix. QUIS +14.4pp vs Baseline. ONLYSTATS cao vì exhaustive enumeration tìm toàn bộ (B,M) có significance (upper bound thống kê).
  - Kết luận cho bài báo: QUIS beat Baseline +14.4pp: QuGen đặt hypothesis có ý nghĩa thống kê hơn LLM không có cấu trúc. † ONLYSTATS 92% là expected upper bound của exhaustive search — không phản ánh chất lượng phân tích, chỉ cho thấy systematic enumeration tìm được nhiều pattern significant hơn.

- **2b. Pattern Coverage**
  - Group: Core & Efficiency
  - QUIS: 4/4 (100%)
  - Baseline: 3/4 (75%)
  - ONLYSTATS: 4/4 (100%)
  - Winner vs Baseline: QUIS
  - Winner vs ONLYSTATS: Tie
  - Vai trò trong paper: QuGen vs Baseline
  - Công thức: `pattern_coverage = len(covered) / len(ALL_PATTERNS)` với covered = patterns có ≥1 structurally valid insight
  - Validity rules:
    - OUTSTANDING_VALUE: no breakdown constraint
    - TREND: breakdown must be Temporal
    - ATTRIBUTION: breakdown must be Categorical or ID
    - DISTRIBUTION_DIFFERENCE: breakdown must be Categorical or ID
  - Ý nghĩa khoa học: Số pattern có ≥1 insight với breakdown đúng kiểu / 4. Baseline thiếu ATTRIBUTION vì toàn bộ ATTRIBUTION insights dùng numeric breakdown.
  - Kết luận cho bài báo: QUIS 4/4 vs Baseline 3/4: QuGen đảm bảo đặt câu hỏi đúng trên cả 4 analytical pattern. ONLYSTATS cũng 4/4 nhờ schema enumeration — cho thấy schema awareness (dù từ QuGen hay enumeration) đủ để đảm bảo coverage.

## Intent Layer Quality

- **12. Structural Validity Rate**
  - Group: Intent Layer Quality
  - QUIS: 100.0% (97/97)
  - Baseline: 43.0% (37/86)
  - ONLYSTATS: 100.0% (93/93)
  - Winner vs Baseline: QUIS
  - Winner vs ONLYSTATS: Tie
  - Vai trò trong paper: QuGen vs Baseline (core evidence)
  - Công thức: `SVR = valid_total / total`
  - Ý nghĩa khoa học: % insights có breakdown type đúng cho pattern (TREND→Temporal ATTRIBUTION/DD→Categorical). Metric mới — gap lớn nhất trong toàn evaluation +57pp QUIS vs Baseline.
  - Kết luận cho bài báo: QUIS 100% vs Baseline 43%: LLM không có cấu trúc vi phạm semantic constraint ở 57% insights. ONLYSTATS cũng 100% vì IsGen enforce TREND rule nội tại. Kết luận: SVR phân biệt *schema-aware* (QUIS ONLYSTATS) khỏi *unstructured LLM* (Baseline) — QuGen là một cách đạt schema awareness, không phải cách duy nhất.

- **12a. SVR — ATTRIBUTION**
  - Group: Intent Layer Quality
  - QUIS: 100% (24/24)
  - Baseline: 0% (0/11)
  - ONLYSTATS: 100% (15/15)
  - Winner vs Baseline: QUIS
  - Winner vs ONLYSTATS: Tie
  - Vai trò trong paper: QuGen vs Baseline (strongest evidence)
  - Công thức: `valid_rate = valid_count / total_count` với valid = breakdown là Categorical hoặc ID
  - Ý nghĩa khoa học: ATTRIBUTION cần categorical breakdown. Baseline 0%: toàn bộ 11 insights dùng Total Sales / Units Sold làm B — vi phạm hoàn toàn.
  - Kết luận cho bài báo: Bằng chứng cực đoan nhất: Baseline 0% không phải vì thiếu insights, mà vì LLM luôn chọn numeric breakdown cho ATTRIBUTION. QuGen (và schema enumeration) hiểu ATTRIBUTION cần descriptor column, không phải numeric target.

- **12a. SVR — TREND**
  - Group: Intent Layer Quality
  - QUIS: 100% (3/3)
  - Baseline: 38% (15/39)
  - ONLYSTATS: 100% (10/10)
  - Winner vs Baseline: QUIS
  - Winner vs ONLYSTATS: Tie
  - Vai trò trong paper: QuGen vs Baseline
  - Công thức: `valid_rate = valid_count / total_count` với valid = breakdown là Temporal (datetime)
  - Ý nghĩa khoa học: TREND cần temporal breakdown. 24/39 baseline TREND insights dùng Retailer Region (categorical) thay vì Invoice Date.
  - Kết luận cho bài báo: Baseline 38%: QuGen hiểu TREND yêu cầu trục thời gian → chọn Invoice Date. ONLYSTATS 100% nhờ IsGen filter nội tại (basic_insight.py skip TREND cho non-temporal column).

- **10c. BM — Actionability**
  - Group: Intent Layer Quality
  - QUIS: 1.000
  - Baseline: 0.677
  - ONLYSTATS: 1.000
  - Winner vs Baseline: QUIS
  - Winner vs ONLYSTATS: Tie
  - Vai trò trong paper: QuGen vs Baseline
  - Công thức: `actionability = len(cat_pairs) / len(pairs)` với cat_pairs = pairs có breakdown là Categorical/Temporal/ID
  - Ý nghĩa khoa học: % cặp (B M) mà B là categorical — breakdown cho insight có thể hành động (subgroup discovery đúng nguyên tắc).
  - Kết luận cho bài báo: QUIS và ONLYSTATS đều 100%. Baseline 67.7%: LLM sinh numeric breakdown (Total Sales Units Sold) làm B — không actionable. Cho thấy bất kỳ approach nào tôn trọng schema classification đều đạt actionability cao — QuGen không cần thiết cho metric này.

- **11c. Question–Insight Alignment**
  - Group: Intent Layer Quality
  - QUIS: 0.563
  - Baseline: 0.576
  - ONLYSTATS: —
  - Winner vs Baseline: Tie
  - Winner vs ONLYSTATS: —
  - Vai trò trong paper: Control (loại trừ giải thích thay thế)
  - Công thức: `Align_{Q-I} = mean_i cosine(Embed(q_i), Embed(insight_string_i))` với insight_string = "breakdown | measure | pattern | condition"
  - Ý nghĩa khoa học: Cosine similarity trung bình giữa embedding câu hỏi và embedding insight. Đo xem IsGen có thực sự trả lời câu hỏi QuGen đặt ra không. Không áp dụng cho ONLYSTATS (template alignment là artifact).
  - Kết luận cho bài báo: Control metric: gap QUIS–Baseline chỉ 0.013 (Tie) → IsGen execute câu hỏi trung thực ở cả hai pipeline. Kết luận: chênh lệch ở SVR/Subspace/Significance thực sự đến từ QuGen, không phải IsGen tốt hơn.

- **11e. Reason–Insight Coherence**
  - Group: Intent Layer Quality
  - QUIS: 0.571
  - Baseline: 0.510
  - ONLYSTATS: —
  - Winner vs Baseline: QUIS
  - Winner vs ONLYSTATS: —
  - Vai trò trong paper: QuGen reasoning quality (QUIS vs Baseline only)
  - Công thức: `Coh_{R-I} = mean_i cosine(Embed(reason_i), Embed(insight_string_i))`
  - Ý nghĩa khoa học: Cosine similarity giữa trường reason và insight. reason là output đặc trưng của QuGen. Không áp dụng cho ONLYSTATS (template reason là artifact).
  - Kết luận cho bài báo: QUIS +0.061 vs Baseline: reason của QuGen grounded bám sát slice/pattern cụ thể, không phải template chung. Đây là proxy cho *quality of reasoning* của QuGen — một khả năng mà neither Baseline nor ONLYSTATS có được.

## Subspace Deep-dive

- **7. Subspace Rate**
  - Group: Subspace Deep-dive
  - QUIS: 45/97 (46.4%)
  - Baseline: 32/86 (37.2%)
  - ONLYSTATS: 33/93 (35.5%)
  - Winner vs Baseline: QUIS
  - Winner vs ONLYSTATS: QUIS ★★★
  - Vai trò trong paper: Ablation key metric — QuGen unique contribution
  - Công thức: `subspace_rate = insights_with_subspace / total_insights` với subspace = list of (column, value) filter conditions
  - Ý nghĩa khoa học: % insights có subspace filter. Metric DUY NHẤT QUIS vượt cả Baseline lẫn ONLYSTATS. +10.9pp vs ONLYSTATS +9.2pp vs Baseline.
  - Kết luận cho bài báo: ★★★ Contribution cốt lõi của QuGen: sinh câu hỏi conditional ('trong nhóm X…') → IsGen khám phá nhiều subspace insight hơn. ONLYSTATS (pure enumeration) không có khả năng này — question template không mang conditional context. Đây là bằng chứng thực nghiệm rõ ràng nhất cho giá trị của QuGen so với ablation.
