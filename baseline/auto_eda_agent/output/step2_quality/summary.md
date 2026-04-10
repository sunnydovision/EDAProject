# Data Quality Report

## Summary

- **Total Issues**: 2
- **Critical Issues**: 2
- **Quality Score**: 70/100

## Missing Values

No missing values detected.

## Outliers

- **Retailer ID**: 45.4% (4383 outliers)
- **Units Sold**: 6.5% (627 outliers)

## Critical Issues

### Outliers in Retailer ID
- **Severity**: high
- **Impact**: The presence of a significant number of outliers (45.43%) in Retailer ID indicates potential data entry errors or inconsistencies. This can lead to misattribution of sales data to incorrect retailers, skewing analysis and reporting.
- **Recommendation**: Investigate the source of these outliers. Validate the Retailer ID entries against a trusted reference dataset to ensure accuracy and consistency.

### Outliers in Units Sold
- **Severity**: medium
- **Impact**: With 6.50% of Units Sold being classified as outliers, this could distort sales performance analysis and forecasting. Negative values, in particular, are concerning as they may indicate data entry errors.
- **Recommendation**: Review the entries for Units Sold, especially those with negative values. Implement validation rules to prevent negative entries and consider using statistical methods to identify and handle outliers appropriately.

