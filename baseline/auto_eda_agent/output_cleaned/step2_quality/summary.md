# Data Quality Report

## Summary

- **Total Issues**: 6
- **Critical Issues**: 5
- **Quality Score**: 70/100

## Missing Values

No missing values detected.

## Outliers

- **Retailer ID**: 45.4% (4383 outliers)
- **Operating Profit**: 7.3% (706 outliers)
- **Total Sales**: 6.8% (653 outliers)
- **Units Sold**: 6.5% (627 outliers)
- **Price per Unit**: 0.8% (81 outliers)
- **Operating Margin**: 0.5% (44 outliers)

## Critical Issues

### Outliers in Retailer ID
- **Severity**: high
- **Impact**: The presence of a significant number of outliers (45.43%) in Retailer ID suggests potential data entry errors or inconsistencies, which can lead to incorrect retailer identification and affect sales analysis.
- **Recommendation**: Investigate the source of these outliers and correct or remove erroneous entries to ensure accurate retailer identification.

### Outliers in Units Sold
- **Severity**: medium
- **Impact**: With 6.50% of Units Sold data being outliers, this can skew sales performance metrics and mislead inventory and sales forecasting.
- **Recommendation**: Review the outlier entries for Units Sold and determine if they are valid. Consider applying transformations or removing extreme values if they are erroneous.

### Outliers in Total Sales
- **Severity**: medium
- **Impact**: The 6.77% outlier rate in Total Sales can distort revenue analysis and financial reporting, leading to incorrect business decisions.
- **Recommendation**: Analyze the outlier transactions for Total Sales to ascertain their validity and either correct or exclude them from analysis.

### Outliers in Operating Profit
- **Severity**: medium
- **Impact**: Outliers in Operating Profit (7.32%) can misrepresent the financial health of the business, affecting strategic planning and investment decisions.
- **Recommendation**: Investigate the outliers in Operating Profit to determine their accuracy and make necessary adjustments to ensure reliable financial reporting.

### Outliers in Operating Margin
- **Severity**: low
- **Impact**: While the percentage of outliers in Operating Margin is relatively low (0.46%), they can still affect performance metrics and comparisons across periods.
- **Recommendation**: Review the outlier entries in Operating Margin for potential corrections or exclusions to maintain consistent performance metrics.

