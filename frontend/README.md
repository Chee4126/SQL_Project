# Frontend

Giao diện React + Vite.

## Chức năng hiện có

- **Tài khoản:** Staff đăng ký bằng họ tên, email, số điện thoại và mật khẩu;
  đăng nhập bằng email. Mọi tài khoản có cùng vai trò Staff, có thể sửa hồ sơ,
  đổi mật khẩu và quản lý danh sách tài khoản. Hệ thống không phân cấp
  quyền giữa các tài khoản.
- **Dịch vụ:** xem danh mục, thêm/cập nhật tên, đơn giá và đơn vị; ghi nhận
  mức sử dụng theo mã sinh viên; tra cứu tổng hợp sử dụng theo khoảng ngày.
  Backend chốt đơn giá tại thời điểm ghi nhận nên cập nhật giá không đổi lịch
  sử dụng cũ.
- **Xe:** đăng ký vé tháng theo sinh viên và kỳ; lọc danh sách đăng ký; ghi
  nhận lượt gửi/lấy. Backend áp dụng mức 100.000 đồng/xe/tháng, giới hạn hai
  xe mỗi sinh viên/kỳ, miễn phí hai lượt đầu mỗi ngày và tính 3.000 đồng cho
  mỗi lượt tiếp theo.

Các chức năng phân phòng, ghi nhận khách thăm, sử dụng dịch vụ, đăng ký xe
và lập hóa đơn chọn sinh viên từ danh sách hồ sơ đã tạo; mã và họ tên được lấy
từ API sinh viên. Backend vẫn xác thực mã sinh viên và các giới hạn nghiệp vụ
khi lưu. API hiện chưa cung cấp danh sách lịch sử lượt xe hoặc danh
sách từng giao dịch dịch vụ; giao diện chỉ hiển thị kết quả vừa ghi nhận và
báo cáo tổng hợp theo nhóm.

## Cài đặt và chạy
```bash
npm install
npm run dev
```

Đặt `VITE_API_URL` nếu backend không chạy tại `http://127.0.0.1:8000/api`.
