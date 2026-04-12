# Statistical Analysis Report

## Summary

- **Numerical Columns**: 6
- **Categorical Columns**: 7
- **Strong Correlations**: 3

## Key Findings

- Revenue and profit distributions are highly concentrated in a relatively small number of very large transactions, so mean-based summaries materially overstate the typical transaction size and profitability.
- Operating Margin is comparatively stable while Total Sales and Operating Profit are highly volatile, implying that transaction size and volume are the main drivers of financial variation rather than dramatic differences in margin rate.
- The strongest relationships are structural: units drive sales, and sales drive profit. This means business comparisons across retailers, products, or channels should normalize for transaction size before interpreting performance differences.

## Strong Correlations

### Units Sold and Total Sales
- **Strength**: strong
- **Interpretation**: This strong positive relationship (r=0.845) means higher unit volume is closely associated with higher revenue, which is expected because sales dollars are mechanically driven by quantity times price. This is primarily a structural relationship rather than a behavioral one. The fact that the correlation is not even higher suggests price variation across products, channels, or retailers meaningfully affects revenue in addition to volume.

### Units Sold and Operating Profit
- **Strength**: strong
- **Interpretation**: This strong positive relationship (r=0.814) indicates that larger-quantity transactions tend to generate more operating profit. This is partly structural, since more units usually create more gross contribution, but it may also reflect behavioral/business effects such as certain high-volume channels or retailers being more profitable. Because profit is also shaped by margin differences, the correlation being lower than sales-profit correlation suggests that not all volume converts equally well into profit.

### Total Sales and Operating Profit
- **Strength**: strong
- **Interpretation**: This very strong positive relationship (r=0.956) shows that revenue and operating profit move almost in lockstep. This is largely structural because profit is derived from sales through margin assumptions. In business terms, this suggests that differences in profit are driven much more by transaction size than by large swings in margin percentage. It also means any analysis of profit drivers should control for sales size before concluding that a retailer, region, or product is inherently more profitable.

