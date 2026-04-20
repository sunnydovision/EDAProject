# Data Quality Report

## Summary

- **Total Issues**: 20
- **Critical Issues**: 20
- **Quality Score**: 68/100

## Missing Values

- **Mã màu**: 32.0% (332 rows)
- **Tên màu**: 32.0% (332 rows)
- **Khu Vực (Quận/Huyện)**: 4.7% (49 rows)
- **Khoảng_cách_đơn_trước**: 4.1% (42 rows)

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

### Missing values in 'Mã màu' (332 records, 32.05%), a high-importance product attribute.
- **Severity**: high
- **Impact**: Affects product-level analysis, SKU grouping, color-based sales reporting, inventory segmentation, and any downstream modeling that relies on product identity or color classification. Missing product code values can also break joins with reference/master data.
- **Recommendation**: Investigate whether 'Mã màu' can be backfilled from 'Tên màu', SKU fields, or product master data. Enforce mandatory capture for this field at source and add validation rules to prevent null product color codes.

### Missing values in 'Tên màu' (332 records, 32.05%), reducing interpretability of product color information.
- **Severity**: medium
- **Impact**: Limits business reporting and user-facing analysis by color, reduces explainability of product segmentation, and weakens validation against 'Mã màu'. While less critical than coded attributes, it still affects commercial analysis and data usability.
- **Recommendation**: Standardize and populate 'Tên màu' using lookup tables from 'Mã màu'. Add a controlled dictionary for color names and enforce consistency between code and label.

### Missing values in 'Khu Vực (Quận/Huyện)' (49 records, 4.73%) in a high-importance geographic field.
- **Severity**: high
- **Impact**: Reduces accuracy of district-level sales analysis, geographic demand mapping, delivery performance analysis, and regional customer segmentation. It may also distort local operational planning and territory performance reporting.
- **Recommendation**: Backfill district values from customer address, province-city combinations, or CRM/location master data. Add address completeness checks during data entry.

### Missing values in 'Khoảng_cách_đơn_trước' (42 records, 4.05%) in a medium-importance behavioral feature.
- **Severity**: medium
- **Impact**: Impairs recency analysis, customer purchase pattern tracking, and predictive features used for churn, reorder, or sales frequency modeling.
- **Recommendation**: Recompute this field from transaction dates ordered by customer/product. If derived, avoid manual storage and generate it systematically in the transformation layer.

### High outlier rate in 'Khối lượng' (99 records, 9.56%) for a high-importance operational measure.
- **Severity**: high
- **Impact**: Can distort pricing analysis, logistics planning, product profitability, and unit economics. Extreme values may indicate unit inconsistency, entry errors, or genuinely exceptional orders that need separate treatment.
- **Recommendation**: Validate units of measure and compare against expected ranges by product type. Review extreme records with business owners and either correct data-entry errors or flag legitimate exceptional transactions.

