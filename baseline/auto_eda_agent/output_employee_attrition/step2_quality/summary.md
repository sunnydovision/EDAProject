# Data Quality Report

## Summary

- **Total Issues**: 10
- **Critical Issues**: 10
- **Quality Score**: 82/100

## Missing Values

No missing values detected.

## Outliers

- **TrainingTimesLastYear**: 16.2% (238 outliers)
- **PerformanceRating**: 15.4% (226 outliers)
- **MonthlyIncome**: 7.8% (114 outliers)
- **YearsSinceLastPromotion**: 7.3% (107 outliers)
- **YearsAtCompany**: 7.1% (104 outliers)
- **StockOptionLevel**: 5.8% (85 outliers)
- **TotalWorkingYears**: 4.3% (63 outliers)
- **NumCompaniesWorked**: 3.5% (52 outliers)
- **YearsInCurrentRole**: 1.4% (21 outliers)
- **YearsWithCurrManager**: 1.0% (14 outliers)

## Critical Issues

### Outliers detected in PerformanceRating (226 records, 15.37%). The IQR method flags all values outside 3.0, indicating the variable is highly concentrated and likely discrete/ordinal rather than truly anomalous.
- **Severity**: medium
- **Impact**: Because PerformanceRating is a medium-importance feature, treating these values as errors could distort performance-related segmentation, employee evaluation analysis, and any models using rating as a predictor. The issue is more about inappropriate outlier detection than clear data corruption.
- **Recommendation**: Do not automatically remove these records. Validate the allowed rating scale from business rules and assess frequency distribution instead of using continuous-variable outlier logic for this ordinal field.

### Outliers detected in TrainingTimesLastYear (238 records, 16.19%). This is a medium-importance count variable with a large share of values outside the IQR bounds.
- **Severity**: medium
- **Impact**: If these values are valid, they may represent meaningful variation in employee development activity. If invalid, they can bias workforce development reporting and any attrition or performance models that use training frequency.
- **Recommendation**: Validate against expected business limits for annual training counts. Use rule-based checks for count variables and consider capping or categorizing only if values are confirmed implausible.

### Outliers detected in MonthlyIncome (114 records, 7.76%) in a high-importance column.
- **Severity**: high
- **Impact**: MonthlyIncome is central to compensation analysis, pay equity studies, attrition modeling, and workforce planning. Extreme values can skew averages, inflate variance, and mislead compensation benchmarking or predictive models.
- **Recommendation**: Review extreme salary records against payroll source systems. Confirm whether they reflect valid executive/high-pay roles or data entry issues. Apply winsorization, segmentation by job level, or robust statistics if values are valid but influential.

### Outliers detected in TotalWorkingYears (63 records, 4.29%) in a high-importance column.
- **Severity**: high
- **Impact**: This field is important for tenure, experience, promotion, and attrition analysis. Implausible experience values can distort workforce seniority distributions and weaken models that rely on career-stage indicators.
- **Recommendation**: Cross-check against Age and YearsAtCompany for logical consistency. Investigate unusually high values and apply business-rule validation such as TotalWorkingYears <= Age - minimum working age.

### Outliers detected in YearsAtCompany (104 records, 7.07%) in a medium-importance tenure field.
- **Severity**: medium
- **Impact**: Extreme tenure values can bias retention analysis, internal mobility studies, and tenure-based segmentation. They may also indicate inconsistencies when compared with TotalWorkingYears.
- **Recommendation**: Validate against employment history and enforce consistency rules such as YearsAtCompany <= TotalWorkingYears.

