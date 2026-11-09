# Database

Thư mục chứa các script MySQL để tạo CSDL quản lý ký túc xá, nhập dữ liệu
mẫu và chạy các truy vấn của Project 2.

## Yêu cầu

- MySQL 8.0.16 trở lên (để thực thi các ràng buộc `CHECK`).

## Tạo CSDL và dữ liệu mẫu

Mở Command Prompt tại thư mục gốc của dự án và chạy lần lượt:

```cmd
mysql -u root -p < database\create_database.sql
mysql -u root -p < database\create_tables.sql
mysql -u root -p < database\insert_data.sql
```

Hoặc mở MySQL client rồi chạy lần lượt:

```sql
SOURCE database/create_database.sql;
SOURCE database/create_tables.sql;
SOURCE database/insert_data.sql;
```

Dữ liệu mẫu tập trung vào kỳ tháng 03/2025. Script nhập dữ liệu có thể
chạy lại để khôi phục các bản ghi mẫu.

## Chạy truy vấn

```cmd
mysql -u root -p < database\queries.sql
```

Script `queries.sql` gồm các báo cáo chi phí tháng, chi phí dịch vụ theo
khoảng ngày, lượt khách theo tuần/tháng, doanh thu dịch vụ theo tháng,
sức chứa phòng và giới hạn đăng ký xe. Có thể sửa các biến ngày/tháng/năm
ở đầu từng phần truy vấn để chọn kỳ khác.

Các truy vấn kiểm tra sức chứa và số xe nhằm phát hiện dữ liệu vi phạm.
Backend vẫn cần thực hiện các kiểm tra này trong transaction để tránh
phân phòng hoặc đăng ký xe vượt giới hạn khi có thao tác đồng thời.
