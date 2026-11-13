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

## Tài khoản

- `POST /api/auth/register` tạo tài khoản có vai trò `STAFF` bằng `full_name`,
  `email`, `phone_number`, `password` và `password_confirm`; đăng ký thành
  công trả token để đăng nhập ngay. Mọi tài khoản có cùng vai trò `STAFF`.
- `POST /api/auth/login` đăng nhập bằng `email` và `password`.
- `GET /api/auth/me` xem hồ sơ tài khoản; `PATCH /api/auth/me` cập nhật họ
  tên, email, số điện thoại. Đổi mật khẩu yêu cầu mật khẩu hiện tại,
  `new_password` và `password_confirm`.
- Người dùng đã đăng nhập có thể xem và tạo tài khoản Staff qua
  `GET`/`POST /api/accounts`; có thể xóa tài khoản khác bằng
  `DELETE /api/accounts/{user_id}`. Không thể tự xóa tài khoản đang đăng
  nhập. Không có API phân quyền vì hệ thống chỉ có một vai trò.

## Xóa danh mục

Các thao tác xóa danh mục cần xác thực và chỉ xóa cứng bản ghi chưa được
dùng trong dữ liệu nghiệp vụ:

- `DELETE /api/students/{student_id}` bị từ chối nếu sinh viên có phân
  phòng, lượt thăm, lượt dùng dịch vụ, đăng ký xe hoặc hóa đơn.
- `DELETE /api/rooms/{room_id}` bị từ chối nếu phòng có lịch sử phân phòng.
- `DELETE /api/services/{id}` bị từ chối nếu dịch vụ có lượt sử dụng.
- `DELETE /api/accounts/{user_id}` bị từ chối nếu đó là tài khoản hiện tại.

Các lỗi do bản ghi đã được tham chiếu trả HTTP 400 cùng lý do cụ thể.
Không xóa giao dịch hay lịch sử. Xe được tạo cùng đăng ký vé tháng nên
không có thao tác xóa xe, đăng ký xe hoặc lượt gửi/lấy.

Chạy kiểm tra:

```bash
python manage.py test
```

## Hóa đơn

`POST /api/invoices/generate` lập hoặc cập nhật hóa đơn chưa thanh toán cho
một sinh viên trong tháng/năm. Backend tự cộng dịch vụ theo đơn giá lúc sử
dụng và vé tháng; lượt gửi/lấy xe không phát sinh phí. Ví dụ:

```json
{
  "student_id": "SV001",
  "month": 11,
  "year": 2026,
  "room_amount": "500000.00"
}
```

`room_amount` là khoản tiền phòng bắt buộc do quản lý nhập lần đầu vì dự án
chưa tự tính tiền từ lịch sử phân phòng. Đơn giá và sức chứa được cấu hình
trên từng phòng, nhưng chưa tự tổng hợp vào hóa đơn. Có thể bỏ qua trường
này khi lập lại hóa đơn chưa thanh toán để giữ giá trị đã nhập. Hóa đơn đã
thanh toán không thể lập lại.

## Phòng

`POST /api/rooms` tạo phòng với `room_id`, `name`, `floor`,
`monthly_price` và `max_occupants`. Chỉ hợp lệ hai cặp cấu hình:
1.800.000 đồng/tháng với sức chứa 4 người hoặc 250.000 đồng/tháng với sức
chứa 8 người. Phân phòng kiểm tra sức chứa theo lựa chọn của phòng.

Tra cứu bằng `GET /api/invoices` (lọc tùy chọn `student_id`, `month`, `year`,
`status`), xem một hóa đơn bằng `GET /api/invoices/{id}`, và đổi trạng thái
bằng `PATCH /api/invoices/{id}/status` với `{"status":"DA_THANH_TOAN"}` hoặc
`{"status":"CHUA_THANH_TOAN"}`.

## Báo cáo

- `GET /api/reports/monthly-student-costs?month=M&year=YYYY`: các khoản và
  tổng tiền của sinh viên có lượt phân phòng giao với tháng được chọn,
  sắp xếp theo tên; báo cáo lấy trực tiếp từ lượt ở, sử dụng dịch vụ và
  đăng ký vé tháng, không yêu cầu hóa đơn đã lập. Tiền phòng tính trọn tháng
  nếu sinh viên ở ít nhất một ngày.
- `GET /api/reports/service-usage?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD`:
  tổng số lượng và tiền dịch vụ trong khoảng ngày.
- `GET /api/reports/service-revenue?year=YYYY&month=M`: số lượng và doanh thu
  từng dịch vụ trong tháng.
- `GET /api/reports/vehicle-registration-limits?month=M&year=YYYY`: số xe
  đăng ký theo sinh viên và trạng thái có nằm trong giới hạn 2 xe hay không.

Chi phí tháng chỉ liệt kê sinh viên có lượt phân phòng giao với tháng được
chọn. Báo cáo sức chứa phòng và lượt thăm lấy dữ liệu từ các module tương ứng.
