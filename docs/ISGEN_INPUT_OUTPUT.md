# ISGEN – Input & Output

## Input

| Thành phần | Mô tả |
|------------|--------|
| **Insight Cards** | File JSON từ QUGEN (mỗi phần tử: `question`, `reason`, `breakdown`, `measure`). Mặc định: `insight_cards.json`. |
| **Dataset** | File CSV (cùng format với QUGEN: delimiter tự nhận `;` hoặc `,`, số thập phân `,` hoặc `.`). |

## Output

| Thành phần | Mô tả |
|------------|--------|
| **Insights Summary** | File JSON: danh sách object, mỗi object gồm `question`, `explanation` (mô tả NL), `plot_path` (đường dẫn file hình, nếu có `--plot-dir`), `insight` (breakdown, measure, subspace, pattern, score). |
| **Plots** | Nếu dùng `--plot-dir`: thư mục chứa ảnh PNG (scatter/bar/pie) theo từng insight. |

## Lệnh mẫu

```bash
# Chỉ basic insights, không subspace search
python scripts/run_isgen.py --csv data/transactions.csv --insight-cards insight_cards.json --output insights_summary.json --no-subspace

# Đầy đủ (basic + subspace search), có vẽ đồ thị
python scripts/run_isgen.py --csv data/transactions.csv --insight-cards insight_cards.json --output insights_summary.json --plot-dir plots
```
