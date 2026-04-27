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
- **Units Sold**: 6.5% (627 outliers)
- **Price per Unit**: 0.8% (81 outliers)
- **Operating Margin**: 0.5% (44 outliers)

## Critical Issues

### Operating Profit contains 706 outliers (7.32%), which is the highest outlier rate among the high-importance financial columns.
- **Severity**: high
- **Impact**: Operating Profit is a core profitability metric. A high concentration of extreme values can distort profit trend analysis, margin benchmarking, store/product performance comparisons, and executive reporting. If these values are erroneous rather than legitimate business spikes, they may lead to incorrect conclusions about profitability drivers and poor decision-making.
- **Recommendation**: Validate extreme Operating Profit records against source transactions and business rules. Check whether these values are driven by unusually large sales volumes, pricing anomalies, returns, or data entry/calculation errors. If valid, flag them as legitimate extremes; if invalid, correct or exclude them from downstream reporting.

### Total Sales contains 653 outliers (6.77%) in a high-importance revenue column.
- **Severity**: high
- **Impact**: Total Sales directly affects revenue reporting, forecasting, product performance analysis, and regional comparisons. Extreme values may skew averages, trend lines, and aggregated KPIs, especially if they result from incorrect unit counts, pricing errors, or formula issues.
- **Recommendation**: Audit outlier Total Sales records by reconciling them with Price per Unit and Units Sold. Confirm whether the values reflect genuine large transactions or calculation inconsistencies. Implement validation rules to ensure Total Sales aligns with expected sales formulas and transaction limits.

### Units Sold contains 627 outliers (6.50%) in a high-importance volume column.
- **Severity**: high
- **Impact**: Units Sold is foundational for demand analysis, inventory planning, and sales performance measurement. Extreme unit values can mislead demand forecasting, product ranking, replenishment decisions, and operational planning. Because Units Sold also influences Total Sales and Operating Profit, issues here may propagate into multiple downstream metrics.
- **Recommendation**: Review extreme Units Sold records for bulk orders, returns, promotions, or entry errors. Compare suspicious values with invoice-level context, product type, and sales method. Add range and reasonability checks tailored to product and channel.

### Price per Unit contains 81 outliers (0.84%) in a high-importance pricing column, outside the expected range of 5.0 to 85.0.
- **Severity**: medium
- **Impact**: Although the outlier percentage is relatively low, pricing is a critical business field. Abnormal prices can distort revenue calculations, margin analysis, discount effectiveness studies, and product profitability assessments. Even a small number of pricing errors can materially affect high-value transactions.
- **Recommendation**: Investigate whether extreme prices are valid premium/discounted products or data quality issues such as misplaced decimals, currency inconsistencies, or incorrect product-price mappings. Apply product-level pricing validation and exception monitoring.

### Operating Margin contains 44 outliers (0.46%) in a medium-importance profitability ratio column, outside the expected range of 14.0 to 70.0.
- **Severity**: low
- **Impact**: The volume of outliers is small, but unusual margin values can still affect profitability benchmarking and comparative analysis across products, retailers, or regions. Since Operating Margin is often derived from other financial fields, anomalies may indicate either valid business conditions or upstream calculation inconsistencies.
- **Recommendation**: Verify whether Operating Margin is calculated consistently from Total Sales and Operating Profit. Investigate extreme ratios for rounding issues, formula mismatches, or exceptional transactions. Consider recalculating the field from validated source measures where possible.

