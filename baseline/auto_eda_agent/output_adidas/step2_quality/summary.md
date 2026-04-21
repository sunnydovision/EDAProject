# Data Quality Report

## Summary

- **Total Issues**: 5
- **Critical Issues**: 5
- **Quality Score**: 78/100

## Missing Values

No missing values detected.

## Outliers

- **Operating Profit**: 7.3% (706 outliers)
- **Total Sales**: 6.8% (653 outliers)
- **Units Sold**: 5.3% (508 outliers)
- **Price per Unit**: 0.8% (81 outliers)
- **Operating Margin**: 0.5% (44 outliers)

## Critical Issues

### Outliers detected in Operating Profit (706 records, 7.32%) in a high-importance financial column.
- **Severity**: high
- **Impact**: Operating Profit is a core profitability measure used for margin analysis, product performance evaluation, and retailer/state-level financial reporting. A relatively high proportion of outliers can materially distort profit trends, skew averages, and lead to incorrect conclusions about business performance or underperforming segments.
- **Recommendation**: Validate extreme profit values against source transactions and business rules. Confirm whether these represent legitimate high-value sales, returns, discounts, or data entry/calculation errors. Apply targeted treatment such as correction, exclusion, or winsorization only after business review.

### Outliers detected in Total Sales (653 records, 6.77%) in a high-importance revenue column.
- **Severity**: high
- **Impact**: Total Sales drives revenue reporting, forecasting, and performance benchmarking. Outliers at this level can significantly bias sales KPIs, inflate or suppress regional/product comparisons, and reduce trust in executive dashboards and financial summaries.
- **Recommendation**: Reconcile extreme sales values with invoice-level records and verify consistency with Price per Unit × Units Sold. Investigate whether outliers are caused by bulk orders, returns, aggregation issues, or calculation errors. Flag validated exceptional transactions separately from erroneous records.

### Outliers detected in Units Sold (508 records, 5.27%) in a high-importance volume column.
- **Severity**: high
- **Impact**: Units Sold is central to demand analysis, inventory planning, and product performance measurement. Outliers can distort demand forecasts, create misleading sales velocity patterns, and affect derived metrics such as average selling price and profit per unit.
- **Recommendation**: Review extreme unit quantities for bulk purchases, returns, or input errors. Cross-check against invoice date, product, and total sales values. Establish business thresholds by product category and sales channel to distinguish valid operational extremes from bad data.

### Outliers detected in Price per Unit (81 records, 0.84%) in a high-importance pricing column.
- **Severity**: medium
- **Impact**: Although the percentage is relatively low, Price per Unit is a critical driver of revenue and margin calculations. Abnormal prices can indicate discounting anomalies, unit-of-measure inconsistencies, or entry errors, which may propagate into Total Sales and Operating Profit analysis.
- **Recommendation**: Audit price outliers against product master data, promotion schedules, and contract pricing. Confirm whether values outside the expected range reflect premium products, pricing exceptions, or incorrect unit pricing. Standardize unit definitions where necessary.

### Outliers detected in Operating Margin (44 records, 0.46%) in a high-importance profitability ratio column.
- **Severity**: medium
- **Impact**: Operating Margin is used to assess efficiency and profitability across products, retailers, and geographies. Even a small number of abnormal ratios can mislead comparative profitability analysis, especially in segment-level reporting where sample sizes are smaller.
- **Recommendation**: Check whether margin outliers are mathematically consistent with Total Sales and Operating Profit. Investigate potential causes such as incorrect profit allocation, unusual discount structures, or formula inconsistencies. Recalculate margins from validated base measures where possible.

