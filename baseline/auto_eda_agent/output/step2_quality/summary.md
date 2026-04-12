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

### Operating Profit contains 706 outliers (7.32%) in a high-importance financial column.
- **Severity**: high
- **Impact**: Operating Profit is a core profitability measure. A high proportion of outliers can materially distort profit trend analysis, retailer/product performance comparisons, forecasting, and margin-based decision-making. Extreme values may reflect valid business events, but they may also indicate calculation errors, data entry issues, or inconsistent treatment of discounts/costs.
- **Recommendation**: Perform targeted validation of extreme Operating Profit records against source transactions and business rules. Recalculate profit from underlying revenue and cost components where possible, and flag confirmed exceptional but valid values separately from erroneous records.

### Total Sales contains 653 outliers (6.77%) in a high-importance revenue column.
- **Severity**: high
- **Impact**: Total Sales drives revenue reporting, sales trend analysis, and performance benchmarking. Outliers at this level can skew aggregate sales metrics, inflate or suppress averages, and reduce confidence in dashboards and forecasting models. Because Total Sales is often derived from Price per Unit and Units Sold, anomalies may indicate upstream calculation inconsistencies.
- **Recommendation**: Validate extreme Total Sales values against invoice-level source data and confirm whether they align with Price per Unit × Units Sold. Investigate potential unit scaling issues, duplicate line aggregation, returns/credits treatment, or formula errors.

### Units Sold contains 627 outliers (6.50%) in a high-importance volume column.
- **Severity**: high
- **Impact**: Units Sold is fundamental for demand analysis, inventory planning, and sales productivity metrics. A large number of outliers can distort volume trends, product mix analysis, and operational planning. Since the lower bound is negative, the outlier detection likely captures unusually large values rather than invalid negatives, but these still require review for bulk orders, aggregation issues, or entry errors.
- **Recommendation**: Review extreme Units Sold records by product, retailer, and invoice date to distinguish legitimate bulk transactions from data errors. Apply business-rule thresholds by product category or sales channel rather than relying only on generic statistical outlier detection.

### Price per Unit contains 81 outliers (0.84%) in a high-importance pricing column.
- **Severity**: medium
- **Impact**: Although the proportion is relatively low, Price per Unit is a critical driver of revenue and margin calculations. Pricing anomalies can lead to incorrect sales valuation, misleading discount analysis, and downstream inconsistencies in Total Sales and Operating Profit.
- **Recommendation**: Check outlier prices against product master data, approved price lists, and promotion/discount records. Standardize handling of special pricing scenarios such as bundles, markdowns, or wholesale contracts.

### Operating Margin contains 44 outliers (0.46%) in a high-importance profitability ratio column.
- **Severity**: medium
- **Impact**: Operating Margin is used to assess efficiency and profitability quality. Even a small number of anomalous margin values can mislead profitability benchmarking and exception reporting, especially if they are concentrated in specific retailers, products, or regions. Margin anomalies may also signal inconsistency between Total Sales and Operating Profit.
- **Recommendation**: Recompute Operating Margin from validated Total Sales and Operating Profit values and compare against stored values. Investigate records outside expected business ranges for possible formula, rounding, or sign errors.

