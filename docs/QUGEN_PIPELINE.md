# QUGEN Pipeline – Theo code thực thi trong project

Tài liệu này mô tả **đúng luồng và chi tiết** của QUGEN theo code trong `ifq/qugen/` (tham chiếu bài báo QUIS, Figure 1 & Section 3.1).

---

## 1. Định nghĩa Insight Card (đầu ra)

Mỗi **Insight Card** có 4 trường (`ifq/qugen/models.py` – `InsightCard`):

| Thành phần | Mô tả |
|------------|--------|
| **question** | Câu hỏi tự nhiên hướng dẫn phân tích. |
| **reason** | Lý do / rationale. |
| **breakdown** | Chiều breakdown B (tên cột). |
| **measure** | Đại lượng M, dạng agg(C), ví dụ MEAN(C), SUM(C), COUNT(*). |

Schema bảng: **TableSchema** (`table_name` + `columns`: list dict `name`, `dtype`, optional `description`).

---

## 2. Input thực tế

- **TableSchema**: từ CSV (hàm `schema_from_dataframe()` trong `models.py`) hoặc từ file JSON schema.
- **DataFrame (tùy chọn)**: nếu có, dùng cho (1) basic stats đơn giản theo cột, (2) `run_query_fn` (hiện tại placeholder trả về 2).
- **Natural language stats**: do **BasicStatsGenerator** (`stats.py`) tạo **một lần** trước vòng lặp:
  - Gọi LLM với prompt Figure 7 → parse câu hỏi trong `[STAT]...[/STAT]`.
  - Nếu có DataFrame: `_compute_simple_stats()` tính theo từng cột (số: min/max/mean; khác: số giá trị duy nhất), tối đa 25 dòng.
  - Nếu không có DataFrame hoặc lỗi: liệt kê tối đa 20 câu hỏi stat dạng bullet.
- **Few-shot**: mặc định từ `examples.py` – 2 cặp (Employee schema + 1 card, Sales schema + 1 card). Từ iteration 2 trở đi thêm **một block** (cùng table_schema + tối đa n card từ pool) **đặt trước** few-shot mặc định (`pipeline.py` – `_select_in_context_examples`).

---

## 3. Luồng pipeline (theo code)

### 3.1 Khởi tạo và chuẩn bị (`pipeline.run()`)

1. **Natural language stats** (một lần):
   - `BasicStatsGenerator.generate(table_schema, df)` → chuỗi NL stats dùng cho mọi iteration.
2. **run_query_fn** (cho simple-question filter):
   - Nếu config không set: dùng `_make_simple_row_count_fn(df)` khi có `df`, hiện tại **luôn trả về 2** (placeholder, không text2sql).
   - Nếu không có `df`: `run_query_fn` là `None` → dùng lọc heuristic.

### 3.2 Mỗi iteration (`run_one_iteration()`)

**Bước 1 – Tạo prompt** (`prompts.build_qugen_prompt()`)

- Nội dung: Task description + Instructions (Figure 6) + "Examples :" + từng block `[EXAMPLE TABLE SCHEMA]` / `[OUTPUT]` (Insight Card) / `[/OUTPUT]` + "Test Dataset :" + schema bảng + "NATURAL LANGUAGE STATS:" + chuỗi NL stats + yêu cầu sinh `num_questions` câu, format REASON/QUESTION/BREAKDOWN/MEASURE trong `[INSIGHT]...[/INSIGHT]`.
- `example_schemas_and_cards`: iteration 1 = few-shot mặc định; từ iteration 2 = **[(table_schema, selected_cards)] + few_shot** (selected_cards = shuffle pool, lấy tối đa `num_in_context_examples`).

**Bước 2 – Gọi LLM**

- `llm.complete_multi(prompt, num_samples=..., temperature=..., max_tokens=2048)`.
- Trong project:
  - **OpenAI Responses API** (mặc định): `client.responses.create(model=..., input=prompt, store=False, max_output_tokens=max(2048, 8192))`; không gửi `temperature` (một số model không hỗ trợ); lấy text từ `response.output_text` hoặc fallback duyệt `response.output` (message + content type `output_text`).
  - **Chat Completions** (khi tắt Responses API): `client.chat.completions.create(messages=..., temperature=..., max_tokens=...)`.
- Số lần gọi = `num_samples_per_iteration`; mỗi lần trả về một chuỗi text.

**Bước 3 – Parse** (`parser.parse_insight_cards_from_text()`)

- Tìm các khối `[INSIGHT]...[/INSIGHT]` (regex, không phân biệt hoa thường).
- Trong mỗi khối: tìm dòng bắt đầu `REASON:`, `QUESTION:`, `BREAKDOWN:`, `MEASURE:` (hoặc chữ thường) → tách giá trị sau dấu `:`.
- Chỉ giữ card có `question` và `measure` khác rỗng.
- Nếu không có tag `[INSIGHT]`: fallback tách theo "Insight Card N" hoặc parse toàn bộ text như một block.

**Bước 4 – Debug (khi parse ra 0 card)**

- Nếu sau parse không có card nào nhưng có `raw_outputs`: ghi `raw_outputs[0]` vào `debug_llm_response.txt` ở thư mục project.

**Bước 5 – Lọc (theo thứ tự trong code)**

1. **Schema relevance** (`filters.filter_by_schema_relevance`):
   - Embedding: **sentence-transformers** `all-MiniLM-L6-v2` (lazy load).
   - Schema text = table_name + tên cột (+ description nếu có). So cosine similarity giữa embedding câu hỏi và schema; giữ card khi similarity ≥ `schema_relevance_threshold` (mặc định 0.25). Nếu không load được model thì bỏ qua bước này.

2. **Deduplication** (`filters.filter_duplicates`):
   - Embedding câu hỏi (cùng model). Với mỗi card, so với các card đã giữ; nếu có similarity ≥ `dedup_similarity_threshold` (mặc định 0.85) thì coi là trùng, bỏ. Giữ card đầu tiên trong mỗi “cụm” trùng.

3. **Simple-question filter** (`filters.filter_simple_questions`):
   - Nếu `run_query_fn` là `None`: dùng **heuristic** (`_filter_simple_heuristic`): loại câu có độ dài < 15 ký tự; loại câu bắt đầu "what is the (total )?(number of|count of) " và độ dài < 60.
   - Nếu có `run_query_fn`: giữ card khi `run_query_fn(question)` > 1 (hoặc None/exception thì vẫn giữ). Trong code hiện tại, `_make_simple_row_count_fn` luôn trả 2 nên mọi card đều được giữ khi dùng df.

**Bước 6 – Cập nhật pool và in-context cho iteration sau**

- `pool.extend(new_cards)`.
- Deduplicate toàn bộ pool với cùng `dedup_similarity_threshold`.
- `in_context = _select_in_context_examples(pool, num_in_context_examples, table_schema)`:
  - Nếu pool rỗng hoặc n ≤ 0: trả về few-shot mặc định.
  - Ngược lại: shuffle pool, lấy tối đa n card → `[(table_schema, selected)] + few_shot`.

### 3.3 Kết thúc

- Sau đủ `num_iterations` vòng: trả về **pool** (danh sách InsightCard). CLI ghi ra file JSON (mỗi phần tử là dict `question`, `reason`, `breakdown`, `measure`).

---

## 4. Tham số và file liên quan (theo code)

| Tham số / hành vi | Vị trí | Giá trị / ghi chú |
|-------------------|--------|--------------------|
| temperature | QUGENConfig, run_qugen --temperature | Mặc định 1.1; với Responses API không gửi lên API. |
| num_samples_per_iteration | QUGENConfig, --samples | Mặc định 3. |
| num_iterations | QUGENConfig, --iterations | Mặc định 10. |
| num_in_context_examples | QUGENConfig, --in-context | Mặc định 6. |
| num_questions_per_prompt | QUGENConfig | Mặc định 10 (số câu yêu cầu trong prompt). |
| schema_relevance_threshold | QUGENConfig, filters | 0.25. |
| dedup_similarity_threshold | QUGENConfig, filters | 0.85. |
| max_tokens (gửi từ pipeline) | run_one_iteration | 2048; client Responses API dùng max_output_tokens = max(2048, 8192). |
| LLM | llm_client.py | Mặc định: OpenAI Responses API, model `gpt-5-nano`; hoặc Chat Completions `gpt-4o-mini`. Điều khiển bởi env OPENAI_USE_RESPONSES_API, QUGEN_LLM_MODEL, OPENAI_API_KEY, OPENAI_API_BASE. |
| Semantic similarity | filters.py | all-MiniLM-L6-v2 (Sentence Transformers). |

---

## 5. Input / Output tóm tắt (theo code)

| | Mô tả |
|--|--------|
| **Input** | **TableSchema** (từ CSV qua `schema_from_dataframe()` hoặc từ JSON) + **DataFrame tùy chọn** (cho basic stats và run_query_fn). Cấu hình: QUGENConfig (s, iterations, in-context, threshold, …). |
| **Output** | Danh sách **InsightCard** (question, reason, breakdown, measure). CLI xuất JSON; module trả về list để ISGEN dùng sau. |

---

## 6. Khác biệt so với mô tả “lý tưởng” trong bài báo

- **Basic stats**: Không có bước “chuyển câu hỏi stat sang SQL, chạy trên dataset, rồi dịch kết quả sang NL”. Code chỉ: LLM sinh câu hỏi [STAT]; NL stats = thống kê đơn giản theo cột (khi có df) hoặc danh sách câu hỏi.
- **Simple-question filter**: Không có text2sql thật. Có `run_query_fn` nhưng `_make_simple_row_count_fn` chỉ trả 2; thực tế đang dùng **heuristic** (độ dài câu, mẫu "what is the number of/count of").
- **LLM**: Project dùng **OpenAI** (Responses API hoặc Chat Completions), không dùng Llama-3-70b trực tiếp; có thể dùng endpoint khác qua OPENAI_API_BASE.
- **Debug**: Khi parse ra 0 card, ghi phản hồi thô vào `debug_llm_response.txt`.

Document này phản ánh đúng code trong `ifq/qugen/` và `run_qugen.py` tại thời điểm review.
