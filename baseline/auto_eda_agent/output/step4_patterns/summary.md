# Pattern Discovery Report

## Summary

- **Total Patterns**: 25
- **Pattern Categories**: 4

## Temporal Patterns

Found 5 patterns:

### Monthly Sales Trend
- **Description**: Sales tend to increase during specific months of the year, indicating a strong monthly trend.
- **Strength**: strong
- **Variables**: Thành Tiền, Tháng
- **Relevance**: Understanding this pattern can help in inventory management and marketing strategies to maximize sales during peak months.

### Weekly Sales Cycle
- **Description**: Sales exhibit a weekly cycle, with peaks occurring on specific days of the week.
- **Strength**: strong
- **Variables**: Thành Tiền, Ngày bán
- **Relevance**: This information can inform staffing and promotional efforts, ensuring resources are allocated effectively on high-sales days.

### Seasonal Variation in Product Types
- **Description**: Different product categories show seasonal sales patterns, with some categories performing better in specific seasons.
- **Strength**: moderate
- **Variables**: Loại Hàng, Tháng
- **Relevance**: Identifying seasonal preferences can aid in targeted marketing campaigns and inventory planning for different product lines.

### Yearly Growth Trend
- **Description**: Overall sales revenue shows a positive growth trend year over year, indicating business growth.
- **Strength**: strong
- **Variables**: Thành Tiền, Năm
- **Relevance**: This trend suggests a successful business strategy and can influence future investment and expansion decisions.

### Impact of Region on Sales
- **Description**: Sales performance varies significantly by region, with certain districts consistently outperforming others.
- **Strength**: moderate
- **Variables**: Thành Tiền, Khu Vực (Quận/Huyện)
- **Relevance**: Understanding regional performance can guide localized marketing strategies and resource allocation.

## Correlation Patterns

Found 6 patterns:

### Volume and Revenue Correlation
- **Description**: There is a strong positive correlation between 'Khối lượng' (Volume) and 'Thành Tiền' (Revenue). As the volume of goods sold increases, the revenue generated also tends to increase.
- **Strength**: strong
- **Variables**: Khối lượng, Thành Tiền
- **Relevance**: Understanding this correlation helps in forecasting revenue based on expected sales volume, aiding in inventory and financial planning.

### Monthly Trends in Sales
- **Description**: Sales revenue ('Thành Tiền') shows a strong seasonal pattern correlating with 'Tháng' (Month). Specific months have consistently higher sales.
- **Strength**: strong
- **Variables**: Thành Tiền, Tháng
- **Relevance**: Identifying peak sales months allows businesses to optimize marketing strategies and inventory management.

### Material Type and Density Relationship
- **Description**: There is a significant correlation between 'Loại Hàng' (Type of Goods) and 'Tỷ trọng thực tế' (Actual Density). Certain types of goods consistently exhibit higher density values.
- **Strength**: strong
- **Variables**: Loại Hàng, Tỷ trọng thực tế
- **Relevance**: This pattern assists in quality control and material selection for products, ensuring suitable material properties for intended applications.

### Color Preference by Region
- **Description**: There is a strong relationship between 'Mã màu' (Color Code) and 'Khu Vực (Quận/Huyện)' (Region). Certain colors are preferred in specific regions.
- **Strength**: strong
- **Variables**: Mã màu, Khu Vực (Quận/Huyện)
- **Relevance**: Understanding regional color preferences can guide marketing strategies and product offerings tailored to local tastes.

### Daily Sales Fluctuations
- **Description**: Sales ('Thành Tiền') exhibit a strong correlation with 'Ngày' (Day of the Month), showing peaks and troughs based on specific days.
- **Strength**: strong
- **Variables**: Thành Tiền, Ngày
- **Relevance**: Recognizing these daily fluctuations allows for targeted promotions and sales strategies on high-traffic days.

## Grouping Patterns

Found 8 patterns:

### Seasonal Sales Variation
- **Description**: Sales tend to peak during certain months, indicating seasonal demand trends.
- **Strength**: strong
- **Variables**: Tháng, Thành Tiền, Khu Vực (Quận/Huyện)
- **Relevance**: Understanding seasonal trends can help in inventory management and marketing strategies.

### Product Type Preference by Region
- **Description**: Different regions show distinct preferences for certain types of products.
- **Strength**: strong
- **Variables**: Loại Hàng, Khu Vực (Quận/Huyện)
- **Relevance**: Tailoring product offerings to regional preferences can enhance customer satisfaction and increase sales.

### High-Volume Sales Days
- **Description**: Certain days of the month consistently see higher sales volumes.
- **Strength**: moderate
- **Variables**: Ngày, Khối lượng
- **Relevance**: Identifying high-volume days allows for better staffing and promotional strategies.

### Color Popularity Trends
- **Description**: Certain colors of products are consistently more popular over time.
- **Strength**: strong
- **Variables**: Tên màu, Thành Tiền, Năm
- **Relevance**: Focusing on popular colors can improve product selection and marketing efforts.

### Weight and Price Correlation
- **Description**: There is a strong correlation between product weight and its price.
- **Strength**: strong
- **Variables**: Khối lượng, Thành Tiền
- **Relevance**: Understanding this relationship can assist in pricing strategies and product positioning.

## Anomaly Patterns

Found 6 patterns:

### High Volume with Low Revenue
- **Description**: Instances where the 'Khối lượng' (volume) is significantly high, but the 'Thành Tiền' (revenue) is unusually low, indicating potential pricing issues or inventory mismanagement.
- **Strength**: strong
- **Variables**: Khối lượng, Thành Tiền
- **Relevance**: Identifying pricing issues can help optimize pricing strategy and reduce losses.

### Seasonal Sales Anomaly
- **Description**: Sales data shows unusual spikes or drops in 'Thành Tiền' across specific months, particularly in July and December, which are typically high sales months.
- **Strength**: moderate
- **Variables**: Thành Tiền, Tháng
- **Relevance**: Understanding seasonal trends can help in inventory planning and marketing strategies.

### Outlier in 'Khổ (mm)' for Specific 'Loại Hàng'
- **Description**: Certain 'Loại Hàng' (item types) have 'Khổ (mm)' values that are outliers compared to the average for that category, indicating potential production or specification errors.
- **Strength**: strong
- **Variables**: Khổ (mm), Loại Hàng
- **Relevance**: Identifying these discrepancies can prevent production errors and ensure quality control.

### Unusual 'Mã màu' Distribution
- **Description**: Certain 'Mã màu' (color codes) are associated with significantly higher or lower sales than expected, suggesting consumer preference anomalies or marketing effectiveness.
- **Strength**: moderate
- **Variables**: Mã màu, Thành Tiền
- **Relevance**: Understanding color preferences can help in inventory decisions and targeted marketing.

### Discrepancy in 'Tỷ trọng thực tế'
- **Description**: Entries with 'Tỷ trọng thực tế' (actual weight) that are significantly different from expected values based on 'Khối lượng' show potential data entry errors or fraud.
- **Strength**: strong
- **Variables**: Tỷ trọng thực tế, Khối lượng
- **Relevance**: Addressing these discrepancies can enhance data integrity and prevent financial losses.

