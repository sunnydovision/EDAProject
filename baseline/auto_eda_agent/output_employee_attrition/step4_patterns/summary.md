# Pattern Discovery Report

## Summary

- **Total Patterns**: 29
- **Pattern Categories**: 3

## Correlation Patterns

Found 7 patterns:

### Job level and monthly income move together very strongly
- **Description**: Employees at higher job levels tend to have substantially higher monthly income. This is the strongest relationship in the provided results and is consistent with compensation increasing with seniority/grade.
- **Strength**: strong
- **Variables**: JobLevel, MonthlyIncome
- **Relevance**: This indicates compensation is closely aligned with organizational level. JobLevel is a strong proxy for pay and should be treated as highly overlapping with MonthlyIncome in analysis or modeling.

### Job level rises with total working experience
- **Description**: Employees with more total working years tend to be in higher job levels. The relationship suggests seniority in role hierarchy is associated with accumulated career experience.
- **Strength**: strong
- **Variables**: JobLevel, TotalWorkingYears
- **Relevance**: Experience is strongly associated with seniority level. Workforce planning and promotion analysis should account for the close linkage between tenure in the labor market and internal grade.

### Monthly income increases with total working experience
- **Description**: Employees with more total working years tend to earn higher monthly income. This suggests compensation grows with accumulated experience.
- **Strength**: strong
- **Variables**: MonthlyIncome, TotalWorkingYears
- **Relevance**: Experience is strongly tied to pay. Compensation benchmarking and equity reviews should consider TotalWorkingYears because it co-moves strongly with income.

### Salary hike and performance rating are tightly linked
- **Description**: Employees with higher performance ratings tend to receive larger percentage salary hikes. The two variables move together strongly.
- **Strength**: strong
- **Variables**: PercentSalaryHike, PerformanceRating
- **Relevance**: Pay increase decisions appear closely connected to performance evaluation outcomes. This is important for understanding reward policy consistency and for avoiding double-counting similar signals in models.

### Years at company and years in current role move together
- **Description**: Employees who have been at the company longer also tend to have spent more years in their current role. Time in company and time in role are strongly aligned.
- **Strength**: strong
- **Variables**: YearsAtCompany, YearsInCurrentRole
- **Relevance**: Internal tenure is closely related to role tenure. Analyses of mobility, stagnation, or promotion timing should recognize that these variables carry overlapping information.

## Grouping Patterns

Found 11 patterns:

### BusinessTravel is heavily concentrated in Travel_Rarely
- **Description**: The BusinessTravel distribution is highly uneven, with most employees in the Travel_Rarely segment.
- **Strength**: strong
- **Variables**: BusinessTravel
- **Relevance**: Strongly relevant for staffing, policy, and travel-program decisions because the dominant employee segment is Travel_Rarely, so company-wide travel policies will mostly affect this group.

### Department headcount is dominated by Research & Development
- **Description**: Department membership is highly skewed toward Research & Development, with Sales a distant second and Human Resources much smaller.
- **Strength**: strong
- **Variables**: Department
- **Relevance**: Highly relevant because department-level planning, budgeting, and change management will be driven primarily by Research & Development due to its much larger population.

### EducationField is concentrated in Life Sciences and Medical
- **Description**: Two education fields account for most employees, while several other fields are much smaller.
- **Strength**: strong
- **Variables**: EducationField
- **Relevance**: Relevant for recruiting, training, and talent pipeline decisions because the workforce is concentrated in a small number of academic backgrounds.

### Gender distribution is male-skewed
- **Description**: The workforce has more male employees than female employees.
- **Strength**: moderate
- **Variables**: Gender
- **Relevance**: Relevant for workforce composition monitoring and diversity reporting, though the imbalance is less extreme than some other category skews in the dataset.

### JobRole headcount is concentrated in Sales Executive and Research Scientist
- **Description**: Among job roles, a few roles hold much larger employee counts than the rest.
- **Strength**: strong
- **Variables**: JobRole
- **Relevance**: Relevant for role-based workforce planning because hiring, retention, and training efforts will have the broadest impact in these large roles.

## Anomaly Patterns

Found 11 patterns:

### Constant-value administrative fields
- **Description**: Some variables have no variation at all, which is anomalous for analytical modeling because they carry no discriminatory information.
- **Strength**: strong
- **Variables**: EmployeeCount, StandardHours
- **Relevance**: This is most likely a data design or placeholder issue rather than a real business event. In downstream analysis, these columns should usually be dropped because they contain no signal and can distort feature screening or automated anomaly detection.

### Degenerate two-point performance distribution with IQR-based outlier inflation
- **Description**: PerformanceRating is concentrated almost entirely at one value, causing the higher category to be flagged as outliers by the IQR rule even though it appears to be a valid category.
- **Strength**: strong
- **Variables**: PerformanceRating
- **Relevance**: This is unlikely to be a data quality error; it is more consistent with a highly compressed rating system. For downstream analysis, do not treat the flagged 4s as erroneous outliers. Handle this as a low-cardinality ordinal variable, and avoid generic IQR-based outlier removal on such fields.

### Compressed training-count distribution with boundary values flagged as outliers
- **Description**: TrainingTimesLastYear has a narrow central range, so low and high valid counts are flagged as outliers by the IQR rule.
- **Strength**: strong
- **Variables**: TrainingTimesLastYear
- **Relevance**: This looks more like a real business distribution with discrete counts than a data quality issue. In downstream analysis, keep the values but treat the variable as a bounded count/ordinal feature. Avoid deleting these observations solely because of IQR flags.

### High-income right tail
- **Description**: MonthlyIncome shows a pronounced right-skewed distribution with a substantial upper tail and a nontrivial share of high-end outliers.
- **Strength**: strong
- **Variables**: MonthlyIncome
- **Relevance**: This is more likely a real compensation structure effect, such as senior or specialized roles, than a data error. For downstream analysis, retain the values but consider log transformation, robust scaling, or winsorization if using methods sensitive to skew and leverage.

### Tenure at company has an extreme upper tail
- **Description**: YearsAtCompany is strongly right-skewed with unusually long tenure values relative to the central distribution.
- **Strength**: strong
- **Variables**: YearsAtCompany
- **Relevance**: This likely reflects a real long-tenure subgroup rather than bad data, though the max of 40 years is operationally extreme and worth validation if employee ages are later cross-checked. For downstream analysis, keep the field but use robust methods or cap extreme values if model stability is a concern.

