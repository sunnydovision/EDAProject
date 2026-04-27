# Data Quality Report

## Summary

- **Total Issues**: 3
- **Critical Issues**: 3
- **Quality Score**: 78/100

## Missing Values

No missing values detected.

## Outliers

- **Unit Price**: 10.0% (24 outliers)
- **Total Revenue**: 7.9% (19 outliers)
- **Units Sold**: 0.4% (1 outliers)

## Critical Issues

### Outlier detected in 'Units Sold' (1 record, 0.42%) in a high-importance column. The value falls outside the expected range based on profiling bounds (-2.0 to 6.0).
- **Severity**: medium
- **Impact**: Because 'Units Sold' is a core transactional measure, even a small number of anomalous values can distort average sales volume, demand patterns, inventory planning, and product performance analysis. The low frequency limits overall impact, but the column's business importance makes it worth review.
- **Recommendation**: Manually inspect the flagged record against source transactions. Confirm whether it reflects a legitimate bulk sale or a data entry/calculation issue. If invalid, correct or exclude it from analytical aggregates.

### High number of outliers in 'Unit Price' (24 records, 10.0%) in a high-importance column. Although the statistical lower bound is negative and therefore not inherently invalid, the proportion of unusual values is significant.
- **Severity**: high
- **Impact**: Unit price is a key driver of revenue, margin, pricing analysis, and product benchmarking. A 10% outlier rate can materially skew average selling price, pricing strategy assessments, discount analysis, and profitability reporting. If these values are errors, downstream financial insights may be misleading.
- **Recommendation**: Validate outlier prices against product master data, pricing rules, and promotional/discount records. Separate legitimate premium/discounted transactions from erroneous entries. Apply business-rule validation such as non-negative price checks and expected price ranges by product category.

### Substantial outliers in 'Total Revenue' (19 records, 7.92%) in a high-importance column, indicating potentially inconsistent transaction totals or legitimate extreme sales values.
- **Severity**: high
- **Impact**: Total revenue is a primary financial metric. Outliers in this field can distort revenue trends, regional performance comparisons, forecasting, and executive reporting. They may also indicate inconsistency between 'Units Sold', 'Unit Price', and 'Total Revenue', which would undermine trust in the dataset.
- **Recommendation**: Recalculate 'Total Revenue' from 'Units Sold × Unit Price' and compare against recorded values. Investigate mismatches, rounding issues, returns, bundled sales, or data entry errors. Establish reconciliation checks to ensure transactional consistency.

