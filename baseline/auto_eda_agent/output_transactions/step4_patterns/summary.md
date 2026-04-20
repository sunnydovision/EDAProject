# Pattern Discovery Report

## Summary

- **Total Patterns**: 49
- **Pattern Categories**: 4

## Temporal Patterns

Found 11 patterns:

### STT mean increases every month
- **Description**: The monthly average of STT shows a continuous month-over-month rise across the full observed period.
- **Strength**: strong
- **Variables**: STT
- **Relevance**: This indicates a clear upward time trend in the record index values over time, which is expected for sequential numbering and confirms later months contain higher-indexed records.

### STT sum trends upward overall with a dip in November
- **Description**: The monthly sum of STT increases strongly overall from August to January, but the pattern is interrupted by a decline in November before resuming growth.
- **Strength**: moderate
- **Variables**: STT
- **Relevance**: This shows overall expansion in total indexed activity over time, though November breaks the upward pattern.

### Transaction count peaks in October, drops in November, then recovers
- **Description**: Monthly record count rises sharply into October, falls to the lowest point in November, and then rebounds in December and January.
- **Strength**: strong
- **Variables**: STT count, Độ D count, Khối lượng count, Met A count, Met B count
- **Relevance**: This indicates the volume of monthly records is uneven over time, with a pronounced October surge and November slowdown.

### Độ D mean remains highly stable over time
- **Description**: The monthly average of Độ D changes very little across the six months, indicating no meaningful time trend in average thickness.
- **Strength**: strong
- **Variables**: Độ D
- **Relevance**: Average product thickness appears temporally stable, suggesting little month-to-month shift in the thickness mix sold.

### Độ D sum follows count-driven fluctuations
- **Description**: The monthly total of Độ D rises and falls in the same general pattern as monthly record counts, while the mean stays stable.
- **Strength**: moderate
- **Variables**: Độ D, Độ D count
- **Relevance**: Changes in total thickness sold appear to be driven more by the number of records than by changes in average thickness per record.

## Correlation Patterns

Found 11 patterns:

### Revenue metrics move almost identically
- **Description**: Thành Tiền, Doanh_thu_trên_mm, and Tỷ_trọng_doanh_thu_% show near-perfect positive co-movement. When one increases, the others increase almost one-for-one across records. This is very likely structural rather than behavioral, because these variables appear to be revenue-based transformations or normalizations of the same underlying sales value.
- **Strength**: strong
- **Variables**: Thành Tiền, Doanh_thu_trên_mm, Tỷ_trọng_doanh_thu_%
- **Relevance**: These measures are effectively redundant for correlation purposes. In analysis or modeling, keeping all three may duplicate the same revenue signal rather than reveal distinct business behavior.

### Sales mass strongly drives line revenue
- **Description**: Khối lượng has a very strong positive relationship with Thành Tiền and with the two revenue-derived metrics. Higher sold mass is associated with higher revenue per line. This likely reflects direct commercial dependence: larger transaction volumes generate larger invoice values. The relationship is likely partly structural because revenue commonly depends on quantity sold.
- **Strength**: strong
- **Variables**: Khối lượng, Thành Tiền, Doanh_thu_trên_mm, Tỷ_trọng_doanh_thu_%
- **Relevance**: Transaction revenue is highly volume-driven. Operationally, changes in sold weight are closely tied to changes in recognized sales value.

### Length measure Met A rises with sold mass and revenue
- **Description**: Met A is strongly positively associated with Khối lượng and also with revenue metrics. Longer measured product length tends to coincide with heavier transactions and higher revenue. This may be partly structural if length contributes to physical quantity, and partly operational because longer cuts/orders likely represent larger sales lines.
- **Strength**: strong
- **Variables**: Met A, Khối lượng, Thành Tiền, Doanh_thu_trên_mm, Tỷ_trọng_doanh_thu_%
- **Relevance**: Order size in linear meters is closely linked to both physical shipment size and revenue outcome, so Met A appears to be an important scale variable in transactions.

### Material thickness strongly aligns with actual weight density
- **Description**: Độ D and Tỷ trọng thực tế have a very strong positive relationship. Thicker material is associated with higher actual weight density. This looks structural, as thickness would directly affect mass per unit length or similar physical density measures.
- **Strength**: strong
- **Variables**: Độ D, Tỷ trọng thực tế
- **Relevance**: This confirms a strong physical dependency in the product data: thickness is a major determinant of actual weight-per-unit behavior.

### Product sales frequency and product revenue move together
- **Description**: Số_lần_bán_sản_phẩm and Tổng_doanh_thu_sản_phẩm are almost perfectly positively correlated. Products sold more often also generate much higher total revenue. This is likely largely structural, because cumulative product revenue naturally increases as the number of sales occurrences increases.
- **Strength**: strong
- **Variables**: Số_lần_bán_sản_phẩm, Tổng_doanh_thu_sản_phẩm
- **Relevance**: Product-level revenue concentration is strongly tied to repeat selling. High-frequency products are also the main revenue contributors.

## Grouping Patterns

Found 15 patterns:

### Phân loại 1 áp đảo rõ rệt về số dòng và khối lượng
- **Description**: Trong biến Phân loại, nhóm 1 chiếm phần lớn số bản ghi và tổng khối lượng, vượt xa tất cả các nhóm còn lại.
- **Strength**: strong
- **Variables**: Phân loại, count, Khối lượng
- **Relevance**: Rất quan trọng cho quyết định tồn kho, mua hàng và ưu tiên vận hành vì phần lớn hoạt động tập trung ở Phân loại 1.

### Khối lượng trung bình giảm mạnh ở các phân loại 2 và 3
- **Description**: Các nhóm Phân loại có quy mô giao dịch trung bình rất khác nhau, trong đó nhóm 2 và đặc biệt nhóm 3 có khối lượng trung bình thấp hơn rõ rệt so với nhóm 1/1A/1B.
- **Strength**: strong
- **Variables**: Phân loại, Khối lượng.mean
- **Relevance**: Có ý nghĩa trong phân khúc đơn hàng: nhóm 2 và 3 có thể cần chính sách bán hàng, giao hàng hoặc chi phí phục vụ khác với nhóm 1/1A.

### Độ dày theo Phân loại khá đồng đều, không có chênh lệch lớn
- **Description**: Mặc dù khác biệt lớn về số lượng và khối lượng, độ dày trung bình giữa các nhóm Phân loại lại khá gần nhau.
- **Strength**: moderate
- **Variables**: Phân loại, Độ D.mean
- **Relevance**: Cho thấy khác biệt giữa các phân loại chủ yếu nằm ở quy mô giao dịch/khối lượng hơn là độ dày; điều này hữu ích khi chuẩn hóa kỹ thuật sản phẩm.

### PPGL chiếm ưu thế về số dòng và tổng khối lượng so với GL
- **Description**: Trong Loại Hàng, PPGL là nhóm chiếm đa số cả về số lượng giao dịch lẫn tổng khối lượng.
- **Strength**: strong
- **Variables**: Loại Hàng, count, Khối lượng.sum
- **Relevance**: Rất quan trọng để phân bổ nguồn lực bán hàng, kế hoạch cung ứng và danh mục sản phẩm trọng tâm.

### GL có khối lượng trung bình mỗi dòng cao hơn PPGL
- **Description**: Dù PPGL chiếm tổng quy mô lớn hơn, mỗi dòng giao dịch GL lại có khối lượng trung bình cao hơn.
- **Strength**: moderate
- **Variables**: Loại Hàng, Khối lượng.mean
- **Relevance**: Hữu ích cho tối ưu vận chuyển và xử lý đơn: đơn GL có xu hướng nặng hơn trên mỗi dòng, dù tổng số dòng ít hơn.

## Anomaly Patterns

Found 12 patterns:

### Zero-inflation cực mạnh ở Met B
- **Description**: Met B có phân phối tập trung gần như hoàn toàn tại 0, chỉ một nhóm nhỏ giá trị dương rất lớn kéo trung bình lên cao. Đây là mẫu zero-inflation rõ rệt kèm đuôi phải rất dài.
- **Strength**: strong
- **Variables**: Met B
- **Relevance**: Khả năng cao đây là biến cấu trúc có nhiều giao dịch không có phần Met B, không nhất thiết là lỗi dữ liệu. Trong phân tích downstream nên tách thành hai biến: cờ Met B > 0 và giá trị Met B có điều kiện khi > 0; tránh dùng giả định chuẩn hoặc chỉ dùng mean.

### Zero-inflation/one-point inflation ở Met C với giá trị nền bằng 2
- **Description**: Met C gần như cố định ở mức 2, chỉ một số ít quan sát tăng vọt lên các giá trị lớn hơn nhiều. Đây là phân phối bất thường kiểu point-mass inflation hơn là phân phối liên tục thông thường.
- **Strength**: strong
- **Variables**: Met C
- **Relevance**: Nhiều khả năng đây là giá trị mặc định/quy cách chuẩn và một số giao dịch đặc biệt lệch khỏi chuẩn. Nên xử lý như biến rời rạc có mode rất mạnh; cân nhắc tạo cờ Met C != 2 thay vì chuẩn hóa như biến số liên tục.

### Giá trị thấp bất thường kéo lệch mạnh ở Khối lượng
- **Description**: Khối lượng có cụm chính ở mức cao nhưng tồn tại một nhóm nhỏ giá trị rất thấp, tạo lệch trái mạnh và đuôi dày.
- **Strength**: strong
- **Variables**: Khối lượng
- **Relevance**: Có thể là các đơn hàng nhỏ bất thường hoặc lỗi nhập liệu/đơn vị ở một số dòng rất thấp. Trong phân tích doanh thu hay nhu cầu nên winsorize/capping phía thấp hoặc kiểm tra logic đơn vị cho các giá trị dưới 2385.

### Đuôi trái mạnh ở Thành Tiền và các biến doanh thu dẫn xuất
- **Description**: Thành Tiền và các biến dẫn xuất từ doanh thu có phân phối lệch trái rõ rệt do một nhóm nhỏ giao dịch doanh thu rất thấp so với cụm chính.
- **Strength**: strong
- **Variables**: Thành Tiền, Doanh_thu_trên_mm, Tỷ_trọng_doanh_thu_%
- **Relevance**: Vì ba biến cùng chia sẻ đúng mẫu lệch và cùng số lượng ngoại lệ, đây nhiều khả năng là các giao dịch doanh thu thấp thực sự hơn là lỗi ngẫu nhiên đơn lẻ. Nên dùng median/quantile thay mean trong báo cáo; kiểm tra riêng các giao dịch doanh thu cực thấp trước khi huấn luyện mô hình.

### Ngoại lệ cực hiếm nhưng rất xa ở Tỷ trọng thực tế
- **Description**: Tỷ trọng thực tế nhìn chung ổn định, nhưng có một giá trị cực cao tách biệt rõ khỏi phần còn lại.
- **Strength**: strong
- **Variables**: Tỷ trọng thực tế
- **Relevance**: Vì chỉ có 1 điểm ngoại lệ và khoảng cách rất lớn so với upper bound, đây là ứng viên mạnh cho lỗi dữ liệu hoặc trường hợp nghiệp vụ rất hiếm. Nên rà soát thủ công bản ghi này; trong phân tích tổng quát có thể loại hoặc winsorize.

