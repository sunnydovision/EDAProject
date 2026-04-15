# Pattern Discovery Report

## Summary

- **Total Patterns**: 38
- **Pattern Categories**: 4

## Temporal Patterns

Found 10 patterns:

### Broad step-change upward from 2020 to 2021 in transaction volume and totals
- **Description**: Monthly counts and monthly sums are much higher in every month of 2021 than in the corresponding months of 2020, indicating a clear year-over-year level shift rather than a small gradual increase.
- **Strength**: strong
- **Variables**: Total Sales, Operating Profit, Units Sold, count
- **Relevance**: This indicates the business operated at a much larger monthly scale in 2021, affecting capacity planning, forecasting, and interpretation of year-over-year performance.

### 2020 mid-year trough followed by partial rebound
- **Description**: In 2020, several key metrics decline from early-year levels into June, then recover in July through September before weakening again late in the year.
- **Strength**: strong
- **Variables**: Total Sales, Operating Profit, Units Sold, count
- **Relevance**: This shows a clear within-year disruption and rebound pattern in 2020, useful for identifying abnormal periods and avoiding misleading trend baselines.

### 2021 sales and profit trough in March, then climb to summer peak
- **Description**: In 2021, Total Sales and Operating Profit decline from January to March, then rise through spring and early summer, reaching their highest levels around July-August before easing in autumn.
- **Strength**: strong
- **Variables**: Total Sales, Operating Profit
- **Relevance**: This seasonal-like rise into summer and decline into autumn can inform staffing, inventory, and promotional timing.

### Units sold peak in late summer in both years
- **Description**: The highest monthly Units Sold sums occur in August in both 2020 and 2021, indicating a repeated late-summer volume high.
- **Strength**: moderate
- **Variables**: Units Sold
- **Relevance**: A repeated August volume peak suggests planning for higher fulfillment and inventory needs in late summer.

### Late-year recovery in 2021 after autumn slowdown
- **Description**: After declining from summer into October 2021, sales and profit recover in November and especially December.
- **Strength**: strong
- **Variables**: Total Sales, Operating Profit, Units Sold, Price per Unit
- **Relevance**: This suggests year-end strengthening in 2021, relevant for revenue targeting and end-of-year commercial planning.

## Correlation Patterns

Found 3 patterns:

### Total Sales and Operating Profit move together very strongly
- **Description**: Total Sales and Operating Profit have a very strong positive relationship: records with higher sales tend to also show higher operating profit. This is likely partly structural because profit is financially linked to sales, though the relationship is not perfect, indicating margins or cost structure vary across records.
- **Strength**: strong
- **Variables**: Total Sales, Operating Profit
- **Relevance**: Revenue growth is closely associated with profit growth in this dataset. From a business perspective, higher-revenue transactions are also the main source of higher operating profit. Because Operating Profit is economically dependent on Total Sales, this relationship is likely substantially structural rather than purely behavioral.

### Units Sold is strongly associated with Total Sales
- **Description**: Units Sold and Total Sales show a strong positive relationship: transactions with more units sold generally produce higher total sales. This is consistent with the revenue structure of sales data, since selling more units typically increases revenue, although variation in Price per Unit prevents the relationship from being perfect.
- **Strength**: strong
- **Variables**: Units Sold, Total Sales
- **Relevance**: Volume is a major driver of revenue in the dataset. This relationship is likely largely structural because Total Sales is directly influenced by quantity sold, but it also reflects business performance differences across transactions because price levels vary.

### Units Sold is strongly associated with Operating Profit
- **Description**: Units Sold and Operating Profit have a strong positive relationship: higher-volume transactions tend to generate higher operating profit. This likely reflects a dependency chain where selling more units raises sales, which in turn raises profit, subject to margin differences.
- **Strength**: strong
- **Variables**: Units Sold, Operating Profit
- **Relevance**: Sales volume appears to be an important contributor to profitability. This relationship is partly structural rather than purely behavioral, because Operating Profit is financially downstream of sales volume through Total Sales, but the less-than-perfect correlation shows that profit per unit and operating margin vary.

## Grouping Patterns

Found 18 patterns:

### Retailer transaction volume is concentrated in three chains
- **Description**: Record counts are uneven across retailers, with Foot Locker, West Gear, and Sports Direct accounting for most observations.
- **Strength**: strong
- **Variables**: Retailer, count
- **Relevance**: High. Any retailer-level analysis will be dominated by Foot Locker, West Gear, and Sports Direct, so decisions based on aggregate retailer performance should account for this imbalance.

### Walmart has the highest average units sold per record despite the smallest retailer count
- **Description**: Retailers differ meaningfully in average units sold, and Walmart leads on units per record even though it has the fewest records.
- **Strength**: strong
- **Variables**: Retailer, Units Sold, count
- **Relevance**: High. Walmart appears to generate larger order quantities per record, which matters for fulfillment, inventory allocation, and channel strategy.

### Foot Locker and West Gear dominate total units sold among retailers
- **Description**: Total units sold are concentrated in two retailers, driven by their larger record counts.
- **Strength**: strong
- **Variables**: Retailer, Units Sold, count
- **Relevance**: High. Volume planning and retailer prioritization should focus heavily on West Gear and Foot Locker because they carry the largest total unit movement.

### Amazon has the highest average price per unit among retailers
- **Description**: Average selling price differs across retailers, with Amazon at the top and Sports Direct at the bottom.
- **Strength**: moderate
- **Variables**: Retailer, Price per Unit
- **Relevance**: Moderate to high. Retailers appear to operate at different price points, which is relevant for pricing strategy, promotion planning, and margin comparisons.

### Regional record counts are concentrated in West and Northeast
- **Description**: The number of records is uneven by region, with West and Northeast having the largest counts and Southeast the smallest.
- **Strength**: strong
- **Variables**: Region, count
- **Relevance**: High. Geographic analyses are balanced toward West and Northeast, so these regions will strongly influence overall results.

## Anomaly Patterns

Found 7 patterns:

### High-end outliers in Units Sold
- **Description**: Units Sold shows a noticeable upper-tail anomaly pattern, with unusually large transaction quantities relative to the central distribution.
- **Strength**: strong
- **Variables**: Units Sold
- **Relevance**: This is more consistent with real high-volume sales events than a clear data quality issue because values are nonnegative and the upper-tail pattern aligns with positive skew. In downstream analysis, use robust summaries (median, IQR), consider winsorizing or segmenting bulk-sale records, and test whether these records correspond to specific products, channels, or periods.

### Extreme right tail in Total Sales
- **Description**: Total Sales has a strongly concentrated lower/middle range with a very large upper tail, indicating revenue spikes or very large orders.
- **Strength**: strong
- **Variables**: Total Sales
- **Relevance**: This could reflect real large transactions, but the very large mean-median gap indicates that aggregate results will be dominated by a small subset of records. Downstream analysis should use log scaling or robust statistics, and analysts should separately profile these high-sales records before modeling or benchmarking.

### Extreme right tail in Operating Profit
- **Description**: Operating Profit contains a pronounced set of unusually high values, more extreme than the sales distribution, indicating profit spikes concentrated in a minority of records.
- **Strength**: strong
- **Variables**: Operating Profit
- **Relevance**: This likely reflects real highly profitable transactions or combinations of high sales and high margin, rather than obvious data error, because values remain nonnegative. For downstream work, use robust estimators, inspect these records separately, and avoid relying only on averages when comparing profitability across groups.

### Zero-inflation at the lower bound in sales and profit measures
- **Description**: Both Total Sales and Operating Profit have exact zeros as their minimum values, creating a lower-bound mass that is unusual for continuous monetary measures and may indicate no-sale, canceled, or placeholder records.
- **Strength**: moderate
- **Variables**: Total Sales, Operating Profit, Units Sold
- **Relevance**: This could be either a real business state (no units sold / no revenue / no profit) or a data quality/process artifact. Downstream analysis should explicitly quantify zero counts, treat zero-valued records as a separate segment, and verify whether they represent valid transactions before including them in revenue or margin modeling.

### Mild upper-tail anomalies in Price per Unit
- **Description**: Price per Unit has some unusually high values, but the anomaly rate is low and the distribution is much more stable than the volume and monetary measures.
- **Strength**: moderate
- **Variables**: Price per Unit
- **Relevance**: These high prices may be legitimate premium-price transactions rather than data errors, since the lower bound is not violated and the central tendency is stable. In downstream analysis, keep these values but consider capping or separate segmentation if price-sensitive models are affected by the small number of high-price records.

