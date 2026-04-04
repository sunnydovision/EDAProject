# Data Quality Report

## Summary

- **Total Issues**: 6
- **Critical Issues**: 4
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

### High percentage of outliers in Retailer ID
- **Severity**: high
- **Impact**: The presence of a large number of outliers (45.43%) in Retailer ID suggests potential data entry errors or inconsistencies, which can lead to misinterpretation of retailer performance and skewed analysis.
- **Recommendation**: Investigate the source of these outliers to determine if they are valid entries or errors. Implement data validation rules to prevent incorrect Retailer IDs from being entered.

### Outliers in Units Sold
- **Severity**: medium
- **Impact**: A significant number of outliers (6.50%) in Units Sold may indicate erroneous sales data, which can distort sales performance analysis and forecasting.
- **Recommendation**: Review the data collection process for Units Sold and apply statistical methods to identify and handle outliers appropriately, such as capping or transforming the data.

### Negative values in Total Sales and Operating Profit
- **Severity**: medium
- **Impact**: Negative values in Total Sales (-214363.75) and Operating Profit (-73289.5) can indicate serious issues with data accuracy and may mislead financial analysis.
- **Recommendation**: Conduct a thorough review of the calculations and data sources for Total Sales and Operating Profit to ensure accuracy. Implement checks to flag negative values where they are not expected.

### Outliers in Operating Margin
- **Severity**: medium
- **Impact**: The presence of outliers (0.46%) in Operating Margin can affect profitability analysis and decision-making.
- **Recommendation**: Analyze the data for Operating Margin to identify the cause of these outliers and consider adjusting the calculation methodology to better reflect true performance.

