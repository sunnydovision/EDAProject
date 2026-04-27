# Báo cáo: Module QUGEN – Tạo sinh câu hỏi (Insight Cards)

**Môn học:** [Điền tên môn học]  
**Tham chiếu:** QUIS – Question-guided Insights Generation for Automated Exploratory Data Analysis (arXiv:2410.10270).

---

## 1. Mục tiêu

Module **QUGEN (QUGEN)** thuộc hệ thống QUIS, có nhiệm vụ **tự động sinh tập câu hỏi phân tích** từ dữ liệu bảng (schema + thống kê cơ bản), không cần mục tiêu định sẵn hay bộ ví dụ soạn tay. Mỗi câu hỏi được đóng gói dưới dạng **Insight Card** (Question, Reason, Breakdown, Measure), dùng làm đầu vào cho bước sinh insight thống kê (ISGEN) sau này.

---

## 2. Pipeline tạo sinh câu hỏi (Insight Cards)

Luồng xử lý gồm các bước chính sau, tương ứng với sơ đồ *Pipeline tạo sinh câu hỏi (Insight Cards)*:

1. **Chuẩn bị Data Semantics (Prepare Data Semantics)**  
   Từ bảng dữ liệu (CSV hoặc schema JSON), hệ thống suy ra schema (tên cột, kiểu dữ liệu) và tạo **natural language stats**: gọi LLM với prompt Figure 7 để sinh câu hỏi thống kê cơ bản trong tag `[STAT]...[/STAT]`, sau đó chuyển thành mô tả ngắn (thống kê theo cột hoặc danh sách câu hỏi). Dữ liệu semantics này được dùng cố định cho toàn bộ vòng lặp.

2. **Build prompt**  
   Ở mỗi vòng lặp, prompt được xây từ: (i) mô tả nhiệm vụ EDA và hướng dẫn sinh Insight Card (Figure 6), (ii) few-shot examples (schema mẫu + Insight Card mẫu), (iii) schema bảng cần phân tích và chuỗi natural language stats, (iv) từ vòng 2 trở đi — một tập con Insight Card lấy từ **Pool** làm in-context.

3. **Prompts → LLM Generate Insight Cards**  
   Prompt được gửi tới LLM (OpenAI Responses API hoặc Chat Completions). LLM sinh nhiều Insight Card trong một lần (samples), mỗi card có format REASON, QUESTION, BREAKDOWN, MEASURE và được bọc trong tag `[INSIGHT]...[/INSIGHT]`.

4. **Insight Card → Filter Insight Cards**  
   Output của LLM được parse thành danh sách Insight Card. Sau đó áp dụng ba bước lọc theo thứ tự: (i) **Schema relevance** — loại câu hỏi không liên quan schema (embedding all-MiniLM-L6-v2, ngưỡng cosine similarity); (ii) **Deduplication** — loại trùng theo độ tương đồng câu hỏi; (iii) **Simple-question filter** — loại câu quá ngắn hoặc dạng “what is the count of…” (heuristic, hoặc theo số dòng trả về nếu có run_query_fn).

5. **Filter → Pool**  
   Các Insight Card còn lại được đưa vào **Pool**. Pool được deduplicate và tích lũy qua các vòng.

6. **Pool → Pick Few-shot Example**  
   Từ pool, chọn ngẫu nhiên một subset (ví dụ 6 card) cùng schema bảng hiện tại, tạo thành block in-context **đặt trước** few-shot mặc định (Employee, Sales).

7. **Feedback to Prompts**  
   Block in-context này được đưa lại vào bước Build prompt của vòng tiếp theo, tạo vòng lặp tinh chỉnh: càng về sau LLM càng có thêm ví dụ từ chính dữ liệu đang phân tích, giúp sinh câu hỏi đa dạng và bám schema hơn.

Sơ đồ tổng thể: *Prepare Data Semantics → Build prompt → Prompts → LLM Generate Insight Cards → Insight Card → Filter Insight Cards → Pool → Pick Few-shot Example → (quay lại) Prompts.*

---

## 3. Định dạng Insight Card

Mỗi Insight Card gồm bốn trường:

| Trường      | Ý nghĩa |
|-------------|---------|
| **question** | Câu hỏi tự nhiên hướng dẫn phân tích dữ liệu. |
| **reason**   | Lý do / rationale của câu hỏi. |
| **breakdown**| Chiều so sánh (tên cột), ví dụ: Năm, Khu vực, Phân khúc. |
| **measure**  | Đại lượng đo, dạng agg(C): MEAN(Thành Tiền), SUM(Doanh thu), COUNT(*), … |

Breakdown và Measure sau này được ISGEN dùng để tính view (nhóm theo breakdown, tính measure) và tìm pattern (trend, outlier, attribution, …).

---

## 4. Công nghệ và triển khai

- **LLM:** OpenAI (Responses API mặc định, model `gpt-5-nano`; hoặc Chat Completions `gpt-4o-mini`). Cấu hình qua biến môi trường: `OPENAI_API_KEY`, `OPENAI_API_BASE`, `QUGEN_LLM_MODEL`, `OPENAI_USE_RESPONSES_API`.
- **Semantic similarity:** Sentence Transformers `all-MiniLM-L6-v2` (embedding câu hỏi và schema cho lọc relevance và dedup).
- **Cấu trúc code:** `quis/qugen/` gồm `pipeline.py` (vòng lặp QUGEN), `prompts.py` (Figure 6, 7), `stats.py` (BasicStatsGenerator), `parser.py` (parse [INSIGHT]), `filters.py` (relevance, dedup, simple-question), `llm_client.py`, `models.py` (InsightCard, TableSchema), `examples.py` (few-shot mặc định). CLI: `run_qugen.py` (input CSV/schema, output JSON).

Tham số mặc định: số iteration 10, số samples mỗi iteration 3, số in-context examples 6, số câu hỏi yêu cầu mỗi prompt 10; ngưỡng relevance 0,25, dedup 0,85.

---

## 5. Input và Output

- **Input:** (i) Bảng dữ liệu dạng CSV (schema suy từ DataFrame) hoặc file schema JSON; (ii) tùy chọn DataFrame để tạo natural language stats và (nếu mở rộng) simple-question filter; (iii) cấu hình (số iterations, samples, in-context, ngưỡng lọc).
- **Output:** Danh sách Insight Card (question, reason, breakdown, measure), xuất ra file JSON hoặc trả về trong code để ISGEN sử dụng.

---

## 6. Kết luận

Module QUGEN triển khai pipeline tạo sinh câu hỏi theo bài báo QUIS: chuẩn bị data semantics, xây prompt có few-shot và in-context từ pool, dùng LLM sinh Insight Card, lọc theo relevance–dedup–simple question, cập nhật pool và chọn few-shot cho vòng sau. Pipeline vừa khớp với sơ đồ *Pipeline tạo sinh câu hỏi (Insight Cards)* (chuẩn bị semantics → build prompt → LLM → filter → pool → pick few-shot → feedback), vừa phản ánh đúng luồng thực thi trong code và tài liệu `docs/QUGEN_PIPELINE.md`.
