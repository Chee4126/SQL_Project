# Backend

API sử dụng Django REST Framework.

## Cài đặt cơ bản
```bash
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Sau đó cấu hình file `.env` và Django settings trước khi chạy server.

Backend mặc định dùng SQLite; sao chép `.env.example` thành `.env` để cấu
hình MySQL. Khởi tạo schema và chạy API:

```bash
python manage.py migrate
python manage.py runserver
```

Chạy kiểm tra:

```bash
python manage.py test apps.services apps.vehicles apps.invoices
```

## Hóa đơn

`POST /api/invoices/generate` lập hoặc cập nhật hóa đơn chưa thanh toán cho
một sinh viên trong tháng/năm. Backend tự cộng dịch vụ theo đơn giá lúc sử
dụng, vé tháng và phí lượt xe đã lưu. Ví dụ:

```json
{
  "student_id": "SV001",
  "month": 11,
  "year": 2026,
  "room_amount": "500000.00"
}
```

`room_amount` là khoản tiền phòng bắt buộc do quản lý nhập lần đầu vì dự án
hiện chưa có mô hình phòng, đơn giá phòng và lịch sử phân phòng để tự tính.
Có thể bỏ qua trường này khi lập lại hóa đơn chưa thanh toán để giữ giá trị
đã nhập. Hóa đơn đã thanh toán không thể lập lại.

Tra cứu bằng `GET /api/invoices` (lọc tùy chọn `student_id`, `month`, `year`,
`status`), xem một hóa đơn bằng `GET /api/invoices/{id}`, và đổi trạng thái
bằng `PATCH /api/invoices/{id}/status` với `{"status":"DA_THANH_TOAN"}` hoặc
`{"status":"CHUA_THANH_TOAN"}`.

## Báo cáo

- `GET /api/reports/monthly-student-costs?month=M&year=YYYY`: các khoản và
  tổng tiền từ hóa đơn đã lập, sắp xếp theo tên sinh viên.
- `GET /api/reports/service-usage?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD`:
  tổng số lượng và tiền dịch vụ trong khoảng ngày.
- `GET /api/reports/service-revenue?year=YYYY&month=M`: số lượng và doanh thu
  từng dịch vụ trong tháng.
- `GET /api/reports/vehicle-registration-limits?month=M&year=YYYY`: số xe
  đăng ký theo sinh viên và trạng thái có nằm trong giới hạn 2 xe hay không.

Chi phí tháng phản ánh hóa đơn đã có, không phải danh sách đầy đủ sinh viên
đang ở vì backend chưa có lịch sử phân phòng. Báo cáo sức chứa phòng và lượt
thăm đang chờ các module phòng/phân phòng/khách/lượt thăm có dữ liệu nguồn.
