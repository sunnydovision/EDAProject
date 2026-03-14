# Statistical Analysis Report

## Summary

- **Numerical Columns**: 23
- **Categorical Columns**: 20
- **Strong Correlations**: 5

## Key Findings

- The variable 'Khối lượng' has a significant impact on revenue generation, indicating that sales volume is a critical factor for business performance.
- The perfect correlation between 'Thành Tiền' and 'Doanh_thu_trên_mm' suggests redundancy in these metrics, which may warrant further investigation or consolidation.
- The presence of extreme outliers in 'Met B' and 'Met C' indicates potential issues with data quality or the need for further analysis to understand these distributions.

## Strong Correlations

### Khối lượng and Thành Tiền
- **Strength**: strong
- **Interpretation**: This strong positive correlation (0.95) indicates that as the volume increases, the total revenue also increases significantly, suggesting a direct relationship between the quantity sold and revenue generated.

### Thành Tiền and Doanh_thu_trên_mm
- **Strength**: strong
- **Interpretation**: The perfect correlation (1.0) implies that these two variables are essentially measuring the same underlying phenomenon, indicating that total revenue and revenue per square meter are directly related.

### Năm and Tháng
- **Strength**: strong
- **Interpretation**: The strong negative correlation (-0.95) suggests that as the year increases, the month decreases, which is expected in a time series context.

### Số_lần_bán_sản_phẩm and Tần_suất_bán
- **Strength**: strong
- **Interpretation**: The strong positive correlation (0.89) indicates that the frequency of product sales is closely related to the number of times a product is sold, suggesting that higher sales frequency leads to more sales.

### Cờ_khiếu_nại_lặp_lại and Điểm_hài_lòng_khách_hàng
- **Strength**: strong
- **Interpretation**: The strong negative correlation (-0.81) indicates that an increase in repeated complaints is associated with a decrease in customer satisfaction, suggesting that customer dissatisfaction leads to more complaints.

