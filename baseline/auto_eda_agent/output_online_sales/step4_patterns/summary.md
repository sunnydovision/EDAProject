# Pattern Discovery Report

## Summary

- **Total Patterns**: 31
- **Pattern Categories**: 4

## Temporal Patterns

Found 6 patterns:

### Units sold rises through Q1, then declines from March to July
- **Description**: Monthly sales volume increased from January to March, then generally fell through July, with only a small uptick in June before reaching the lowest level in August.
- **Strength**: strong
- **Variables**: Units Sold
- **Relevance**: This indicates demand was strongest in late Q1 and weakened across late spring and summer, which matters for inventory and sales planning.

### Total revenue trends downward over time after January, with a small rebound in August
- **Description**: Revenue was highest at the start of the period and generally declined across the following months, bottoming in July before recovering slightly in August.
- **Strength**: strong
- **Variables**: Total Revenue
- **Relevance**: This suggests weakening revenue generation through most of the observed period, relevant for forecasting and diagnosing whether lower revenue is driven by pricing, volume, or both.

### Unit price is volatile, with peaks in January and April and a trough in July
- **Description**: Average selling price does not follow a steady trend; instead it fluctuates substantially month to month, with notable highs early in the year and in April, followed by lower levels in May through July.
- **Strength**: moderate
- **Variables**: Unit Price
- **Relevance**: Price fluctuations can materially affect revenue trends and may indicate changing product mix or pricing levels across months.

### Revenue decline from April to July coincides with both lower units sold and lower unit prices
- **Description**: From April through July, revenue fell each month while both average units sold and average unit price were also lower than in April.
- **Strength**: strong
- **Variables**: Total Revenue, Units Sold, Unit Price
- **Relevance**: This shows the mid-year revenue weakness aligns with simultaneous softness in both sales volume and pricing, which is important for identifying the drivers of decline.

### Transaction counts are mostly stable by month, except for August
- **Description**: The number of records per month stays close to the number of calendar days in each month, with limited variation from January through July, while August is lower.
- **Strength**: moderate
- **Variables**: Transaction ID
- **Relevance**: Because monthly record counts are mostly stable through July, changes in units sold and revenue are less likely to be explained by large swings in transaction volume alone; August should be interpreted carefully because it has fewer records.

## Correlation Patterns

Found 1 patterns:

### Unit Price and Total Revenue move together strongly
- **Description**: There is a strong positive relationship between Unit Price and Total Revenue: transactions with higher unit prices tend to have higher total revenue. This is consistent with revenue increasing as the selling price per item increases.
- **Strength**: strong
- **Variables**: Unit Price, Total Revenue
- **Relevance**: This relationship is likely largely structural rather than purely behavioral, because Total Revenue is likely calculated from Unit Price multiplied by Units Sold. The very high positive correlation suggests price level is a major driver of transaction revenue in this dataset, especially given the wide spread in Unit Price (std 429.45, max 3899.99) and Total Revenue (std 485.80, max 3899.99).

## Grouping Patterns

Found 18 patterns:

### Product category volumes are evenly distributed by transaction count
- **Description**: All product categories have exactly the same number of transactions, so there is no category dominance by order count.
- **Strength**: strong
- **Variables**: Product Category, Transaction ID
- **Relevance**: This means category differences are not driven by more transactions. Business comparisons across categories should focus on units sold and pricing rather than order frequency.

### Clothing is the dominant category by units sold
- **Description**: Clothing has the highest total and average units sold among categories, clearly ahead of the lower-volume categories.
- **Strength**: strong
- **Variables**: Product Category, Units Sold
- **Relevance**: This is meaningful for inventory and merchandising decisions because Clothing shows the strongest quantity movement despite the same transaction count as every other category.

### Beauty Products and Home Appliances are the lowest-volume categories by units
- **Description**: These two categories sit at the bottom of unit sales, with Beauty Products lowest overall.
- **Strength**: strong
- **Variables**: Product Category, Units Sold
- **Relevance**: This is relevant for assortment and replenishment planning because these categories generate fewer units per transaction than the others.

### Electronics dominates category pricing
- **Description**: Electronics has by far the highest unit prices among product categories, creating a clear high-price segment.
- **Strength**: strong
- **Variables**: Product Category, Unit Price
- **Relevance**: This is highly relevant for pricing, margin, and risk management because Electronics is concentrated in much higher ticket items than the rest of the catalog.

### Books form the lowest-price category segment
- **Description**: Books are priced far below every other category, making them a distinct low-price group.
- **Strength**: strong
- **Variables**: Product Category, Unit Price
- **Relevance**: This matters for basket-building and promotional strategy because Books occupy a very different price band from all other categories.

## Anomaly Patterns

Found 6 patterns:

### Extreme right-tail outliers in Unit Price
- **Description**: Unit Price shows a concentrated set of unusually high values relative to the bulk of the distribution, indicating a heavy upper tail.
- **Strength**: strong
- **Variables**: Unit Price
- **Relevance**: This is more consistent with real business variation, such as a mix of low- and high-priced products, than a data quality issue, because prices are all positive and the lower bound is negative while the observed minimum is 6.5. In downstream analysis, use robust summaries (median, IQR), consider log-transforming price, and segment analyses by product category or price band so high-priced items do not dominate averages.

### Extreme right-tail outliers in Total Revenue
- **Description**: Total Revenue contains a notable group of unusually large transactions compared with the typical transaction size.
- **Strength**: strong
- **Variables**: Total Revenue
- **Relevance**: This likely reflects real high-value sales events rather than obvious data errors, since revenue is strictly positive and the distribution is consistent with occasional large transactions. For downstream analysis, report both median and mean revenue, investigate top transactions separately, and consider winsorization or log-scaling when building models sensitive to extreme values.

### Single high-quantity spike in Units Sold
- **Description**: Units Sold is mostly concentrated at low counts, with one unusually large quantity transaction standing apart from the rest.
- **Strength**: moderate
- **Variables**: Units Sold
- **Relevance**: This appears more like a real bulk-purchase event than a data quality issue, because the values are positive integers and only one record exceeds the outlier threshold. In downstream analysis, keep the record but use robust statistics for central tendency and consider separate treatment of bulk orders if modeling customer purchase behavior.

### Strong mean-median gaps indicate non-normal transaction distributions
- **Description**: Several numeric business measures have means far above medians, showing that typical transactions are much smaller than average values suggest.
- **Strength**: strong
- **Variables**: Unit Price, Total Revenue, Units Sold
- **Relevance**: This is likely a real distributional feature rather than bad data, especially for price and revenue where a minority of expensive transactions inflate averages. Downstream reporting should avoid relying on means alone; medians, percentiles, and segmented summaries will better represent typical behavior.

### No evidence of zero-inflation or zero-value anomalies in numeric sales fields
- **Description**: The numeric sales measures do not show zero-heavy behavior and contain no zero values.
- **Strength**: strong
- **Variables**: Units Sold, Unit Price, Total Revenue
- **Relevance**: This suggests there is no zero-inflation problem in the provided numeric transaction fields. Downstream analysis does not need zero-inflation-specific handling for these variables, but analysts should still verify whether returns, cancellations, or free items are excluded from the dataset.

