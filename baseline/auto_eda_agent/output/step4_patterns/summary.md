# Pattern Discovery Report

## Summary

- **Total Patterns**: 36
- **Pattern Categories**: 4

## Temporal Patterns

Found 13 patterns:

### Step-change upward in monthly transaction volume from 2020 to 2021
- **Description**: Monthly record counts rise sharply at the start of 2021 and remain at a much higher level throughout 2021 than in 2020.
- **Strength**: strong
- **Variables**: count, Retailer ID, Price per Unit, Units Sold, Total Sales, Operating Profit
- **Relevance**: Any time-based comparison of sums between 2020 and 2021 is heavily influenced by much higher transaction volume in 2021.

### Total Sales sums are consistently much higher in 2021 than in 2020
- **Description**: Monthly total sales show a clear year-over-year level shift upward in 2021 versus 2020.
- **Strength**: strong
- **Variables**: Total Sales
- **Relevance**: Revenue levels are materially higher in 2021, indicating a major change in business scale over time.

### Operating Profit sums are consistently much higher in 2021 than in 2020
- **Description**: Monthly operating profit also shifts to a higher level in 2021 compared with 2020.
- **Strength**: strong
- **Variables**: Operating Profit
- **Relevance**: Profitability in absolute dollars improved substantially in 2021, not just sales.

### Units Sold sums are consistently much higher in 2021 than in 2020
- **Description**: Monthly unit volume rises to a much higher level in 2021 and remains elevated all year.
- **Strength**: strong
- **Variables**: Units Sold
- **Relevance**: The business sold far more units in 2021, supporting the higher sales and profit totals.

### Mid-2020 decline followed by partial rebound in Total Sales
- **Description**: Total Sales fall sharply from spring into early summer 2020, rebound in late summer, then weaken again toward year-end.
- **Strength**: strong
- **Variables**: Total Sales
- **Relevance**: 2020 shows pronounced intra-year volatility, which matters for planning and benchmarking.

## Correlation Patterns

Found 3 patterns:

### Total Sales and Operating Profit move together very strongly
- **Description**: Total Sales and Operating Profit have a very strong positive relationship. Records with higher sales revenue also tend to have higher operating profit. Given the semantic definitions, this relationship is likely largely structural because profit is generated from sales after operating costs, and the relatively bounded Operating Margin distribution supports that profit tends to scale with sales.
- **Strength**: strong
- **Variables**: Total Sales, Operating Profit
- **Relevance**: This indicates that revenue growth is closely tied to profit growth in the dataset. From a business perspective, sales expansion appears to translate into operating profit consistently, making Total Sales a key indicator for profit performance.

### Units Sold is strongly associated with Total Sales
- **Description**: Units Sold and Total Sales show a strong positive relationship. Transactions with more units sold tend to generate higher total sales. This relationship is likely partly structural because sales revenue is directly influenced by quantity sold, though variation in Price per Unit means it is not a perfect one-to-one relationship.
- **Strength**: strong
- **Variables**: Units Sold, Total Sales
- **Relevance**: This suggests sales volume is a major driver of revenue. Operationally, actions that increase unit volume are likely to have a meaningful impact on total sales outcomes.

### Units Sold is strongly associated with Operating Profit
- **Description**: Units Sold and Operating Profit have a strong positive relationship. Records with higher quantities sold tend to produce higher operating profit. This dependency is likely partly structural and partly business-behavioral: more units sold raises revenue, which in turn supports higher profit, while margin variation prevents the relationship from being perfect.
- **Strength**: strong
- **Variables**: Units Sold, Operating Profit
- **Relevance**: This shows that volume growth is not only linked to revenue but also to profitability. Increasing sales quantity appears to be an important lever for improving operating profit in this dataset.

## Grouping Patterns

Found 13 patterns:

### Retailer volume is concentrated in three retailers
- **Description**: Units sold are heavily concentrated in West Gear, Foot Locker, and Sports Direct, while Walmart and Amazon are much smaller by total volume.
- **Strength**: strong
- **Variables**: Retailer, Units Sold
- **Relevance**: This concentration is meaningful because a small set of retailers accounts for most unit volume, so retailer partnerships, inventory allocation, and account management should prioritize these dominant channels.

### Walmart has the highest average units sold per record despite the smallest record count
- **Description**: Walmart stands out as a high-intensity retailer on a per-record basis, even though it has the fewest observations.
- **Strength**: strong
- **Variables**: Retailer, Units Sold, Retailer count
- **Relevance**: This is meaningful because Walmart appears to generate larger orders per record, which may support different replenishment, packaging, or channel strategies than higher-frequency but lower-intensity retailers.

### Amazon has the highest average price per unit among retailers
- **Description**: Average selling price differs across retailers, with Amazon at the top and Sports Direct at the bottom.
- **Strength**: moderate
- **Variables**: Retailer, Price per Unit
- **Relevance**: This matters for pricing and channel strategy because retailer channels are not priced evenly; Amazon supports the highest average unit price while Sports Direct is the lowest-priced among the listed retailers.

### Regional unit volume is led by the West, but per-record intensity is led by the Southeast
- **Description**: The West has the largest total units sold, while the Southeast has the highest average units sold per record.
- **Strength**: strong
- **Variables**: Region, Units Sold
- **Relevance**: This is meaningful because total demand and transaction intensity point to different regions. The West is the largest market by volume, while the Southeast appears to have larger orders per record.

### Price levels are much higher in Southeast and West than in South and Midwest
- **Description**: Regional pricing is uneven, with Southeast and West clearly above South and Midwest on average price per unit.
- **Strength**: strong
- **Variables**: Region, Price per Unit
- **Relevance**: This is meaningful for regional pricing and assortment decisions because the data shows materially different price levels across regions, not a uniform national pricing pattern.

## Anomaly Patterns

Found 7 patterns:

### High-end outliers in Units Sold
- **Description**: Units Sold shows a noticeable upper-tail outlier pattern, with unusually large transaction quantities relative to the central distribution.
- **Strength**: strong
- **Variables**: Units Sold
- **Relevance**: Likely a real business-volume effect rather than a data quality issue, because values are nonnegative and the anomaly is concentrated in the upper tail. Downstream analysis should use robust summaries or winsorization if modeling average transaction size, while preserving these records for demand and large-order analysis.

### Extreme right tail in Total Sales
- **Description**: Total Sales has a strongly uneven distribution with very large high-end values compared with the typical record, indicating revenue spikes or a mixture of small and very large transactions.
- **Strength**: strong
- **Variables**: Total Sales
- **Relevance**: This is more consistent with real sales spikes or heterogeneous transaction sizes than with impossible values, since sales are nonnegative and the tail is on the high side. Use log transforms, robust statistics, or segment-level analysis in downstream work; do not remove by default because these records may represent major revenue events.

### Highly concentrated extreme values in Operating Profit
- **Description**: Operating Profit contains a pronounced concentration of unusually high values, with a heavier tail than Total Sales and a very large gap between typical and average profit.
- **Strength**: strong
- **Variables**: Operating Profit
- **Relevance**: This pattern likely reflects real profit spikes tied to large or high-margin transactions rather than obvious data errors, because values are nonnegative and the tail is one-sided. For downstream analysis, use robust estimators and consider separate treatment of high-profit records in forecasting or profitability segmentation.

### Price per Unit has limited but distinct upper-end price anomalies
- **Description**: Price per Unit is relatively stable overall but includes a small set of unusually high prices above the normal range.
- **Strength**: moderate
- **Variables**: Price per Unit
- **Relevance**: Because the outlier share is small and the overall distribution is fairly centered, these values are more likely premium pricing or product/channel differences than data quality issues. Keep them in analysis, but check whether pricing models should cap or segment high-price records.

### Operating Margin has a small set of boundary-like extreme values
- **Description**: Operating Margin is mostly compact but includes a small number of unusually low and high margin records near the edges of the observed range.
- **Strength**: moderate
- **Variables**: Operating Margin
- **Relevance**: These could be real unusually low- or high-margin transactions, but because margin is a ratio-like measure, edge values should be validated for calculation consistency. Downstream analysis should retain them but consider sensitivity checks, especially in margin benchmarking.

