# Data Quality Report

## Summary

- **Total Issues**: 22
- **Critical Issues**: 22
- **Quality Score**: 68/100

## Missing Values

- **Mã màu**: 32.0% (332 rows)
- **Tên màu**: 32.0% (332 rows)
- **Khu Vực (Quận/Huyện)**: 4.7% (49 rows)
- **Khoảng_cách_đơn_trước**: 4.1% (42 rows)
- **Tổng_doanh_thu_sản_phẩm**: 2.5% (26 rows)
- **Doanh_thu_theo_tuan_trong_thang**: 2.4% (25 rows)

## Outliers

- **Năm**: 21.7% (225 outliers)
- **Tháng**: 21.7% (225 outliers)
- **Thành Tiền**: 10.6% (110 outliers)
- **Doanh_thu_trên_mm**: 10.6% (110 outliers)
- **Tỷ_trọng_doanh_thu_%**: 10.6% (110 outliers)
- **Khối lượng**: 9.6% (99 outliers)
- **Met A**: 8.6% (89 outliers)
- **Khoảng_cách_đơn_trước**: 8.1% (84 outliers)
- **Met C**: 4.2% (44 outliers)
- **Met B**: 3.9% (40 outliers)

## Critical Issues

### Missing values in 'Mã màu' (32.05%), a high-importance product attribute.
- **Severity**: high
- **Impact**: A large share of records cannot be reliably grouped, filtered, or analyzed by color code. This weakens product-level sales analysis, SKU mapping, inventory reporting, and any downstream segmentation or pricing analysis tied to color.
- **Recommendation**: Backfill 'Mã màu' from product master data or infer from related fields such as 'Tên màu', 'SKU_Màu', or 'Mã_sản_phẩm'. Enforce mandatory population of color code at data entry.

### Missing values in 'Tên màu' (32.05%), a medium-importance descriptive product field closely related to a high-importance attribute.
- **Severity**: medium
- **Impact**: Color-based reporting becomes less interpretable for business users, and validation between color code and color name is not possible for one-third of records. This also reduces trust in product categorization outputs.
- **Recommendation**: Standardize and populate 'Tên màu' using reference mappings from 'Mã màu' or product master tables. Add validation rules to ensure color name is present when color code exists.

### Missing values in 'Khu Vực (Quận/Huyện)' (4.73%), a high-importance geographic field.
- **Severity**: high
- **Impact**: Regional sales analysis, district-level demand planning, logistics optimization, and customer distribution reporting are incomplete. Geographic aggregation may be biased or understated in affected districts.
- **Recommendation**: Recover missing district values from customer address, delivery records, or 'Tỉnh / Thành Phố'. Add address standardization and mandatory geographic validation in source systems.

### Missing values in 'Doanh_thu_theo_tuan_trong_thang' (2.41%), a derived medium-importance revenue metric.
- **Severity**: medium
- **Impact**: Weekly-in-month revenue trend analysis and period-over-period comparisons may be inconsistent. Dashboards using this metric may show gaps or understate performance.
- **Recommendation**: Recalculate the field from 'Ngày bán' and 'Thành Tiền' rather than storing it as a standalone value. Validate completeness during feature engineering.

### Missing values in 'Khoảng_cách_đơn_trước' (4.05%), a medium-importance behavioral feature.
- **Severity**: medium
- **Impact**: Customer purchase cadence analysis, churn modeling, and repeat-purchase behavior metrics become less reliable. Models using recency intervals may be biased.
- **Recommendation**: Recompute from sorted transaction history by customer and sale date. Distinguish true first-order cases from missing historical data.

