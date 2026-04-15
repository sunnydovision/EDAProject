# Data Quality Report

## Tóm tắt

- **Tổng số vấn đề**: 20
- **Vấn đề nghiêm trọng**: 3
- **Điểm chất lượng**: 75/100

## Missing Values

- **Mã màu**: 32.0% (332 rows)
- **Tên màu**: 32.0% (332 rows)
- **Khu Vực (Quận/Huyện)**: 4.7% (49 rows)
- **Khoảng_cách_đơn_trước**: 4.1% (42 rows)

## Outliers

- **Năm**: 21.7% (225 outliers)
- **Tháng**: 21.7% (225 outliers)
- **Thành Tiền**: 10.6% (110 outliers)
- **Doanh_thu_trên_mm**: 10.6% (110 outliers)
- **Tỷ_trọng_doanh_thu_%**: 10.6% (110 outliers)
- **Khối lượng**: 9.6% (99 outliers)
- **Met A**: 8.6% (89 outliers)
- **Khoảng_cách_đơn_trước**: 8.1% (84 outliers)
- **Met C**: 4.2% (44 outliers)
- **Met B**: 3.9% (40 outliers)

## Vấn đề nghiêm trọng

### Thiếu giá trị trong các trường Mã màu và Tên màu
- **Mức độ**: high
- **Tác động**: Thiếu thông tin này có thể dẫn đến khó khăn trong việc phân tích và phân loại dữ liệu, ảnh hưởng đến khả năng ra quyết định.
- **Khuyến nghị**: Cần thu thập và bổ sung thông tin cho các trường Mã màu và Tên màu.

### Số lượng ngoại lệ cao trong các trường Khối lượng và Thành Tiền
- **Mức độ**: high
- **Tác động**: Các giá trị ngoại lệ có thể làm sai lệch kết quả phân tích và dẫn đến quyết định không chính xác.
- **Khuyến nghị**: Cần kiểm tra và làm sạch dữ liệu để loại bỏ hoặc điều chỉnh các giá trị ngoại lệ.

### Năm và Tháng có nhiều giá trị ngoại lệ
- **Mức độ**: medium
- **Tác động**: Giá trị không hợp lệ trong các trường này có thể gây nhầm lẫn trong việc phân tích theo thời gian.
- **Khuyến nghị**: Cần xác minh và điều chỉnh các giá trị năm và tháng để đảm bảo tính chính xác.

