# Pattern Discovery Report

## Summary

- **Total Patterns**: 40
- **Pattern Categories**: 4

## Temporal Patterns

Found 13 patterns:

### Sharp year-over-year step-up in transaction volume in 2021
- **Description**: Monthly record counts rise sharply from 2020 to 2021 and remain consistently high throughout 2021.
- **Strength**: strong
- **Variables**: count, Retailer ID, Price per Unit, Units Sold, Total Sales, Operating Profit
- **Relevance**: Any time-based comparison of sums between 2020 and 2021 is heavily influenced by much higher transaction volume in 2021.

### Total Sales sums are much higher in every month of 2021 than the same month in 2020
- **Description**: Monthly Total Sales show a clear year-over-year increase across the full calendar year.
- **Strength**: strong
- **Variables**: Total Sales
- **Relevance**: Revenue expanded materially year over year, indicating a much larger sales base in 2021.

### Operating Profit sums are much higher in every month of 2021 than the same month in 2020
- **Description**: Monthly Operating Profit follows the same year-over-year expansion pattern as Total Sales.
- **Strength**: strong
- **Variables**: Operating Profit
- **Relevance**: Profitability in absolute dollars increased substantially year over year.

### Units Sold sums are much higher in every month of 2021 than the same month in 2020
- **Description**: Monthly unit volume increases consistently from 2020 to 2021 across all matched months.
- **Strength**: strong
- **Variables**: Units Sold
- **Relevance**: The revenue and profit increase is accompanied by substantially higher unit movement.

### 2020 mid-year decline followed by partial recovery in Total Sales
- **Description**: In 2020, Total Sales fall sharply from spring into early summer, recover in late summer, then weaken again toward year-end.
- **Strength**: strong
- **Variables**: Total Sales
- **Relevance**: 2020 shows pronounced within-year volatility, which may matter for planning and benchmarking.

## Correlation Patterns

Found 3 patterns:

### Total Sales and Operating Profit move together very strongly
- **Description**: Total Sales and Operating Profit have a very strong positive relationship: records with higher sales tend to also show higher operating profit. This is likely largely structural because profit is financially tied to sales, though the less-than-perfect correlation indicates margins or cost structure vary across records.
- **Strength**: strong
- **Variables**: Total Sales, Operating Profit
- **Relevance**: This suggests revenue growth is closely associated with profit growth in the dataset. From a business perspective, sales expansion appears to translate into higher operating profit, but not perfectly, implying margin differences across products, channels, or transactions.

### Units Sold strongly co-moves with Total Sales
- **Description**: Units Sold and Total Sales show a strong positive relationship: transactions with more units sold generally produce higher total sales. This relationship is likely structural because sales revenue is directly influenced by quantity sold, together with price per unit.
- **Strength**: strong
- **Variables**: Units Sold, Total Sales
- **Relevance**: Volume is a major driver of revenue in this dataset. Increasing units sold is strongly linked to higher sales outcomes, which is useful for forecasting and for identifying volume-led growth opportunities.

### Units Sold strongly co-moves with Operating Profit
- **Description**: Units Sold and Operating Profit have a strong positive relationship: records with higher sales volume tend to generate higher operating profit. This is partly structural because more units sold tends to raise sales, which in turn supports profit, though profitability per unit is not constant.
- **Strength**: strong
- **Variables**: Units Sold, Operating Profit
- **Relevance**: Sales volume appears to be an important profit driver. Operationally, this means initiatives that increase unit throughput are likely to improve profit, although the correlation being lower than Sales-Profit suggests margins and pricing still matter.

## Grouping Patterns

Found 17 patterns:

### Retailer transaction volume is concentrated in three retailers
- **Description**: Foot Locker, West Gear, and Sports Direct dominate the dataset by record count, while Walmart and Amazon have much smaller representation.
- **Strength**: strong
- **Variables**: Retailer, count
- **Relevance**: High. Any retailer-level analysis or planning will be heavily influenced by these three retailers, so they should be prioritized for segmentation, forecasting, and partnership decisions.

### West Gear and Foot Locker lead total units sold, but Walmart leads per-record unit volume
- **Description**: The dominant retailers differ depending on whether total volume or average volume per record is considered.
- **Strength**: strong
- **Variables**: Retailer, Units Sold
- **Relevance**: High. West Gear and Foot Locker matter most for aggregate volume, while Walmart appears to generate larger orders per record, which may call for different inventory and channel strategies.

### Amazon has the highest average price per unit among retailers
- **Description**: Retailer pricing levels are uneven, with Amazon at the top and Sports Direct at the bottom on average price per unit.
- **Strength**: moderate
- **Variables**: Retailer, Price per Unit
- **Relevance**: Moderate to high. This indicates retailer-level pricing differences that may affect positioning, margin expectations, and promotional planning.

### Regional record counts are concentrated in West and Northeast
- **Description**: The West and Northeast have the largest number of records, while the Southeast has the smallest.
- **Strength**: strong
- **Variables**: Region, count
- **Relevance**: High. Coverage, staffing, and market analysis will be disproportionately driven by West and Northeast activity.

### Southeast has the highest average units sold per record despite the fewest records
- **Description**: The Southeast is underrepresented in record count but leads all regions in average units sold per record.
- **Strength**: strong
- **Variables**: Region, Units Sold, count
- **Relevance**: High. The Southeast appears to produce larger transactions on average, which is important for inventory allocation and sales strategy even though it has fewer records.

## Anomaly Patterns

Found 7 patterns:

### Heavy right-tail outliers in Operating Profit
- **Description**: Operating Profit shows a pronounced concentration of unusually high values relative to its central range, indicating a heavy right tail.
- **Strength**: strong
- **Variables**: Operating Profit
- **Relevance**: This is more consistent with real business concentration in a subset of records than random noise, because multiple statistics align in the same direction. Downstream analysis should use robust summaries (median, IQR), consider winsorization or log transforms for modeling, and separately inspect the highest-profit records to confirm they are valid.

### Extreme right-skew and high-value spikes in Total Sales
- **Description**: Total Sales contains many unusually large records compared with the typical transaction level, producing a strongly skewed distribution with substantial upper-end spikes.
- **Strength**: strong
- **Variables**: Total Sales
- **Relevance**: These values may reflect real large sales events or aggregation differences rather than obvious data errors, since the minimum is 0 and no negative sales are present. Use robust statistics, segment analyses by sales size, and validate whether very large sales records represent bulk orders or a different transaction grain.

### Right-skewed Units Sold with upper-end volume outliers
- **Description**: Units Sold has a long upper tail with a noticeable set of unusually high-volume records.
- **Strength**: strong
- **Variables**: Units Sold
- **Relevance**: High-unit records are likely real high-volume sales events, but they can dominate averages and regression fits. Downstream analysis should consider robust scaling, possible log transformation, and separate review of zero-unit and very high-unit records.

### Zero-valued records in sales and profit measures
- **Description**: The dataset contains records with zero Total Sales, zero Operating Profit, and zero Units Sold, which is unusual for completed sale records and may indicate cancellations, placeholders, or nonstandard transaction states.
- **Strength**: moderate
- **Variables**: Units Sold, Total Sales, Operating Profit
- **Relevance**: These could be valid business records such as returns netted to zero, canceled invoices, or non-sales placeholders, but they also may reflect data quality issues depending on business rules. Downstream analysis should quantify zero frequency, decide whether zero records belong in revenue/profit modeling, and possibly exclude them from analyses intended to represent completed sales.

### Retailer ID is highly concentrated at a single value
- **Description**: Retailer ID appears unusually concentrated, with the middle 50% of records all sharing the same identifier.
- **Strength**: strong
- **Variables**: Retailer ID
- **Relevance**: Because Retailer ID is an identifier rather than a continuous measure, this is not a numeric outlier issue but a distribution anomaly that may indicate one retailer dominates the dataset or that records are unevenly sampled. This is likely a real composition issue rather than a data error. Downstream analysis should account for retailer imbalance, avoid interpreting ID numerically, and consider stratifying or weighting by retailer.

