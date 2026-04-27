# Pattern Discovery Report

## Summary

- **Total Patterns**: 36
- **Pattern Categories**: 4

## Temporal Patterns

Found 9 patterns:

### Step-change upward in activity from 2020 to 2021
- **Description**: Monthly totals jump sharply at the start of 2021 across transaction volume and business outcomes, indicating a clear level shift rather than a gradual rise.
- **Strength**: strong
- **Variables**: count, Total Sales, Units Sold, Operating Profit
- **Relevance**: This indicates that 2021 operates at a much larger monthly scale than 2020, so year-over-year comparisons should account for this structural shift.

### 2020 mid-year trough followed by partial recovery
- **Description**: In 2020, business volume and outcomes decline into June, then recover in July through September, though not uniformly to earlier highs.
- **Strength**: strong
- **Variables**: Total Sales, Units Sold, Operating Profit, count
- **Relevance**: This shows a clear 2020 disruption period centered on June, followed by recovery, useful for identifying abnormal operating periods.

### Late-2021 sales and profit acceleration after October dip
- **Description**: After declining into October 2021, Total Sales and Operating Profit recover in November and rise strongly in December.
- **Strength**: strong
- **Variables**: Total Sales, Operating Profit, Units Sold, Price per Unit
- **Relevance**: This indicates a pronounced year-end rebound in 2021, relevant for forecasting and planning around Q4 performance.

### Price per Unit mean declines through early 2021, then climbs through year-end
- **Description**: Average selling price falls from mid-2020 highs into early 2021, then trends upward from spring to December 2021.
- **Strength**: moderate
- **Variables**: Price per Unit
- **Relevance**: This suggests pricing conditions were weaker in early 2021 and firmer later in the year, which matters for revenue mix and margin management.

### Units Sold mean is higher in late 2020 than in most of 2021
- **Description**: Average units per record peak in late summer 2020 and are generally lower across 2021.
- **Strength**: strong
- **Variables**: Units Sold
- **Relevance**: This indicates that larger 2021 totals are driven more by more records than by larger average order quantities.

## Correlation Patterns

Found 3 patterns:

### Total Sales and Operating Profit move together very strongly
- **Description**: Total Sales and Operating Profit have a very strong positive relationship. Records with higher gross sales tend to also show higher operating profit. This is likely largely structural because operating profit is financially downstream from sales, though the exact profit level also depends on costs and margin.
- **Strength**: strong
- **Variables**: Total Sales, Operating Profit
- **Relevance**: This indicates profit is tightly linked to revenue generation in this dataset. Sales growth is closely associated with profit growth, so revenue-driving actions are likely to have a direct effect on operating profit.

### Units Sold is strongly associated with Total Sales
- **Description**: Units Sold and Total Sales show a strong positive relationship. Records with more units sold generally produce higher total sales. This relationship is partly structural because sales revenue depends on quantity sold and price per unit.
- **Strength**: strong
- **Variables**: Units Sold, Total Sales
- **Relevance**: Volume sold is a major driver of revenue in the dataset. Increasing unit volume appears strongly connected with higher sales outcomes.

### Units Sold is strongly associated with Operating Profit
- **Description**: Units Sold and Operating Profit have a strong positive relationship. Records with higher sales volume tend to generate higher operating profit. This is likely an indirect structural relationship because more units sold raises sales, which in turn is strongly tied to profit.
- **Strength**: strong
- **Variables**: Units Sold, Operating Profit
- **Relevance**: Sales volume is strongly linked not just to revenue but also to profitability. Efforts that increase unit movement may also improve operating profit, assuming margins are maintained.

## Grouping Patterns

Found 17 patterns:

### Retailer concentration in record volume
- **Description**: A small set of retailers accounts for much larger record counts than the rest, indicating an uneven distribution by retailer segment.
- **Strength**: strong
- **Variables**: Retailer, count
- **Relevance**: High. Any retailer-level performance summary will be heavily influenced by Foot Locker, West Gear, and Sports Direct because they represent the largest portions of the dataset.

### Retailer leaders in total units sold
- **Description**: Total units sold are concentrated among three retailers, with West Gear leading overall.
- **Strength**: strong
- **Variables**: Retailer, Units Sold
- **Relevance**: High. Volume is dominated by West Gear, Foot Locker, and Sports Direct, so inventory, partnerships, and forecasting decisions should prioritize these retailers.

### Walmart has the highest average units per record despite low total volume
- **Description**: Walmart has the highest average units sold per record, even though it has the lowest record count and one of the lowest total unit sums.
- **Strength**: moderate
- **Variables**: Retailer, Units Sold, count
- **Relevance**: High. Walmart appears to generate larger order sizes per record, which may matter for channel strategy, fulfillment planning, or account management.

### Amazon has the highest average price per unit among retailers
- **Description**: Average selling price differs across retailers, with Amazon at the top and Sports Direct at the bottom.
- **Strength**: moderate
- **Variables**: Retailer, Price per Unit
- **Relevance**: Moderate. Retailers are not only different in volume but also in pricing level, which can affect margin management and retailer positioning.

### West and Northeast dominate regional record counts
- **Description**: Regional distribution is uneven, with West and Northeast carrying the largest number of records.
- **Strength**: strong
- **Variables**: Region, count
- **Relevance**: High. Regional analyses will be weighted toward West and Northeast due to their larger representation in the data.

## Anomaly Patterns

Found 7 patterns:

### High-end price outliers above expected range
- **Description**: A small set of records have unusually high unit prices relative to the central price distribution.
- **Strength**: moderate
- **Variables**: Price per Unit
- **Relevance**: Likely a mix of legitimate premium pricing and possible pricing-entry exceptions. Keep these records, but validate values above 85 before modeling price sensitivity; consider winsorizing or using robust methods if price-driven models are sensitive to tail values.

### Upper-tail volume spikes in units sold
- **Description**: Units Sold shows a pronounced right tail with a nontrivial number of unusually large transactions.
- **Strength**: strong
- **Variables**: Units Sold
- **Relevance**: More likely real business events such as bulk orders or promotion-driven spikes than random noise, because the tail is substantial and aligned with positive skew. Retain for revenue analysis, but use robust summaries, segment large orders separately, and test model sensitivity with and without high-volume records.

### Extremely right-skewed total sales distribution
- **Description**: Total Sales contains very large revenue spikes relative to the typical transaction size, producing a highly uneven distribution.
- **Strength**: strong
- **Variables**: Total Sales
- **Relevance**: This pattern is consistent with a mix of many small transactions and a smaller number of very large deals. Likely mostly real business variation, but values near the maximum should be validated because they strongly influence averages. Use log transforms, medians, or trimmed means in downstream analysis.

### Highly concentrated profit in a small set of records
- **Description**: Operating Profit is even more extreme than Total Sales, with very large positive profit spikes and a heavy upper tail.
- **Strength**: strong
- **Variables**: Operating Profit
- **Relevance**: Likely reflects a small number of very profitable transactions rather than symmetric noise. These records are important for profitability analysis but can distort averages and model coefficients. Keep them, validate the largest profits, and prefer robust or transformed modeling approaches.

### Possible zero-inflation in sales and profit measures
- **Description**: Both Total Sales and Operating Profit have minimum values of zero, suggesting a cluster at zero may exist, which would be unusual for completed sale records if frequent.
- **Strength**: weak
- **Variables**: Total Sales, Operating Profit, Units Sold
- **Relevance**: Zeros could be legitimate canceled, returned, or placeholder records, or they could indicate data quality issues if these are supposed to be completed sales. Downstream, quantify zero counts before modeling; if material, treat zero records as a separate process or filter them depending on business rules.

