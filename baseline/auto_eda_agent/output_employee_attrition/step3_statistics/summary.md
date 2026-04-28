# Statistical Analysis Report

## Summary

- **Numerical Columns**: 26
- **Categorical Columns**: 6
- **Strong Correlations**: 7

## Key Findings

- The organization has a classic hierarchical workforce structure: most employees are in lower job levels, while income and experience rise sharply with level, making JobLevel the central structural driver of compensation.
- Typical employees report moderately positive workplace conditions—job satisfaction, environment satisfaction, relationship satisfaction, job involvement, and work-life balance all center around 3 on 1-4 scales—so the dataset does not show broad dissatisfaction at the aggregate level.
- Tenure and career-history variables are heavily right-skewed with outliers, indicating a workforce made up mostly of shorter- to mid-tenure employees plus a smaller but important group of very long-tenured employees who can materially affect averages.

## Strong Correlations

### JobLevel and MonthlyIncome
- **Strength**: strong
- **Interpretation**: This is an extremely strong positive relationship (r=0.95): higher job grades are associated with much higher monthly income. This is almost certainly structural, reflecting compensation bands tied to organizational level rather than employee behavior. It also means these two variables are largely redundant in modeling unless the goal is specifically to separate level effects from pay effects.

### JobLevel and TotalWorkingYears
- **Strength**: strong
- **Interpretation**: Employees with more total career experience tend to be in higher job levels (r=0.78). This is mostly structural, since promotion systems often reward accumulated experience, though some behavioral and talent effects may also contribute. It suggests seniority and experience are closely linked in this workforce.

### MonthlyIncome and TotalWorkingYears
- **Strength**: strong
- **Interpretation**: More experienced employees tend to earn more (r=0.77). This is expected in HR data and is likely primarily structural through pay progression and promotion ladders. Because JobLevel is also strongly tied to both variables, much of this relationship may be mediated by level rather than pure tenure alone.

### PercentSalaryHike and PerformanceRating
- **Strength**: strong
- **Interpretation**: Employees with higher performance ratings receive larger salary increases (r=0.77). This appears structural, likely reflecting compensation policy that links raises to performance review outcomes. However, because PerformanceRating is highly compressed at 3 and 4 only, the correlation may reflect a simple rule-based distinction rather than nuanced performance differentiation.

### YearsAtCompany and YearsInCurrentRole
- **Strength**: strong
- **Interpretation**: Longer-tenured employees have generally spent more time in their current role (r=0.76). This is partly structural because role tenure cannot exceed company tenure, but it is also behaviorally informative: many employees appear to remain in the same role for substantial portions of their tenure, which may indicate stability or limited internal mobility.

### YearsAtCompany and YearsWithCurrManager
- **Strength**: strong
- **Interpretation**: Employees who have been at the company longer also tend to have spent longer with their current manager (r=0.77). This is partly structural, but it may also indicate relatively stable reporting relationships in parts of the organization. In some contexts this could be positive continuity; in others it could signal low managerial rotation or stagnant team structures.

### YearsInCurrentRole and YearsWithCurrManager
- **Strength**: strong
- **Interpretation**: Employees who have been in their role longer also tend to have had the same manager longer (r=0.71). This is a mix of structural and organizational behavior: role changes often trigger manager changes, and stable roles often come with stable supervision. It may indicate that role mobility and manager mobility are tightly linked.

