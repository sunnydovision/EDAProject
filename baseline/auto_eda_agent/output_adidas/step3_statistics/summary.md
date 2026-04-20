# Statistical Analysis Report

## Summary

- **Numerical Columns**: 6
- **Categorical Columns**: 7
- **Strong Correlations**: 3

## Key Findings

- Sales and profit are highly concentrated in a relatively small number of records: both Total Sales and Operating Profit have means far above medians and strong right tails, so average performance overstates what a typical transaction looks like.
- Operating Margin is comparatively stable despite extreme variation in sales and profit dollars, implying that the business may have fairly consistent margin structures while transaction size varies dramatically.
- The dataset appears operationally balanced across products but not across channels or retailers: product counts are nearly even across the 6 product groups, while Online dominates sales records and Foot Locker/West Gear account for a large share of observations.

## Strong Correlations

### Units Sold and Total Sales
- **Strength**: strong
- **Interpretation**: This strong positive relationship means higher-volume transactions generally produce higher revenue, which is expected because total sales are mechanically influenced by quantity sold. This is primarily structural rather than behavioral, since Total Sales is largely determined by Units Sold multiplied by Price per Unit. Any deviation from a near-perfect relationship likely reflects variation in unit prices across products and transactions.

### Units Sold and Operating Profit
- **Strength**: strong
- **Interpretation**: This strong positive relationship indicates that larger-quantity transactions tend to generate more operating profit in absolute dollars. This is partly structural because more units usually create more gross revenue and therefore more profit dollars, but it may also contain behavioral effects if high-volume sales are concentrated in products, retailers, or channels with systematically different margins.

### Total Sales and Operating Profit
- **Strength**: strong
- **Interpretation**: This is the strongest relationship in the dataset and indicates that higher-revenue transactions almost always correspond to higher operating profit. This is largely structural because operating profit is derived from sales after costs, so profit dollars should rise with revenue. The fact that the correlation is very high but not perfect suggests margin differences across products, retailers, regions, or sales methods.

