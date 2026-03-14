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
- **Impact**: The high percentage of missing values (32.05%) in key attributes can lead to biased analysis and incomplete datasets, affecting decision-making processes.
- **Recommendation**: Implement data collection improvements and validation checks to reduce missing values. Consider using imputation techniques where appropriate.

### Significant outlier counts in 'Thành Tiền' and 'Năm'
- **Severity**: high
- **Impact**: Outliers can skew results and lead to incorrect conclusions, particularly in financial metrics like 'Thành Tiền'.
- **Recommendation**: Conduct a thorough review of outlier data points to determine if they are valid or erroneous. Consider applying data transformation techniques to mitigate their impact.

### Outliers in 'Khối lượng' and 'Doanh_thu_trên_mm'
- **Severity**: medium
- **Impact**: Outliers in these metrics may indicate data entry errors or unusual transactions that could mislead analysis.
- **Recommendation**: Investigate the source of these outliers and apply appropriate data cleansing methods to ensure accuracy.

