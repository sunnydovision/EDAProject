# QUGEN – Input & Output (theo bài báo)

## Input

| Thành phần | Bắt buộc? | Mô tả |
|------------|-----------|--------|
| **File CSV** (hoặc schema JSON) | Có | Dataset cần phân tích. Từ CSV ta suy **schema** (tên cột, kiểu) và dùng **DataFrame** cho basic stats + lọc câu đơn giản. |
| **LLM API** | Có | Bài báo dùng Llama-3-70b-instruct. Code dùng API tương thích OpenAI: cần biến môi trường `OPENAI_API_KEY` (hoặc `OPENAI_API_BASE` nếu gọi endpoint riêng). |

Từ CSV, pipeline tự làm:
- **Schema**: suy từ tên cột + kiểu dữ liệu (INT/DOUBLE/CHAR).
- **Natural language stats**: LLM được prompt với schema (Figure 7) để sinh câu hỏi thống kê cơ bản; kết quả được dùng làm mô tả thống kê trong prompt chính.
- **Few-shot examples**: dùng sẵn trong code (Employee, Sales).

**Tóm tắt:** Chạy QUGEN chỉ cần **1 file CSV** + **API key LLM** (env). Không cần file config hay schema JSON riêng nếu dùng `--csv`.

- **Chạy QUGEN:** bắt buộc đặt `OPENAI_API_KEY` (hoặc `OPENAI_API_BASE`) vì project chạy với API thật.

## Output

- **File JSON** chứa danh sách **Insight Cards**.
- Mỗi card có 4 trường (Figure 2):
  - `question`: câu hỏi phân tích
  - `reason`: lý do / rationale
  - `breakdown`: chiều breakdown (B)
  - `measure`: đại lượng đo (M), ví dụ MEAN(...), SUM(...)

Output này là đầu vào cho bước **ISGEN** (ISGEN).
