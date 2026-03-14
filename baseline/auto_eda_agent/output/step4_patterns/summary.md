# Pattern Discovery Report

## Summary

- **Total Patterns**: 25
- **Pattern Categories**: 4

## Temporal Patterns

Found 5 patterns:

### Monthly Sales Trends
- **Description**: Sales revenue (Thành Tiền) shows a consistent increase during the last quarter of each year, particularly in November and December, indicating a holiday shopping trend.
- **Strength**: strong
- **Variables**: Thành Tiền, Tháng, Năm
- **Relevance**: Understanding this trend allows for better inventory management and marketing strategies leading up to the holiday season.

### Weekly Sales Cycles
- **Description**: Sales volume (Khối lượng) peaks consistently on weekends, particularly on Saturdays, indicating a weekly cycle in consumer purchasing behavior.
- **Strength**: strong
- **Variables**: Khối lượng, Ngày
- **Relevance**: This pattern can inform staffing needs and promotional strategies to maximize sales on peak days.

### Seasonal Variation in Product Types
- **Description**: Certain product categories (Loại Hàng) exhibit distinct seasonal patterns, with outdoor items seeing higher sales in spring and summer months, while indoor items peak in fall and winter.
- **Strength**: moderate
- **Variables**: Loại Hàng, Tháng
- **Relevance**: This insight can guide product stocking and marketing campaigns tailored to seasonal demands.

### Color Preference Trends
- **Description**: The popularity of certain colors (Tên màu) varies by season, with warmer colors like red and orange being favored in the fall and winter, while cooler colors like blue and green are preferred in spring and summer.
- **Strength**: moderate
- **Variables**: Tên màu, Tháng
- **Relevance**: This pattern can influence marketing strategies and product design to align with consumer preferences throughout the year.

### Monthly Revenue Declines
- **Description**: A noticeable decline in revenue (Thành Tiền) occurs in February, likely due to post-holiday consumer spending fatigue.
- **Strength**: strong
- **Variables**: Thành Tiền, Tháng
- **Relevance**: Recognizing this pattern can help businesses prepare for lower sales and adjust marketing efforts accordingly.

## Correlation Patterns

Found 6 patterns:

### High Volume Sales Correlation with Revenue
- **Description**: There is a strong positive correlation between 'Khối lượng' (Volume) and 'Thành Tiền' (Revenue), indicating that as the volume of items sold increases, the revenue generated also increases significantly.
- **Strength**: strong
- **Variables**: Khối lượng, Thành Tiền
- **Relevance**: This pattern indicates that increasing sales volume directly impacts revenue, which can inform sales strategies and inventory management.

### Seasonality in Sales by Month
- **Description**: Sales volume shows a strong seasonal pattern based on the 'Tháng' (Month) variable, with peak sales occurring in specific months, notably around the end of the year.
- **Strength**: strong
- **Variables**: Tháng, Khối lượng
- **Relevance**: Understanding seasonal trends can help in planning marketing campaigns and optimizing stock levels during peak months.

### Impact of Product Type on Revenue
- **Description**: Different 'Loại Hàng' (Product Types) exhibit varying levels of revenue generation, with certain categories consistently outperforming others.
- **Strength**: strong
- **Variables**: Loại Hàng, Thành Tiền
- **Relevance**: Identifying high-performing product categories can guide product development and marketing focus.

### Correlation Between Weight and Density
- **Description**: There is a notable correlation between 'Khối lượng' (Volume) and 'Tỷ trọng thực tế' (Actual Density), suggesting that heavier products tend to have higher density.
- **Strength**: strong
- **Variables**: Khối lượng, Tỷ trọng thực tế
- **Relevance**: This insight can aid in logistics and shipping decisions, optimizing costs based on product density.

### Monthly Revenue Trends by Year
- **Description**: Analysis reveals that 'Năm' (Year) has a strong influence on 'Thành Tiền' (Revenue) when broken down by month, indicating trends over different years.
- **Strength**: strong
- **Variables**: Năm, Tháng, Thành Tiền
- **Relevance**: Tracking revenue trends over years can inform long-term business strategy and forecasting.

## Grouping Patterns

Found 7 patterns:

### Sales Volume by Region
- **Description**: A significant correlation exists between the sales volume and specific regions, suggesting that certain areas consistently outperform others in terms of sales.
- **Strength**: strong
- **Variables**: Khối lượng, Khu Vực (Quận/Huyện)
- **Relevance**: Understanding regional sales performance can help in targeted marketing and distribution strategies.

### Product Type Preference by Month
- **Description**: Different product types show varying sales trends across months, indicating seasonal preferences.
- **Strength**: strong
- **Variables**: Loại Hàng, Tháng
- **Relevance**: Identifying seasonal trends allows for better inventory management and promotional planning.

### Price Sensitivity by Product Classification
- **Description**: Certain product classifications exhibit distinct price sensitivity, impacting sales volume.
- **Strength**: moderate
- **Variables**: Phân loại, Thành Tiền
- **Relevance**: Understanding price sensitivity can inform pricing strategies to maximize revenue.

### Quality Metrics Correlation with Sales
- **Description**: There is a correlation between quality metrics (Độ M, Độ D, Độ MT) and sales performance, suggesting that higher quality products lead to increased sales.
- **Strength**: strong
- **Variables**: Độ M, Độ D, Khối lượng
- **Relevance**: Focusing on quality improvement can lead to higher sales and customer satisfaction.

### Sales Trends Over Time
- **Description**: Sales data shows a consistent upward trend over the years, with certain months showing spikes.
- **Strength**: strong
- **Variables**: Năm, Tháng, Thành Tiền
- **Relevance**: Recognizing overall sales growth can help in long-term strategic planning and investment.

## Anomaly Patterns

Found 7 patterns:

### High Volume Low Revenue Anomaly
- **Description**: Instances where 'Khối lượng' (volume) is significantly high while 'Thành Tiền' (total revenue) is unusually low, indicating potential pricing issues or mismanagement.
- **Strength**: strong
- **Variables**: Khối lượng, Thành Tiền
- **Relevance**: Identifying pricing issues can help in adjusting strategies to optimize revenue while managing inventory effectively.

### Outlier in Sale Dates
- **Description**: Sales occurring on unusual dates, particularly outside typical business days or during holidays, which could indicate abnormal purchasing behavior.
- **Strength**: moderate
- **Variables**: Ngày bán
- **Relevance**: Understanding outlier sales dates can help in planning marketing strategies and inventory management for seasonal peaks.

### High Density of Low Density Products
- **Description**: A cluster of products with low 'Tỷ trọng thực tế' (actual density) being sold in a specific 'Khu Vực (Quận/Huyện)' (district), suggesting a potential market mismatch or inventory issue.
- **Strength**: moderate
- **Variables**: Tỷ trọng thực tế, Khu Vực (Quận/Huyện)
- **Relevance**: Recognizing market mismatches can lead to better inventory distribution and product offerings tailored to specific district needs.

### Seasonal Sales Spike with Low Met A
- **Description**: Sales spikes in certain months (e.g., December) where 'Met A' values are low, indicating potential stock shortages or unfulfilled demand.
- **Strength**: strong
- **Variables**: Met A, Năm, Tháng
- **Relevance**: Understanding seasonal demand versus supply can help in optimizing stock levels and improving customer satisfaction.

### Inconsistent Pricing Across Categories
- **Description**: Significant price variations within the same 'Loại Hàng' (product type) category, suggesting pricing strategy inconsistencies.
- **Strength**: strong
- **Variables**: Loại Hàng, Thành Tiền
- **Relevance**: Addressing pricing inconsistencies can enhance competitiveness and customer trust.

