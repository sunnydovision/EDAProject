# QUIS Project - Hướng dẫn chạy cho thành viên mới

README này dành cho thành viên mới clone project và cần chạy được ngay trên máy local.

## Chuẩn bị chung

### 1) Clone và vào project

```bash
git clone https://github.com/sunnydovision/EDAProject.git
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

- Dataset giao dịch: `data/transactions_cleaned.csv`
- Dataset Adidas (dùng nhiều trong baseline/evaluation): `data/Adidas_cleaned.csv`

---

## Phần 1 - Chạy project QUIS

Phần này gồm 2 cách thường dùng:
- Cách A: chạy app giao diện Streamlit
- Cách B: chạy pipeline bằng CLI (`QUGEN -> ISGEN`)

### A. Chạy app giao diện

Từ thư mục gốc project:

```bash
source venv/bin/activate
streamlit run quis/demo/app.py
```

Sau đó mở URL Streamlit (thường là `http://localhost:8501`).

Trong app:
- Tab `Home`: upload CSV và bấm **Generate New Report**
- Tab `History`: xem report đã có sẵn
- Tab `Settings`: chỉnh số vòng lặp, độ chặt lọc insight, mock LLM

### B. Chạy QUIS bằng command line

#### B1. Sinh Insight Cards (QUGEN)

Chạy với API key:

```bash
python scripts/run_qugen.py \
  --csv data/transactions.csv \
  --output insight_cards.json
```

#### B2. Sinh Insight Summary (ISGEN)

```bash
python scripts/run_isgen.py \
  --csv data/transactions.csv \
  --insight-cards insight_cards.json \
  --output insights_summary.json \
  --plot-dir plots
```

Tùy chọn hay dùng:
- `--no-subspace`: bỏ bước subspace search
- `--no-llm`: không gọi LLM trong subspace search

#### B3. Kiểm tra output QUIS

- `insight_cards.json`: output từ QUGEN
- `insights_summary.json`: output cuối của ISGEN
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
- `quis_format/` (output đã convert sang format tương thích QUIS)

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
- QUIS output: `insights_summary.json`
- Baseline output: `baseline/auto_eda_agent/output/quis_format/insights.json`

### 2) Chạy lệnh evaluation

Từ thư mục gốc project:

```bash
source venv/bin/activate
python evaluation/run_evaluation.py \
  --data data/transactions.csv \
  --system_a QUIS \
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

## Phần 4 - Full Pipeline 3-way Evaluation (QUIS vs Baseline vs OnlyStats)

Pipeline này chạy 3 hệ thống và so sánh kết quả evaluation.

### 1) Chạy QUIS pipeline

```bash
source venv/bin/activate
python scripts/run_quis_pipeline.py --csv data/adidas_cleaned.csv
```

Output: `quis_results/quis_{timestamp}_{dataset}/insight_cards.json`, `insights_summary.json`, `timing.json`, `usage.json`

Lưu ý timestamp trong output directory, ví dụ: `quis_results/quis_20260427_144322_adidas_cleaned/`

### 2) Chạy Baseline pipeline

```bash
cd baseline/auto_eda_agent
python run.py adidas
```

Output: `output_adidas/step1_profiling/profile.json`, `output_adidas/step5_insights/insights.json`

### 3) Chạy OnlyStats pipeline

```bash
cd ../..
python scripts/run_onlystats.py \
  --csv data/adidas_cleaned.csv \
  --profile baseline/auto_eda_agent/output_adidas/step1_profiling/profile.json
```

Output: `onlystats_results/onlystats_{timestamp}_{dataset}/insight_cards.json`, `insights_summary.json`, `timing.json`, `usage.json`

Lưu ý timestamp trong output directory, ví dụ: `onlystats_results/onlystats_20260427_160049_adidas_cleaned/`

### 4) Cập nhật output paths vào evaluation/configs/eval_config.py

Mở file `evaluation/configs/eval_config.py` và cập nhật paths trong DATASETS dict cho dataset tương ứng:

```python
"adidas": {
    "data_path": "data/adidas_cleaned.csv",
    "profile_path": "baseline/auto_eda_agent/output_adidas/step1_profiling/profile.json",
    "quis_insights_path": "quis_results/quis_{timestamp}_adidas_cleaned/insights_summary.json",  # Cập nhật timestamp thực tế
    "baseline_insights_path": "baseline/auto_eda_agent/output_adidas/step5_insights/insights.json",
    "onlystats_insights_path": "onlystats_results/onlystats_{timestamp}_adidas_cleaned/insights_summary.json",  # Cập nhật timestamp thực tế
    "quis_timing_path": "quis_results/quis_{timestamp}_adidas_cleaned/timing.json",
    "quis_usage_path": "quis_results/quis_{timestamp}_adidas_cleaned/usage.json",
    "baseline_timing_path": "baseline/auto_eda_agent/output_adidas/timing.json",
    "baseline_usage_path": "baseline/auto_eda_agent/output_adidas/usage.json",
}
```

**Quan trọng:** Cập nhật timestamp thực tế từ output của QUIS và OnlyStats pipeline.

### 5) Chạy evaluation 3-way

```bash
python evaluation/run_evaluation_3ways.py --dataset adidas
```

### 6) Kết quả

Kết quả so sánh nằm trong `evaluation/evaluation_results/{dataset_name}/`:
- `quis_results.json`, `baseline_results.json`, `onlystats_results.json`
- `comparison_table_3way.csv`
- `comparison_report_3way.md`

---

## Tài liệu chi tiết thêm

- `docs/QUGEN_PIPELINE.md` (QUGEN pipeline)
- `docs/ISGEN_PIPELINE.md` (ISGEN pipeline)
- `baseline/auto_eda_agent/README.md`
- `evaluation/README.md`
