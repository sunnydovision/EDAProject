# Statistical Analysis Report

## Summary

- **Numerical Columns**: 6
- **Categorical Columns**: 7
- **Strong Correlations**: 3

## Key Findings

- Revenue and profit are highly concentrated in a relatively small number of large records, as shown by the extreme right skew and the large mean-median gaps for Total Sales and Operating Profit.
- Operating Margin is much more stable than dollar-based measures, suggesting that differences in business performance are driven more by transaction size and volume than by large swings in percentage profitability.
- The strongest correlations are largely structural: Units Sold drives Total Sales, and Total Sales drives Operating Profit, so raw correlations alone should not be overinterpreted as evidence of causal business behavior.

## Strong Correlations

### Units Sold and Total Sales
- **Strength**: strong
- **Interpretation**: This very strong positive relationship (r=0.91) means higher-volume records almost always generate higher revenue. In business terms, sales dollars are driven primarily by quantity sold, which is expected because Total Sales is mechanically influenced by Units Sold multiplied by price. This is mostly a structural relationship rather than a behavioral insight, although deviations from the pattern could still reveal pricing differences across products or channels.

### Units Sold and Operating Profit
- **Strength**: strong
- **Interpretation**: This strong positive relationship (r=0.89) indicates that larger-volume sales tend to produce larger profit dollars. Business-wise, profit growth appears to come largely from selling more units rather than from unusually high margins on small orders. This is partly structural because more units generally create more revenue and therefore more profit, but it may also reflect behavioral patterns if certain channels or retailers are especially effective at converting volume into profit.

### Total Sales and Operating Profit
- **Strength**: strong
- **Interpretation**: This is the strongest relationship in the dataset (r=0.96), showing that profit scales very closely with revenue. That is highly expected because Operating Profit is derived from Total Sales through margin. This is overwhelmingly structural, not surprising evidence of business performance by itself. The more useful business question is where records sit above or below the expected profit-for-sales line, which would indicate unusually high or low margins by product, retailer, region, or sales method.

