#!/usr/bin/env python3
"""
Từ CSV suy ra schema (JSON) dùng cho QUGEN.

Cách suy schema:
- Đọc CSV bằng pandas → DataFrame
- Với mỗi cột: xem kiểu dữ liệu (dtype) của pandas:
  - integer (int8, int16, int32, int64, Int64, ...) → "INT"
  - float (float16, float32, float64, ...)         → "DOUBLE"
  - còn lại (object, string, datetime, bool, ...)  → "CHAR"
- Tên cột giữ nguyên (pandas có thể đổi tên cột trùng thành "cột.1", "cột.2").

Usage:
  python csv_to_schema.py data/transactions.csv
  python csv_to_schema.py data/transactions.csv -o data/my_schema.json -n transactions
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from quis.qugen.models import schema_from_dataframe


def main():
    parser = argparse.ArgumentParser(
        description="Từ file CSV suy ra schema JSON (tên cột + kiểu INT/DOUBLE/CHAR)."
    )
    parser.add_argument("csv_path", type=str, help="Đường dẫn file CSV")
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="File JSON đầu ra (mặc định: <tên_csv>_schema.json cùng thư mục)",
    )
    parser.add_argument(
        "-n", "--table-name",
        type=str,
        default=None,
        help="Tên bảng (mặc định: tên file CSV không đuôi)",
    )
    args = parser.parse_args()

    csv_path = args.csv_path
    if not os.path.isfile(csv_path):
        print(f"Không tìm thấy file: {csv_path}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(csv_path)
    table_name = args.table_name or os.path.splitext(os.path.basename(csv_path))[0]
    schema = schema_from_dataframe(df, table_name=table_name)

    out_path = args.output
    if not out_path:
        base = os.path.splitext(csv_path)[0]
        out_path = f"{base}_schema.json"

    out_data = {
        "table_name": schema.table_name,
        "columns": schema.columns,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)

    print(f"Đã ghi schema ({len(schema.columns)} cột) → {out_path}")


if __name__ == "__main__":
    main()
