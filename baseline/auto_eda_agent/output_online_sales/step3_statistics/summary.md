# Statistical Analysis Report

## Summary

- **Numerical Columns**: 4
- **Categorical Columns**: 5
- **Strong Correlations**: 1

## Key Findings

- Typical order sizes are small: the median Units Sold is 2 and the middle 50% of transactions fall between 1 and 3 units, indicating most sales are low-quantity retail purchases rather than bulk orders.
- Price and revenue distributions are heavily influenced by a small number of high-value items, so mean Unit Price and mean Total Revenue overstate the typical transaction compared with the medians.
- Category and regional counts are perfectly balanced, which is statistically unusual for real-world sales data and suggests the dataset may be designed, quota-sampled, or otherwise not fully representative of natural business demand.

## Strong Correlations

### Unit Price and Total Revenue
- **Strength**: strong
- **Interpretation**: There is a very strong positive relationship (r = 0.93), meaning higher-priced items tend to generate higher transaction-line revenue. In business terms, revenue variation is being driven more by what product price tier was sold than by large variation in quantity purchased. This is likely a structural relationship rather than a behavioral one, because Total Revenue is likely mechanically calculated from Unit Price multiplied by Units Sold. The strength of the correlation is therefore expected and should not be over-interpreted as an independent customer behavior pattern.

