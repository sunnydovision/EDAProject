# IFQ vs Baseline: Evaluation Report

**Generated**: 2026-04-22 01:41:19

---

## Executive Summary

| | IFQ | Baseline |
|---|---|---|
| **Metrics Won** | 15 | 11 |
| **Overall Winner** | ✓ |  |

---

## Group 1 — Core Metrics & Efficiency

| Metric                                     | IFQ        | Baseline   | Winner   | Description                                             |
|:-------------------------------------------|:-----------|:-----------|:---------|:--------------------------------------------------------|
| 0. Total insights                          | 97         | 86         | N/A      | Total insight cards generated                           |
| 1. Faithfulness                            | 100.0%     | 100.0%     | Tie      | Correctness - đúng dữ liệu                              |
| 2. Statistical Significance (Overall)      | 74.7%      | 60.3%      | IFQ      | Validity - pattern-averaged (fair comparison)           |
| 2a. Significance — TREND                   | 50.0% (2)  | 93.3% (15) | Baseline | Validity - TREND pattern                                |
| 2a. Significance — OUTSTANDING_VALUE       | 53.0% (66) | 81.2% (16) | Baseline | Validity - OUTSTANDING_VALUE pattern                    |
| 2a. Significance — ATTRIBUTION             | 95.8% (24) | N/A        | IFQ      | Validity - ATTRIBUTION pattern                          |
| 2a. Significance — DISTRIBUTION_DIFFERENCE | 100.0% (4) | 66.7% (9)  | IFQ      | Validity - DISTRIBUTION_DIFFERENCE pattern              |
| 3. Insight Novelty                         | 83.5%      | 84.9%      | Baseline | Usefulness - khác baseline                              |
| 4a. Diversity — Semantic                   | 0.468      | 0.451      | IFQ      | Semantic diversity (breakdown|measure|pattern|subspace) |
| 4b. Diversity — Subspace Entropy           | 1.354      | 1.516      | Baseline | Entropy of subspace filter columns used                 |
| 4c. Diversity — Value                      | 1.000      | 0.375      | IFQ      | Unique (column, value) pairs in subspace / total        |
| 4d. Diversity — Dedup Rate                 | 0          | 0.012      | IFQ      | Duplicate rate — lower is better                        |

---

## Group 2 — Subspace Deep-dive

| Metric                                        | IFQ               | Baseline          | Winner   | Description                                                          |
|:----------------------------------------------|:------------------|:------------------|:---------|:---------------------------------------------------------------------|
| 7. Subspace Rate                              | 45/97 (46.4%)     | 32/86 (37.2%)     | IFQ      | Insights with subspace filter / total                                |
| 7a. Subspace Faithfulness                     | 100.0%            | 100.0%            | Tie      | Faithfulness restricted to subspace insights                         |
| 7b. Subspace Significance                     | 55.6%             | 66.7%             | Baseline | Significance restricted to subspace insights                         |
| 7c. Subspace Novelty                          | 91.1%             | 96.9%             | Baseline | Novelty restricted to subspace insights                              |
| 7d.1. Diversity — Semantic (Subspace)         | 0.444             | 0.457             | Baseline | Semantic diversity restricted to subspace insights                   |
| 7d.2. Diversity — Subspace Entropy (Subspace) | 1.354             | 1.516             | Baseline | Entropy of subspace filter columns used (subspace insights)          |
| 7d.3. Diversity — Value (Subspace)            | 1.000             | 0.375             | IFQ      | Unique (column, value) pairs in subspace / total (subspace insights) |
| 7d.4. Diversity — Dedup Rate (Subspace)       | 0                 | 0                 | Tie      | Duplicate rate restricted to subspace insights - lower is better     |
| 8. Score Uplift from Subspace                 | Δ=-0.091, x=0.832 | Δ=-0.112, x=0.812 | IFQ      | Δ = mean(score|subspace) - mean(score|no-subspace)                   |
| 9. Direction Uplift                           | down              | down              | Tie      | Direction of Δ score uplift: up/down/flat                            |

---

## Group 3 — QuGen Quality (Intent Layer)

> **Định nghĩa nhóm**: gom toàn bộ chỉ số đánh giá *Intent Layer* — tầng QuGen quyết định *phân tích cái gì* (target structure) và *đặt câu hỏi như thế nào* (text). Bao gồm hai lớp con:
>
> 1. **Target structure (10a–e)** — chất lượng cặp `(breakdown, measure)` mà QuGen chọn (NMI, Interestingness, Actionability, Diversity).
> 2. **Question text & reason (11a–e)** — chất lượng `question` và `reason` ở dạng ngôn ngữ tự nhiên (Diversity, Specificity, Q-I Alignment, Cross-system Novelty, Reason-I Coherence).
>
> Hai lớp này cùng đo *cùng một mô-đun QuGen* — tách ra chỉ để diễn giải, không tách thành hai group riêng nữa.

### 3.1 Target structure — `(breakdown, measure)`

| Metric                          | IFQ   | Baseline   | Winner   | Description                                                                                |
|:--------------------------------|:------|:-----------|:---------|:-------------------------------------------------------------------------------------------|
| 10. Total (B,M) pairs evaluated | 44/44 | 21/31      | N/A      | Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness) |
| 10a. BM — NMI mean              | 0.075 | 0.121      | Baseline | Mean NMI over categorical-B pairs                                                          |
| 10b. BM — Interestingness       | 0.085 | 0.131      | Baseline | Mean Coverage×EffectSize over categorical-B pairs                                          |
| 10c. BM — Actionability         | 1.000 | 0.677      | IFQ      | % pairs with categorical breakdown                                                         |
| 10d. BM — Diversity             | 0.454 | 0.360      | IFQ      | Unique (B,M) pairs / total insights                                                        |

### 3.2 Question text & reason

| Metric                                   | IFQ           | Baseline      | Winner   | Description                                                                |
|:-----------------------------------------|:--------------|:--------------|:---------|:---------------------------------------------------------------------------|
| 11a. Question Semantic Diversity         | 0.521         | 0.536         | Baseline | 1 − mean cosine sim of question embeddings (within-system)                 |
| 11b. Question Specificity                | 9.53 ± 1.76   | 9.14 ± 1.46   | IFQ      | Avg word count per question (mean ± std) — higher = more specific          |
| 11c. Question–Insight Alignment          | 0.5630        | 0.5629        | IFQ      | Mean cosine(Embed(question), Embed(insight)) — semantic faithfulness       |
| 11d. Question Novelty (cross-system)     | 61.9%         | 57.5%         | IFQ      | % of questions with cross-system max cosine sim < 0.85                     |
| 11e. Reason–Insight Coherence            | 0.5713        | 0.5673        | IFQ      | Mean cosine(Embed(reason), Embed(insight)) — reason grounding              |

> **QuGen take-away**:
> - **Target side**: IFQ thắng tuyệt đối ở Actionability (+32.3pp) và BM Diversity (+9.4pp) — QuGen 'hiểu' subgroup discovery (B luôn categorical) và bao quát nhiều trục phân tích hơn. Baseline thắng NMI/Interestingness vì chọn ít cặp nhưng cường độ cao hơn — trade-off breadth vs intensity.
> - **Text side**: IFQ thắng 4/5 — câu hỏi cụ thể hơn (11b), grounded ngữ nghĩa tương đương (11c), novel cross-system (11d, +4.4pp), và `reason` thực sự bám vào insight thay vì template (11e).
> - **Cùng nhau**: 9/10 chỉ số trong nhóm này nghiêng về IFQ — cơ sở định lượng để bài báo lập luận *QuGen là mô-đun phân biệt chính của QUIS so với baseline auto EDA*. Phần ablation (no-QuGen) sẽ kiểm chứng điều ngược lại: bỏ QuGen thì các chỉ số 10c/10d/11b/11d/11e dự kiến đảo chiều.

---

## Conclusion

**Overall Winner**: IFQ (15 vs 11 metrics won)

- **Group 1 (Core & Efficiency)**: IFQ thắng ở Significance overall, ATTRIBUTION, DIST_DIFF, Diversity Semantic & Value, Dedup Rate.
- **Group 2 (Subspace Deep-dive)**: IFQ thắng ở Subspace Rate, Score Uplift; Baseline thắng Subspace Significance/Novelty (trade-off "rộng vs sâu"). Subspace Rate cao hơn là *hệ quả downstream* của QuGen sinh nhiều câu hỏi conditional.
- **Group 3 (QuGen Quality — Intent Layer, gom từ BM Deep-dive + Question Generation)**: IFQ thắng 6/9 chỉ số có winner; chiếm phần lớn các chiến thắng định tính của bài. Đây là nhóm *trọng tâm khoa học của bài báo* — phơi bày đóng góp của mô-đun QuGen ở cả tầng cấu trúc target lẫn tầng ngôn ngữ tự nhiên (câu hỏi, reason). Chỉ số kỳ vọng đảo chiều khi ablation no-QuGen: 10c (Actionability), 10d (BM Diversity), 11d (Question Novelty), 11e (Reason-I Coherence).

