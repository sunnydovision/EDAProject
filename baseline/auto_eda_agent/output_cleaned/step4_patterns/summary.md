# Pattern Discovery Report

## Summary

- **Total Patterns**: 22
- **Pattern Categories**: 4

## Temporal Patterns

Found 5 patterns:

### Seasonal Sales Peaks
- **Description**: Sales exhibit a clear seasonal pattern, with peaks occurring during specific months of the year, indicating high demand periods.
- **Strength**: strong
- **Variables**: Thành Tiền, Ngày bán, Năm
- **Relevance**: Understanding seasonal peaks can help in inventory management and marketing strategies, ensuring stock availability during high-demand periods.

### Weekly Sales Cycles
- **Description**: Sales data shows a weekly cycle with consistent fluctuations, typically peaking on weekends and dipping during weekdays.
- **Strength**: strong
- **Variables**: Thành Tiền, Ngày bán, Thứ
- **Relevance**: Identifying weekly patterns allows businesses to optimize staffing and promotions, maximizing sales during peak days.

### Monthly Growth Trends
- **Description**: There is a noticeable trend of increasing sales month-over-month, particularly in specific product categories.
- **Strength**: moderate
- **Variables**: Thành Tiền, Khối lượng, Năm
- **Relevance**: Understanding growth trends helps in forecasting and strategic planning for future investments and marketing efforts.

### Geographical Sales Variations
- **Description**: Sales patterns vary significantly across different regions, with certain provinces showing consistently higher sales than others.
- **Strength**: moderate
- **Variables**: Thành Tiền, Tỉnh / Thành Phố, Ngày bán
- **Relevance**: This pattern can inform targeted marketing campaigns and distribution strategies tailored to regional demand.

### Impact of Product Type on Sales
- **Description**: Different product categories exhibit distinct sales trends based on seasonality, with some categories performing better in specific months.
- **Strength**: strong
- **Variables**: Loại Hàng, Thành Tiền, Ngày bán
- **Relevance**: Recognizing the impact of product type on sales allows for better inventory allocation and promotional strategies aligned with seasonal demands.

## Correlation Patterns

Found 6 patterns:

### Weight vs. Actual Density
- **Description**: As the 'Khối lượng' (Weight) increases, the 'Tỷ trọng thực tế' (Actual Density) shows a corresponding increase, indicating a strong positive correlation.
- **Strength**: strong
- **Variables**: Khối lượng, Tỷ trọng thực tế
- **Relevance**: Understanding this relationship can help in optimizing material selection and inventory management.

### Sales Amount vs. Dimension
- **Description**: The 'Thành Tiền' (Sales Amount) is significantly influenced by 'Khổ (mm)' (Dimension), where larger dimensions correlate with higher sales amounts.
- **Strength**: strong
- **Variables**: Thành Tiền, Khổ (mm)
- **Relevance**: This pattern can guide marketing strategies and product line expansions based on size categories.

### Year vs. Sales Amount
- **Description**: There is a notable increase in 'Thành Tiền' (Sales Amount) over the years, suggesting a trend of growth in sales.
- **Strength**: strong
- **Variables**: Năm, Thành Tiền
- **Relevance**: This trend can inform long-term business strategies and financial forecasting.

### Material Type vs. Actual Density
- **Description**: Different 'Loại Hàng' (Material Type) exhibit distinct average 'Tỷ trọng thực tế' (Actual Density), indicating a strong categorical influence.
- **Strength**: strong
- **Variables**: Loại Hàng, Tỷ trọng thực tế
- **Relevance**: This understanding can aid in product development and quality assurance processes.

### Color Code vs. Sales Amount
- **Description**: Certain 'Mã màu' (Color Codes) are associated with higher 'Thành Tiền' (Sales Amount), indicating consumer preferences for specific colors.
- **Strength**: strong
- **Variables**: Mã màu, Thành Tiền
- **Relevance**: Leveraging popular color trends can enhance marketing effectiveness and inventory decisions.

## Grouping Patterns

Found 6 patterns:

### High Volume Sales by Region
- **Description**: A significant cluster of high sales volume is observed in specific regions, particularly in urban areas.
- **Strength**: strong
- **Variables**: Khối lượng, Khu Vực (Quận/Huyện), Tỉnh / Thành Phố
- **Relevance**: Understanding regional sales patterns can help in targeted marketing and inventory management.

### Color Preference by Product Type
- **Description**: Certain colors are preferred for specific product types, indicating a trend in consumer preferences.
- **Strength**: moderate
- **Variables**: Tên màu, Loại Hàng
- **Relevance**: This pattern can guide product design and marketing strategies to align with consumer preferences.

### Sales Peaks on Specific Days
- **Description**: Sales data indicates recurring peaks on specific weekdays, particularly on weekends.
- **Strength**: strong
- **Variables**: Thứ, Thành Tiền
- **Relevance**: Identifying peak sales days can optimize staffing and promotional efforts.

### Product Type and Density Relationship
- **Description**: A correlation exists between product density (size) and sales performance across different categories.
- **Strength**: moderate
- **Variables**: Độ D, Loại Hàng, Thành Tiền
- **Relevance**: This insight can inform product development and selection strategies.

### Seasonal Sales Variation
- **Description**: Sales fluctuate significantly across different months, indicating seasonal buying behavior.
- **Strength**: strong
- **Variables**: Năm, Thành Tiền, Ngày bán
- **Relevance**: Recognizing seasonal trends can enhance inventory planning and promotional strategies.

## Anomaly Patterns

Found 5 patterns:

### High Volume, Low Price Outlier
- **Description**: Instances where the 'Khối lượng' (volume) is significantly high, while the 'Thành Tiền' (total price) is low compared to the median price for that category.
- **Strength**: strong
- **Variables**: Khối lượng, Thành Tiền, Phân loại
- **Relevance**: This pattern may indicate potential pricing errors, bulk sales at a loss, or inventory issues that could affect profitability.

### Seasonal Sales Drop
- **Description**: Notable decrease in sales ('Thành Tiền') during specific months, particularly in the summer months (June-August) for certain product categories.
- **Strength**: moderate
- **Variables**: Thành Tiền, Ngày bán, Loại Hàng
- **Relevance**: Understanding seasonal trends can help in inventory management and marketing strategies to boost sales during these periods.

### High Density of Sales in Specific Regions
- **Description**: Certain 'Khu Vực (Quận/Huyện)' exhibit disproportionately high sales volumes compared to others, indicating regional preferences or market saturation.
- **Strength**: strong
- **Variables**: Khối lượng, Khu Vực (Quận/Huyện), Tỉnh / Thành Phố
- **Relevance**: Identifying these regions can help in targeted marketing and resource allocation to maximize sales.

### Anomalous Weight to Price Ratio
- **Description**: Entries where the 'Tỷ trọng thực tế' (actual density) is significantly higher than expected based on the category, leading to unusually high 'Thành Tiền' for low 'Khối lượng'.
- **Strength**: weak
- **Variables**: Tỷ trọng thực tế, Khối lượng, Thành Tiền, Phân loại
- **Relevance**: This anomaly could indicate misclassification of products or pricing strategies that need review.

### Unusual Trend in 'Met' Measurements
- **Description**: Fluctuations in 'Met A', 'Met B', and 'Met C' that do not align with expected trends based on historical data.
- **Strength**: moderate
- **Variables**: Met A, Met B, Met C, Năm
- **Relevance**: Monitoring these metrics is crucial for quality control and ensuring product consistency.

