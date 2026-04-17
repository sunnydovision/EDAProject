# IFQ Project - Hướng dẫn chạy cho thành viên mới

README này dành cho thành viên mới clone project và cần chạy được ngay trên máy local.

## Chuẩn bị chung

### 1) Clone và vào project

```bash
git clone <repo-url>
cd EDAProj
```

### 2) Tạo môi trường Python và cài thư viện

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3) Cấu hình biến môi trường

```bash
cp .env.example .env
```

Mở file `.env` và điền:

```env
OPENAI_API_KEY=your-real-key
```


### 4) Dataset mặc định trong repo

- Dataset giao dịch: `data/transactions.csv`
- Dataset Adidas (dùng nhiều trong baseline/evaluation): `data/Adidas_cleaned.csv`

---

## Phần 1 - Chạy project IFQ (chạy app)

Phần này gồm 2 cách thường dùng:
- Cách A: chạy app giao diện Streamlit
- Cách B: chạy pipeline bằng CLI (`Question Generation -> Insight Generation`)

### A. Chạy app giao diện

Từ thư mục gốc project:

```bash
source venv/bin/activate
streamlit run app.py
```

Sau đó mở URL Streamlit (thường là `http://localhost:8501`).

Trong app:
- Tab `Home`: upload CSV và bấm **Generate New Report**
- Tab `History`: xem report đã có sẵn
- Tab `Settings`: chỉnh số vòng lặp, độ chặt lọc insight, mock LLM

### B. Chạy IFQ bằng command line

#### B1. Sinh Insight Cards (Question Generation)

Chạy thử (không cần API key):

```bash
python run_qugen.py \
  --csv data/transactions.csv \
  --output insight_cards.json \
  --iterations 2 \
  --samples 1 \
  --dry-run
```

Chạy thật (có API key):

```bash
python run_qugen.py \
  --csv data/transactions.csv \
  --output insight_cards.json
```

#### B2. Sinh Insight Summary (Insight Generation)

```bash
python run_isgen.py \
  --csv data/transactions.csv \
  --insight-cards insight_cards.json \
  --output insights_summary.json \
  --plot-dir plots
```

Tùy chọn hay dùng:
- `--no-subspace`: bỏ bước subspace search
- `--no-llm`: không gọi LLM trong subspace search (chạy nhanh, không tốn API)

#### B3. Kiểm tra output IFQ

- `insight_cards.json`: output từ Question Generation
- `insights_summary.json`: output cuối của Insight Generation
- `plots/`: hình biểu đồ cho từng insight (nếu có bật `--plot-dir`)

---

## Phần 2 - Chạy baseline

Baseline nằm ở `baseline/auto_eda_agent`, chạy theo pipeline 5 bước.

### 1) Chạy baseline pipeline

```bash
source venv/bin/activate
cd baseline/auto_eda_agent
python run.py ../../data/transactions.csv output
```

Nếu chỉ muốn chạy bước 1-4, bỏ bước insight extraction:

```bash
python run.py ../../data/transactions.csv output --skip-step5
```

### 2) Output baseline cần kiểm tra

Kết quả nằm trong `baseline/auto_eda_agent/output/`:
- `step1_profiling/`
- `step2_quality/`
- `step3_statistics/`
- `step4_patterns/`
- `step5_insights/`
- `summary/summary.txt`
- `quis_format/` (output đã convert sang format tương thích IFQ)

### 3) Chạy demo baseline (tuỳ chọn)

Từ thư mục gốc project:

```bash
source venv/bin/activate
streamlit run baseline/auto_eda_agent/demo/app.py --server.port 8502
```

---

## Phần 3 - Chạy evaluation

Evaluation dùng script tại `evaluation/run_evaluation.py` để so sánh 2 hệ thống.

### 1) Chuẩn bị 2 file insight summary để so sánh

Ví dụ:
- IFQ output: `insights_summary.json`
- Baseline output: `baseline/auto_eda_agent/output/quis_format/insights.json`

### 2) Chạy lệnh evaluation

Từ thư mục gốc project:

```bash
source venv/bin/activate
python evaluation/run_evaluation.py \
  --data data/transactions.csv \
  --system_a IFQ \
  --path_a insights_summary.json \
  --timing_a evaluation/timing.json \
  --token_a evaluation/token.json \
  --system_b Baseline \
  --path_b baseline/auto_eda_agent/output/quis_format/insights.json \
  --timing_b evaluation/timing.json \
  --token_b evaluation/token.json \
  --output evaluation/evaluation_results
```

Lưu ý:
- `--timing_*` và `--token_*` là optional. Có thể bỏ nếu chưa có dữ liệu đo thời gian/token.
- Đảm bảo cả 2 file input (`--path_a`, `--path_b`) cùng định dạng danh sách insights.

### 3) Kết quả evaluation

Trong thư mục output (mặc định `evaluation/evaluation_results/`) sẽ có:
- `<system>_results.json` cho từng hệ thống
- `comparison_table.csv`
- `comparison_report.md`
- các file biểu đồ tổng hợp

---

## Tài liệu chi tiết thêm

- `docs/QUGEN_PIPELINE.md` (Question Generation pipeline)
- `docs/ISGEN_PIPELINE.md` (Insight Generation pipeline)
- `baseline/auto_eda_agent/README.md`
- `evaluation/README.md`
