# Pattern Discovery Report

## Summary

- **Total Patterns**: 49
- **Pattern Categories**: 4

## Temporal Patterns

Found 12 patterns:

### STT mean increases every month
- **Description**: The monthly average of STT rises continuously across the full observed period, indicating a clear upward time trend with no monthly reversals.
- **Strength**: strong
- **Variables**: STT
- **Relevance**: This shows a consistent time progression in record numbering/order over the months and confirms the dataset spans a steadily advancing transaction sequence.

### STT sum trends upward overall with a November dip
- **Description**: Monthly STT totals rise strongly from August to October, fall in November, then rebound to new highs in December and January.
- **Strength**: moderate
- **Variables**: STT
- **Relevance**: This indicates the monthly total record index is generally higher later in the timeline, but month-to-month totals are affected by fluctuations in transaction volume.

### Transaction count is volatile, peaking in October and January
- **Description**: Monthly record counts do not follow a steady trend; instead they fluctuate with a sharp rise in October, a trough in November, and another high level in January.
- **Strength**: strong
- **Variables**: STT count, Độ D count, Khối lượng count, Met A count, Met B count
- **Relevance**: This reflects changing transaction activity over time, with especially active months in October and January and a clear slowdown in November.

### Khối lượng total declines early, surges in October, drops in November, then recovers
- **Description**: Total monthly volume shows a cyclical-looking fluctuation over the six months rather than a steady increase or decrease.
- **Strength**: moderate
- **Variables**: Khối lượng
- **Relevance**: This suggests monthly sold volume varies substantially over time, which matters for production planning, logistics, and inventory allocation.

### Average Khối lượng per record is relatively stable over time
- **Description**: Despite large swings in total volume and transaction count, the monthly average volume per record stays within a narrow range.
- **Strength**: strong
- **Variables**: Khối lượng
- **Relevance**: This indicates that changes in total monthly volume are driven more by the number of transactions than by major shifts in average shipment size.

## Correlation Patterns

Found 13 patterns:

### Khối lượng đi cùng doanh thu dòng bán
- **Description**: Khối lượng tăng thì Thành Tiền cũng tăng rất mạnh. Đây là quan hệ đồng biến rõ rệt giữa lượng hàng bán ra và giá trị tiền của dòng giao dịch.
- **Strength**: strong
- **Variables**: Khối lượng, Thành Tiền
- **Relevance**: Quan hệ này có ý nghĩa kinh doanh trực tiếp: doanh thu dòng bán phụ thuộc mạnh vào lượng hàng bán. Khả năng cao đây là quan hệ cấu trúc vì Thành Tiền thường được tính từ khối lượng nhân đơn giá hoặc các quy đổi liên quan.

### Khối lượng đi cùng doanh thu quy đổi
- **Description**: Khối lượng có quan hệ đồng biến rất mạnh với cả Doanh_thu_trên_mm và Tỷ_trọng_doanh_thu_%. Khi giao dịch có khối lượng lớn hơn, các chỉ tiêu doanh thu quy đổi và tỷ trọng doanh thu cũng tăng tương ứng.
- **Strength**: strong
- **Variables**: Khối lượng, Doanh_thu_trên_mm, Tỷ_trọng_doanh_thu_%
- **Relevance**: Điều này cho thấy sản lượng bán ra gắn chặt với đóng góp doanh thu. Tuy nhiên quan hệ có thể mang tính cấu trúc nếu các chỉ tiêu doanh thu quy đổi hoặc tỷ trọng doanh thu được tính trực tiếp từ doanh thu dòng bán.

### Met A đồng biến với khối lượng và doanh thu
- **Description**: Chiều dài Met A tăng đi kèm với Khối lượng và các chỉ tiêu doanh thu tăng. Điều này phản ánh các đơn hàng có chiều dài chính lớn hơn thường cũng có quy mô bán lớn hơn.
- **Strength**: strong
- **Variables**: Met A, Khối lượng, Thành Tiền, Doanh_thu_trên_mm, Tỷ_trọng_doanh_thu_%
- **Relevance**: Về kinh doanh, Met A có vẻ là chỉ báo quy mô đơn hàng. Một phần quan hệ có thể là cấu trúc nếu chiều dài là đầu vào trực tiếp để tính khối lượng hoặc giá trị bán.

### Các chỉ tiêu doanh thu gần như trùng nhau
- **Description**: Thành Tiền, Doanh_thu_trên_mm và Tỷ_trọng_doanh_thu_% gần như di chuyển giống hệt nhau. Đây là mức đồng biến gần hoàn hảo.
- **Strength**: strong
- **Variables**: Thành Tiền, Doanh_thu_trên_mm, Tỷ_trọng_doanh_thu_%
- **Relevance**: Đây gần như chắc chắn là quan hệ cấu trúc, tức các biến này được tính từ cùng một nguồn hoặc là biến đổi tuyến tính của nhau. Trong phân tích, nên tránh dùng đồng thời vì trùng lặp thông tin rất cao.

### Độ dày đi cùng tỷ trọng thực tế
- **Description**: Độ D tăng thì Tỷ trọng thực tế tăng rất mạnh. Vật liệu dày hơn thường đi cùng mức khối lượng trên đơn vị quy đổi cao hơn.
- **Strength**: strong
- **Variables**: Độ D, Tỷ trọng thực tế
- **Relevance**: Về mặt kinh doanh và kỹ thuật, đây là quan hệ rất quan trọng vì độ dày ảnh hưởng mạnh đến đặc tính vật lý của sản phẩm. Khả năng cao đây là quan hệ cấu trúc hoặc vật lý, không phải hành vi thị trường.

## Grouping Patterns

Found 10 patterns:

### Phân loại 1 dominates the dataset
- **Description**: Within Phân loại, group 1 overwhelmingly dominates both record count and total khối lượng, far exceeding all other segments.
- **Strength**: strong
- **Variables**: Phân loại, count, Khối lượng
- **Relevance**: Very meaningful. Inventory, forecasting, and sales planning will be driven primarily by Phân loại 1 because it represents the bulk of observed activity.

### Phân loại groups are highly uneven in average khối lượng
- **Description**: Average khối lượng differs sharply across Phân loại groups, with groups 1 and 1A much heavier on average than groups 2 and 3.
- **Strength**: strong
- **Variables**: Phân loại, Khối lượng
- **Relevance**: Meaningful for production and logistics. Different Phân loại groups likely require different handling and stocking assumptions because average shipment weight is not uniform.

### Loại Hàng is count-dominated by PPGL but average khối lượng is higher for GL
- **Description**: PPGL accounts for most records and total khối lượng, but GL has the higher average khối lượng per record.
- **Strength**: strong
- **Variables**: Loại Hàng, count, Khối lượng, Độ D
- **Relevance**: Meaningful. PPGL drives volume through frequency, while GL contributes heavier average transactions. Sales and fulfillment strategies may differ by product type.

### Độ M is concentrated in AZ050 and AZ080
- **Description**: Most observations and total khối lượng are concentrated in two coating levels: AZ050 and AZ080.
- **Strength**: strong
- **Variables**: Độ M, count, Khối lượng
- **Relevance**: Highly meaningful. Product planning and procurement should focus on AZ050 and AZ080 because they represent the clear majority of demand.

### Higher Độ M groups tend to have higher average khối lượng among well-represented groups
- **Description**: Among the larger Độ M groups, average khối lượng rises from AZ030 to AZ050 to AZ080, with AZ100 also high but based on a smaller sample.
- **Strength**: moderate
- **Variables**: Độ M, Khối lượng
- **Relevance**: Potentially meaningful for pricing, transport, and stock planning, especially across AZ030/AZ050/AZ080 where sample sizes are substantial.

## Anomaly Patterns

Found 14 patterns:

### Severe zero-inflation in Met B
- **Description**: Met B is dominated by zeros, with a small number of very large positive values creating an extremely concentrated and highly skewed distribution.
- **Strength**: strong
- **Variables**: Met B
- **Relevance**: This looks more like a structural/sparse field than random noise. Treat as zero-inflated or two-part data in downstream analysis; avoid standard normal-based methods. Investigate whether zero means 'not applicable' versus true zero usage.

### Severe zero-inflation and point-mass behavior in Met C
- **Description**: Met C is almost entirely fixed at 2, with a small set of much larger values creating a highly abnormal distribution.
- **Strength**: strong
- **Variables**: Met C
- **Relevance**: This may reflect a default/constant setting with occasional exceptions, or a coded business rule. For downstream analysis, treat 2 as a dominant baseline category and analyze deviations separately. Also check whether this field is partly categorical rather than continuous.

### Rare-event binary flag in Cờ_giao_dịch_bất_thường
- **Description**: The abnormal-transaction flag is highly imbalanced, with very few positive cases.
- **Strength**: strong
- **Variables**: Cờ_giao_dịch_bất_thường
- **Relevance**: This is likely a real business-event flag rather than a data error. In downstream analysis, use class-imbalance-aware methods and avoid interpreting IQR outlier flags here as data-quality problems.

### Single extreme high outlier in Tỷ trọng thực tế
- **Description**: Tỷ trọng thực tế is mostly stable but contains one very large high-end value far above the normal range.
- **Strength**: strong
- **Variables**: Tỷ trọng thực tế
- **Relevance**: Because there is only one flagged case, this could be either a data-entry/calculation issue or a genuinely unusual product configuration. It should be individually audited; downstream models should winsorize or exclude it in sensitivity checks.

### Heavy low-end outliers in Khối lượng
- **Description**: Khối lượng shows a concentration in the upper range with a substantial set of unusually small transactions pulling the distribution left.
- **Strength**: strong
- **Variables**: Khối lượng
- **Relevance**: These are likely either small special orders or potentially problematic records if such low weights are not operationally plausible. Downstream analysis should segment small-volume transactions or use robust statistics instead of simple averages.

