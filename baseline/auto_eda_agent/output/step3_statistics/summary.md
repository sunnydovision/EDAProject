# Statistical Analysis Report

## Summary

- **Numerical Columns**: 23
- **Categorical Columns**: 20
- **Strong Correlations**: 3

## Key Findings

- The variable 'Khối lượng' has a high mean (3740.80) and a significant range (from 210 to 5180), indicating variability in the data.
- The variable 'Met B' has a mean of 12.15 but a median of 0, suggesting that most observations are zero, with a few high outliers.
- The correlation between 'Cờ_khiếu_nại_lặp_lại' and 'Điểm_hài_lòng_khách_hàng' is strongly negative (-0.81), indicating that repeated complaints are associated with lower customer satisfaction.

## Strong Correlations

### Khối lượng and Thành Tiền
- **Strength**: strong
- **Interpretation**: This strong positive correlation (0.95) indicates that as the 'Khối lượng' increases, 'Thành Tiền' also increases significantly, suggesting that higher volumes lead to higher revenue.

### Thành Tiền and Doanh_thu_trên_mm
- **Strength**: strong
- **Interpretation**: The correlation of nearly 1 (0.9999) implies that 'Thành Tiền' and 'Doanh_thu_trên_mm' are almost perfectly linearly related, indicating that they may be measuring the same underlying concept.

### Năm and Tháng
- **Strength**: strong
- **Interpretation**: The negative correlation (-0.95) suggests an inverse relationship, where as the year increases, the month decreases, which is expected since months are cyclical within a year.

