# QUGEN Pipeline – Các bước theo bài báo QUIS

Tài liệu này liệt kê các bước của **Question Generation (QUGEN)** theo bài báo *QUIS: Question-guided Insights Generation for Automated Exploratory Data Analysis* (Figure 1, Section 3.1).

---

## 1. Định nghĩa Insight Card (đầu ra của QUGEN)

Mỗi **Insight Card** gồm 4 thành phần (Figure 2):

| Thành phần | Mô tả |
|------------|--------|
| **REASON** | Lý do / rationale đằng sau câu hỏi, giúp phân tích sâu hơn. |
| **QUESTION** | Câu hỏi tự nhiên hướng dẫn phân tích dữ liệu. |
| **BREAKDOWN** | Thuộc tính breakdown B – chiều so sánh (ví dụ: Year, Department). |
| **MEASURE** | Đại lượng đo M – dạng agg(C), ví dụ MEAN(Performance), COUNT(*). |

*Reason* được QUGEN dùng để mở rộng coverage; *Question*, *Breakdown*, *Measure* dùng cho cả QUGEN và ISGEN.

---

## 2. Input của QUGEN

- **Schema bảng**: tên cột, kiểu dữ liệu (và mô tả nếu có).
- **Basic statistics (thống kê cơ bản)**: mô tả ngắn bằng ngôn ngữ tự nhiên, sinh bởi:
  - Prompt LLM (Figure 7) để sinh các câu hỏi thống kê cơ bản;
  - Chuyển sang SQL, chạy trên dataset, rồi chuyển kết quả sang mô tả ngôn ngữ tự nhiên.
- **Few-shot examples**: schema của bảng mẫu + Insight Cards mẫu (trong prompt).
- (Tùy chọn) **Insight Cards từ các iteration trước** dùng làm in-context examples cho iteration tiếp theo.

---

## 3. Các bước pipeline QUGEN (Section 3.1.2)

### Bước 1: Tạo prompt

- Mô tả nhiệm vụ phân tích (high-level).
- Hướng dẫn chi tiết để sinh Insight Card (xem schema + basic statistics).
- Few-shot: bảng schema mẫu + Insight Cards mẫu.
- Schema bảng cần phân tích + **natural language stats** (thống kê cơ bản đã mô tả bằng ngôn ngữ tự nhiên).
- (Từ iteration 2 trở đi) Thêm một **tập con Insight Cards** đã sinh ở các iteration trước làm in-context examples.

### Bước 2: Gọi LLM và lấy mẫu

- Prompt LLM (theo template Figure 6) để sinh **nhiều Insight Cards**.
- **Sampling**: lấy **s** mẫu (samples) với **temperature t** (trong bài: s=3, t=1.1).
- Mỗi mẫu chứa **n** Insight Cards (số lượng có thể dao động do giới hạn token).

### Bước 3: Parse output

- Parse câu trả lời của LLM để trích ra từng Insight Card (REASON, QUESTION, BREAKDOWN, MEASURE).

### Bước 4: Lọc (filtering)

1. **Schema relevance**: Loại Insight Card có **question** không liên quan ngữ nghĩa đến schema bảng.  
   - Dùng **semantic similarity** với mô hình **all-MiniLM-L6-v2** (Sentence Transformers).

2. **Deduplication**: Loại **trùng lặp** dựa trên độ tương đồng ngữ nghĩa giữa các cặp question.

3. **Simple-question filter**: Loại câu hỏi **đơn giản / hời hợt**.  
   - Chuyển question sang SQL, chạy trên dataset;  
   - Nếu truy vấn **chỉ trả về 1 dòng** thì loại câu hỏi đó (chỉ giữ câu hỏi đủ “sâu” để phân tích).

### Bước 5: Cập nhật pool và lặp

- Thêm các Insight Card còn lại sau lọc vào **pool** (Insight Cards DB trong Figure 1).
- Chọn **subset** (ví dụ 6 thẻ) từ pool làm **in-context examples** cho iteration tiếp theo.
- Lặp lại từ **Bước 1** cho đến đủ số **iterations** (ví dụ 10).

### Bước 6: Output

- **Output** của QUGEN: **tập Insight Cards** tích lũy qua tất cả các iteration (ví dụ sau 10 iterations).
- Tập này được dùng làm đầu vào cho **ISGEN** (Insight Generation).

---

## 4. Mô hình sử dụng (theo bài báo)

| Thành phần | Mô hình / Công cụ |
|------------|--------------------|
| Sinh Insight Cards & basic stats questions | **LLM**: Llama-3-70b-instruct |
| Semantic similarity (relevance + dedup) | **all-MiniLM-L6-v2** (Sentence Transformers) |

---

## 5. Tham số thí nghiệm (Appendix D.2 – QUGEN)

- **LLM**: Llama-3-70b-instruct  
- **Temperature** t = 1.1  
- **Số samples mỗi iteration** s = 3  
- **Số iterations** n = 10  
- **Số in-context examples** = 6  

---

## 6. Input / Output tóm tắt

| | Mô tả |
|--|--------|
| **Input** | Dataset (hoặc schema + bảng dữ liệu), cấu hình (s, t, n, số in-context examples). |
| **Output** | Danh sách **Insight Cards**, mỗi card gồm: REASON, QUESTION, BREAKDOWN, MEASURE. |

Các Insight Cards này sau đó được đưa vào **ISGEN** để sinh insight (pattern, subspace, visualization) tương ứng.
