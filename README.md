# QUIS – Question-guided Insights Generation (EDA)

Hiện thực theo bài báo **QUIS: Question-guided Insights Generation for Automated Exploratory Data Analysis** (arXiv:2410.10270v3).

## Phần 1: QUGEN (Question Generation)

Module QUGEN sinh ra **Insight Cards** (Question, Reason, Breakdown, Measure) từ schema và thống kê cơ bản của bảng, lặp theo vòng để mở rộng coverage.

### Các bước pipeline (theo bài báo)

1. **Tạo prompt**: Mô tả nhiệm vụ + hướng dẫn + few-shot examples + schema bảng + natural language stats.
2. **Gọi LLM**: Lấy `s` mẫu với temperature `t` (mặc định s=3, t=1.1).
3. **Parse**: Trích các Insight Card từ output (REASON, QUESTION, BREAKDOWN, MEASURE).
4. **Lọc**:
   - Relevance: bỏ câu hỏi không liên quan schema (all-MiniLM-L6-v2).
   - Dedup: bỏ trùng theo độ tương đồng câu hỏi.
   - Simple: bỏ câu hỏi đơn giản (SQL trả về 1 dòng).
5. **Lặp**: Thêm cards vào pool, chọn subset làm in-context cho iteration tiếp theo.
6. **Output**: Tập Insight Cards sau N iterations (mặc định 10).

Chi tiết: [docs/QUGEN_PIPELINE.md](docs/QUGEN_PIPELINE.md).

### Input / Output

| | Mô tả |
|---|--------|
| **Input** | Schema bảng (tên, cột, kiểu) + tùy chọn DataFrame (CSV) cho basic stats và simple-question filter. |
| **Output** | Danh sách **InsightCard**: `question`, `reason`, `breakdown`, `measure`. |

### Cài đặt

```bash
cd /Users/ngocuit/Desktop/EDAProj
pip install -r requirements.txt
```

Cấu hình LLM (Llama-3-70b-instruct hoặc API tương thích OpenAI):

```bash
export OPENAI_API_KEY="your-key"
# Hoặc endpoint Llama
export OPENAI_API_BASE="https://..."
export QUGEN_LLM_MODEL="meta-llama/Llama-3-70b-instruct"
```

### Dataset mặc định

Dataset của project: **`data/transactions.csv`** (giao dịch bán hàng: sản phẩm, khu vực, doanh thu, khách hàng, …). Schema tương ứng: **`data/transactions_schema.json`**.

### Input theo bài báo

- **Bắt buộc:** 1 file **CSV** (dataset); từ CSV suy schema + dữ liệu cho basic stats.
- **Bắt buộc khi chạy thật:** Biến môi trường **`OPENAI_API_KEY`** (hoặc `OPENAI_API_BASE`) để gọi LLM.
- **Chạy thử không cần API:** thêm `--dry-run` → dùng mock LLM, vẫn ghi output đúng format.

Chi tiết: [docs/QUGEN_INPUT_OUTPUT.md](docs/QUGEN_INPUT_OUTPUT.md).  
**Hướng dẫn từng bước dùng LLM thật:** [docs/HUONG_DAN_LLM_THAT.md](docs/HUONG_DAN_LLM_THAT.md).

### Chạy QUGEN

**Chạy thử (mock LLM, không cần API key):**

```bash
python run_qugen.py --csv data/transactions.csv --output insight_cards.json --iterations 2 --samples 1 --dry-run
```

**Chạy thật (cần OPENAI_API_KEY) – từ CSV:**

```bash
python run_qugen.py --csv data/transactions.csv --output insight_cards.json
```

**Từ file schema JSON (không cần CSV):**

```bash
python run_qugen.py --schema data/transactions_schema.json --output insight_cards.json
```

**Từ CSV suy ra schema (rồi dùng schema đó):**

Schema được suy từ kiểu cột trong DataFrame (pandas): `int` → INT, `float` → DOUBLE, còn lại → CHAR.

```bash
# Tạo file schema JSON từ CSV
python csv_to_schema.py data/transactions.csv -o data/transactions_schema.json -n transactions

# Sau đó chạy QUGEN bằng schema vừa tạo
python run_qugen.py --schema data/transactions_schema.json --output insight_cards.json
```

Logic suy schema nằm trong `quis.qugen.models.schema_from_dataframe()` (và được gọi tự động khi dùng `run_qugen.py --csv ...`).

**Tham số (theo bài báo Appendix D.2):**

- `--iterations 10` – số vòng lặp
- `--samples 3` – số mẫu mỗi vòng
- `--temperature 1.1`
- `--in-context 6` – số Insight Cards dùng làm in-context

### Dùng trong code

```python
import pandas as pd
from quis.qugen import QUGENPipeline, QUGENConfig, InsightCard
from quis.qugen.models import schema_from_dataframe

df = pd.read_csv("data/transactions.csv")
schema = schema_from_dataframe(df, table_name="transactions")

config = QUGENConfig(
    temperature=1.1,
    num_samples_per_iteration=3,
    num_iterations=10,
    num_in_context_examples=6,
)
pipeline = QUGENPipeline(config=config)
cards: list[InsightCard] = pipeline.run(table_schema=schema, df=df)

for c in cards:
    print(c.question, c.breakdown, c.measure)
```

### Cấu trúc thư mục

```
EDAProj/
├── docs/
│   └── QUGEN_PIPELINE.md   # Các bước pipeline theo bài báo
├── quis/
│   ├── qugen/
│   │   ├── models.py       # InsightCard, TableSchema
│   │   ├── prompts.py      # Figure 6, Figure 7
│   │   ├── llm_client.py   # LLM (OpenAI-compatible)
│   │   ├── parser.py       # Parse [INSIGHT] cards
│   │   ├── filters.py      # Relevance, dedup, simple-question
│   │   ├── stats.py        # Basic stats (Figure 7)
│   │   ├── examples.py     # Few-shot examples
│   │   └── pipeline.py     # QUGENPipeline
│   └── __init__.py
├── run_qugen.py            # CLI
├── requirements.txt
└── README.md
```

Phần 2 (ISGEN – Insight Generation) sẽ dùng danh sách Insight Cards này để sinh insight thống kê và visualization.
