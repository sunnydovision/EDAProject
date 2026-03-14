# Data Quality Report

## Summary

- **Total Issues**: 17
- **Critical Issues**: 3
- **Quality Score**: 65/100

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
- **Khối lượng**: 9.6% (99 outliers)
- **Met A**: 8.6% (89 outliers)
- **Khoảng_cách_đơn_trước**: 8.1% (84 outliers)
- **Met C**: 4.2% (44 outliers)
- **Met B**: 3.9% (40 outliers)
- **Cờ_giao_dịch_bất_thường**: 3.9% (40 outliers)

## Critical Issues

### High percentage of missing values in 'Mã màu' and 'Tên màu'
- **Severity**: high
- **Impact**: The high percentage of missing values (32%) in these critical fields can lead to incomplete analyses and misinterpretations, affecting decision-making processes.
- **Recommendation**: Implement data collection improvements to ensure that these fields are filled out during data entry. Consider using validation rules to enforce mandatory fields.

### Significant outliers in 'Thành Tiền' and 'Năm'
- **Severity**: high
- **Impact**: Outliers can skew results and lead to incorrect conclusions about trends and averages, especially in financial metrics like 'Thành Tiền'.
- **Recommendation**: Conduct a thorough investigation to understand the cause of these outliers and determine if they should be corrected or removed from the dataset.

### Outliers in 'Khối lượng' and 'Doanh_thu_trên_mm'
- **Severity**: medium
- **Impact**: While not as severe as the previous issues, these outliers can still affect the reliability of the dataset, leading to potential miscalculations in analyses.
- **Recommendation**: Analyze the context of these outliers and apply appropriate statistical methods to handle them, such as winsorizing or transformation.

