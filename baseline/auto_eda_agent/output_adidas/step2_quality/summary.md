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

### Outliers detected in Operating Profit (706 records, 7.32%). This is a high-importance financial metric, and the outlier rate is the highest among all flagged columns.
- **Severity**: high
- **Impact**: Operating Profit is central to profitability analysis, margin tracking, retailer performance comparisons, and financial reporting. Extreme values can distort average profit, trend analysis, benchmarking, and profitability-based decision-making. If these values are data errors rather than true business events, they may lead to incorrect conclusions about product, retailer, or regional performance.
- **Recommendation**: Validate extreme Operating Profit values against source transactions and business rules. Reconcile with Total Sales, Units Sold, and Operating Margin to confirm whether values are legitimate high-profit events or calculation/data-entry errors. Apply correction, exclusion, or capping rules only after business validation.

### Outliers detected in Total Sales (653 records, 6.77%). This affects a high-importance revenue field with a substantial proportion of records flagged.
- **Severity**: high
- **Impact**: Total Sales drives revenue reporting, sales forecasting, product performance analysis, and retailer ranking. Unchecked outliers can skew revenue aggregates, inflate or suppress sales trends, and mislead strategic decisions such as inventory planning, pricing, and territory management.
- **Recommendation**: Review flagged Total Sales records for transaction validity, especially unusually large orders, returns, or aggregation errors. Cross-check against Price per Unit × Units Sold and invoice-level business logic. Correct calculation issues and document any legitimate exceptional sales events.

### Outliers detected in Units Sold (627 records, 6.50%). This is a high-importance operational measure with a meaningful concentration of extreme values.
- **Severity**: high
- **Impact**: Units Sold affects demand analysis, inventory planning, product performance measurement, and sales productivity metrics. Extreme values may indicate bulk orders, returns, duplication, or entry errors. If not reviewed, they can distort demand forecasts and operational planning.
- **Recommendation**: Investigate extreme Units Sold values by invoice, product, and retailer. Distinguish between valid bulk transactions and anomalies such as duplicate loads, return postings, or unit-entry mistakes. Introduce validation thresholds and exception reporting for future loads.

### Outliers detected in Price per Unit (81 records, 0.84%). Although the percentage is relatively low, this affects a high-importance pricing field.
- **Severity**: medium
- **Impact**: Price per Unit influences revenue calculations, margin analysis, pricing strategy, and product profitability. Even a small number of incorrect prices can materially affect Total Sales and Operating Profit, especially for high-volume transactions.
- **Recommendation**: Audit flagged price records against product price lists, discount policies, and promotional pricing. Confirm whether values reflect valid premium/discounted sales or pricing errors. Add product-level price range validation rules.

### Outliers detected in Operating Margin (44 records, 0.46%). The proportion is low, but the field is high importance and directly tied to profitability interpretation.
- **Severity**: medium
- **Impact**: Operating Margin is used to assess efficiency and profitability across products, retailers, and regions. Extreme margin values may indicate incorrect profit or sales calculations, unusual discounting, or inconsistent cost treatment. This can mislead margin-based comparisons and strategic decisions.
- **Recommendation**: Recalculate Operating Margin for flagged records using validated Operating Profit and Total Sales values. Investigate whether extreme margins are caused by legitimate business scenarios, rounding issues, or upstream calculation defects.

