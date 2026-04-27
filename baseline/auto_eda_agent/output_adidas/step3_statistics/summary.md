# Statistical Analysis Report

## Summary

- **Numerical Columns**: 6
- **Categorical Columns**: 7
- **Strong Correlations**: 3

## Key Findings

- Revenue and profit distributions are highly concentrated in a minority of very large records, so mean sales and mean profit substantially overstate a typical transaction.
- Operating Margin is comparatively stable around the low-40% range, suggesting profitability rates are more consistent than absolute sales or profit dollars.
- The strongest relationships are structural: units drive sales, and sales drive profit, indicating transaction scale is the dominant statistical pattern in the dataset.

## Strong Correlations

### Units Sold and Total Sales
- **Strength**: strong
- **Interpretation**: This strong positive relationship (r=0.845) means higher-volume records generally produce higher revenue, which is expected because Total Sales is mechanically influenced by quantity sold. This is primarily structural rather than behavioral, since sales dollars are mathematically tied to units and price. Any deviation from this relationship would likely reflect pricing differences across products, channels, or discounting.

### Units Sold and Operating Profit
- **Strength**: strong
- **Interpretation**: This strong positive relationship (r=0.814) indicates that larger-volume sales tend to generate more operating profit. This is partly structural because more units usually create more gross revenue and therefore more profit dollars, but it also has a behavioral component if certain channels or products scale more profitably than others. Follow-up should test whether high-volume records also have systematically higher or lower margins.

### Total Sales and Operating Profit
- **Strength**: strong
- **Interpretation**: This very strong positive relationship (r=0.956) shows that profit dollars rise almost directly with revenue. This is largely structural because Operating Profit is derived from Total Sales after costs, and the relatively stable Operating Margin reinforces that profit is closely tied to sales size. From a business perspective, revenue growth appears to be the main driver of profit growth in this dataset.

