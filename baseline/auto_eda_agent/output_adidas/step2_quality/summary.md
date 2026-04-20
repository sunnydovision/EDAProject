# Data Quality Report

## Summary

- **Total Issues**: 5
- **Critical Issues**: 5
- **Quality Score**: 82/100

## Missing Values

No missing values detected.

## Outliers

- **Operating Profit**: 7.3% (706 outliers)
- **Total Sales**: 6.8% (653 outliers)
- **Units Sold**: 6.5% (627 outliers)
- **Price per Unit**: 0.8% (81 outliers)
- **Operating Margin**: 0.5% (44 outliers)

## Critical Issues

### Outliers detected in Operating Profit (706 records, 7.32%) in a high-importance financial column.
- **Severity**: high
- **Impact**: Operating Profit is a core profitability metric used for margin analysis, product performance evaluation, and retailer/regional comparisons. A high share of extreme values can materially distort profit trends, profitability rankings, forecasting, and executive reporting. If invalid, these values may lead to incorrect conclusions about which products, states, or retailers are most profitable.
- **Recommendation**: Validate extreme Operating Profit values against source transactions and business rules. Check whether these records are driven by legitimate high-volume sales, returns, discounts, or data entry/calculation errors. Apply targeted remediation such as correction, exclusion from specific analyses, or winsorization only where justified.

### Outliers detected in Total Sales (653 records, 6.77%) in a high-importance revenue column.
- **Severity**: high
- **Impact**: Total Sales is a primary KPI for revenue reporting and trend analysis. Extreme values can skew aggregate sales, average order value, state/product performance comparisons, and forecasting models. Because this is a high-importance measure, even a moderate outlier rate can significantly affect business decisions and dashboard accuracy.
- **Recommendation**: Investigate whether outliers reflect valid large transactions, bulk orders, refunds, or pricing/quantity errors. Reconcile suspicious records with Price per Unit and Units Sold to confirm whether Total Sales is internally consistent. Flag validated exceptional transactions separately from erroneous ones.

### Outliers detected in Units Sold (627 records, 6.50%) in a high-importance volume column.
- **Severity**: high
- **Impact**: Units Sold drives demand analysis, inventory planning, and sales performance measurement. Extreme values may distort product demand patterns, retailer comparisons, replenishment planning, and seasonality analysis. Since Units Sold also influences Total Sales and Operating Profit, anomalies here may propagate into multiple downstream metrics.
- **Recommendation**: Review extreme quantity records for bulk purchases, returns, cancellations, or entry errors. Cross-check with Total Sales and Price per Unit for consistency. Establish business thresholds by product or sales method rather than relying only on global statistical bounds.

### Outliers detected in Price per Unit (81 records, 0.84%) in a high-importance pricing column.
- **Severity**: medium
- **Impact**: Although the percentage is relatively low, Price per Unit is a critical driver of revenue and margin calculations. Invalid price points can create cascading errors in Total Sales and Operating Profit, affecting pricing analysis, discount effectiveness studies, and product profitability assessments.
- **Recommendation**: Audit records outside expected price ranges to determine whether they represent premium products, promotions, or data entry issues. Validate against product master pricing and discount rules. Where appropriate, segment outlier detection by product category to avoid misclassifying legitimate price variation.

### Outliers detected in Operating Margin (44 records, 0.46%) in a high-importance profitability ratio column.
- **Severity**: medium
- **Impact**: Operating Margin is used to assess efficiency and profitability quality. Even a small number of anomalous margin values can mislead comparative analysis across products, retailers, or regions, especially if margins are used in executive summaries or exception reporting.
- **Recommendation**: Verify whether unusual margins are caused by valid promotional activity, cost allocation differences, or incorrect profit/sales calculations. Recompute Operating Margin from source values where possible and enforce acceptable business-rule ranges.

