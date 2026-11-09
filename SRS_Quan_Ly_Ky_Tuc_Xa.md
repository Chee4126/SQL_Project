# ĐẶC TẢ YÊU CẦU PHẦN MỀM (SRS)
# HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ SINH VIÊN

**Phiên bản:** 2.0  
**Ngày cập nhật:** 05/11/2026  
**Công nghệ dự kiến:** React + Vite, Python, Django REST Framework, MySQL

# 1. TỔNG QUAN HỆ THỐNG

## 1.1. Giới thiệu

Hệ thống quản lý ký túc xá sinh viên được xây dựng để hỗ trợ ban quản lý
theo dõi sinh viên đang ở, phòng ở, khách đến thăm, dịch vụ sử dụng, xe
đăng ký vé tháng, lượt gửi/lấy xe và hóa đơn hàng tháng.

Hệ thống giúp tập trung dữ liệu, hỗ trợ thực hiện các quy tắc nghiệp vụ
về sức chứa phòng, phí dịch vụ, phí gửi xe và cung cấp các báo cáo phục
vụ công tác quản lý.

Hệ thống có hai nhóm người sử dụng chính:

- **Quản trị viên (Admin):** quản lý tài khoản và toàn bộ dữ liệu, cấu
  hình, nghiệp vụ của hệ thống.
- **Nhân viên (Staff):** thực hiện các nghiệp vụ được phân quyền như
  quản lý sinh viên, phòng, khách thăm, dịch vụ, xe và hóa đơn.

Sinh viên và khách là các đối tượng được quản lý trong hệ thống; việc
cấp tài khoản đăng nhập cho họ không thuộc phạm vi yêu cầu hiện tại.

Frontend và Backend được xây dựng tách biệt. Frontend cung cấp giao diện
cho người dùng; Backend tiếp nhận yêu cầu, kiểm tra quy tắc nghiệp vụ
và làm việc với cơ sở dữ liệu.

## 1.2. Mục tiêu của hệ thống

Hệ thống hướng tới các mục tiêu:

- Quản lý hồ sơ sinh viên và lịch sử ở phòng.
- Quản lý phòng, loại phòng, đơn giá và sức chứa.
- Theo dõi khách đến thăm sinh viên theo thời gian.
- Quản lý danh mục dịch vụ và các lần sinh viên sử dụng dịch vụ.
- Quản lý đăng ký vé xe tháng, lượt gửi/lấy xe và phí phát sinh.
- Tổng hợp chi phí và lập hóa đơn hàng tháng cho sinh viên.
- Cung cấp truy vấn, báo cáo về sinh viên, doanh thu, khách thăm và
  tình trạng phòng.
- Đảm bảo các ràng buộc nghiệp vụ được kiểm tra nhất quán ở Backend và
  Database.

## 1.3. Đối tượng sử dụng

### Admin

Admin quản trị hệ thống và có thể:

- Quản lý tài khoản, vai trò và quyền truy cập.
- Quản lý thông tin sinh viên, phòng, loại phòng, khách, dịch vụ và xe.
- Theo dõi phân phòng, lượt thăm, sử dụng dịch vụ và gửi/lấy xe.
- Tạo, tra cứu và theo dõi hóa đơn.
- Xem các báo cáo và thống kê của ký túc xá.

### Nhân viên

Nhân viên thực hiện các nghiệp vụ hằng ngày theo quyền được cấp, bao gồm:

- Cập nhật hồ sơ sinh viên và tình trạng ở.
- Ghi nhận khách đến thăm và thời gian đến/rời đi.
- Quản lý danh mục dịch vụ và ghi nhận sử dụng dịch vụ.
- Ghi nhận đăng ký vé tháng và các lượt gửi/lấy xe thuộc diện lưu trữ.
- Tra cứu hóa đơn, tình trạng phòng và các báo cáo được phân quyền.

### Sinh viên và khách

Sinh viên là đối tượng được quản lý về hồ sơ, chỗ ở, dịch vụ, xe tháng,
khách thăm và công nợ. Khách là đối tượng được ghi nhận khi đến thăm
sinh viên. Hai nhóm này không có quyền truy cập hệ thống theo phạm vi
hiện tại.

## 1.4. Công nghệ và công cụ sử dụng

| Công nghệ/Công cụ | Mục đích |
|---|---|
| React | Xây dựng giao diện Frontend |
| Vite | Phục vụ phát triển và đóng gói Frontend |
| JavaScript | Phát triển Frontend |
| Python | Ngôn ngữ lập trình Backend |
| Django | Xây dựng nền tảng Backend |
| Django REST Framework | Xây dựng REST API |
| MySQL | Lưu trữ dữ liệu |
| npm | Quản lý thư viện Frontend |
| pip / `requirements.txt` | Quản lý thư viện Backend |
| VS Code | Môi trường phát triển |
| Postman | Kiểm thử API |
| Git | Quản lý mã nguồn |

## 1.5. Các quy tắc nghiệp vụ chính

- Mã sinh viên định danh duy nhất cho mỗi sinh viên.
- Mỗi phòng thuộc một loại phòng, có đơn giá và số người tối đa theo
  loại phòng.
- Không được phân phòng làm số người ở vượt quá sức chứa; một sinh viên
  không được ở đồng thời tại nhiều phòng.
- Nếu sinh viên ở phòng ít nhất một ngày trong tháng thì tiền phòng
  được tính trọn tháng theo đơn giá phòng.
- Một sinh viên có thể sử dụng một dịch vụ nhiều lần; tiền dịch vụ được
  cộng dồn theo tháng và theo giá tại thời điểm sử dụng.
- Một sinh viên được đăng ký tối đa 2 xe vé tháng trong một tháng. Giá
  vé là 100.000 đồng/xe/tháng.
- Đối với mỗi xe vé tháng, hai lượt gửi/lấy đầu tiên trong ngày được
  miễn phí; từ lượt thứ ba, mỗi lượt gửi hoặc lấy tính 3.000 đồng.
- Chỉ lưu xe và lịch sử lượt gửi/lấy của xe đăng ký vé tháng. Xe không
  đăng ký vé tháng được tính phí riêng cho từng lượt và không lưu trong
  CSDL.
- Mỗi sinh viên có tối đa một hóa đơn trong một tháng/năm. Hóa đơn gồm
  tiền phòng, dịch vụ, vé tháng và phí gửi/lấy xe phát sinh.
- Các thay đổi có ảnh hưởng tới sức chứa phòng, số xe đăng ký và phí
  phải được kiểm tra nhất quán ở Backend; không chỉ dựa vào giao diện.

# 2. PHÂN TÍCH NGHIỆP VỤ

## 2.1. Mô hình hoạt động

Hệ thống hỗ trợ các nghiệp vụ quản lý ký túc xá từ lúc tiếp nhận hồ sơ
sinh viên, sắp xếp chỗ ở đến khi tổng hợp chi phí hàng tháng.

Quy trình tổng quát:

Ban quản lý

↓

Quản lý sinh viên và phòng

↓

Ghi nhận khách thăm, dịch vụ và xe tháng

↓

Tổng hợp tiền phòng và các khoản phí

↓

Lập hóa đơn tháng

↓

Tra cứu và lập báo cáo

## 2.2. Nghiệp vụ quản lý sinh viên và phòng

Hồ sơ sinh viên gồm mã sinh viên, họ tên, số CMT/CCCD, ngày sinh, lớp
và quê quán. Khi sinh viên vào hoặc rời ký túc xá, hệ thống ghi nhận
thời gian phân phòng để theo dõi tình trạng hiện tại và lịch sử.

Phòng được quản lý theo số phòng và loại phòng. Loại phòng quy định đơn
giá và số người tối đa. Khi phân phòng, hệ thống phải xác định số người
đang ở trong khoảng thời gian tương ứng và từ chối thao tác nếu vượt sức
chứa hoặc sinh viên đang có một lượt phân phòng còn hiệu lực.

Tiền phòng được tính trọn tháng nếu sinh viên ở phòng ít nhất một ngày
trong tháng. Lịch sử phân phòng phải được giữ lại sau khi sinh viên
chuyển phòng hoặc rời ký túc xá.

## 2.3. Nghiệp vụ khách thăm

Hệ thống lưu hồ sơ khách gồm họ tên, số CMT/CCCD và ngày sinh. Mỗi lần
khách đến thăm cần ghi nhận khách, sinh viên được thăm, thời gian đến và
thời gian rời đi (nếu đã rời).

Dữ liệu lượt thăm được sử dụng để tra cứu khách đã đến thăm sinh viên
nào và thống kê số lần thăm theo tuần hoặc tháng.

## 2.4. Nghiệp vụ dịch vụ

Hệ thống quản lý danh mục dịch vụ, đơn giá và đơn vị tính. Các dịch vụ
có thể gồm giặt là, nước uống hoặc các dịch vụ khác của ký túc xá.

Mỗi lần sử dụng dịch vụ được ghi nhận riêng, gồm sinh viên, dịch vụ,
thời gian sử dụng, số lượng và đơn giá áp dụng. Một sinh viên có thể sử
dụng cùng dịch vụ nhiều lần. Chi phí dịch vụ trong tháng được tính bằng
tổng số lượng nhân với đơn giá áp dụng của từng lần sử dụng trong tháng.

Đơn giá áp dụng được lưu cùng giao dịch để các lần sử dụng trước đó
không bị thay đổi khi giá trong danh mục được cập nhật.

## 2.5. Nghiệp vụ gửi/lấy xe

Sinh viên có thể đăng ký tối đa 2 xe vé tháng trong một tháng. Mỗi đăng
ký gồm xe, sinh viên, tháng/năm áp dụng và đơn giá vé tháng là 100.000
đồng.

Với xe có vé tháng, hệ thống lưu từng lượt gửi hoặc lấy. Hai lượt đầu
tiên trong ngày của mỗi xe (tính tổng lượt gửi và lượt lấy) được miễn
phí. Từ lượt thứ ba, mỗi sự kiện gửi hoặc lấy phát sinh 3.000 đồng và
được cộng vào hóa đơn tháng của sinh viên.

Xe không có vé tháng được thu phí riêng cho mỗi lượt gửi/lấy. Theo yêu
cầu, thông tin xe và các lượt này không được lưu trong cơ sở dữ liệu.

## 2.6. Nghiệp vụ hóa đơn và báo cáo

Hệ thống tổng hợp các khoản phát sinh theo sinh viên và tháng, gồm:

- Tiền phòng.
- Tiền các dịch vụ đã sử dụng.
- Tiền đăng ký vé tháng.
- Phí gửi/lấy xe phát sinh của xe tháng.

Mỗi sinh viên có tối đa một hóa đơn trong một tháng/năm. Hóa đơn lưu
tổng tiền và trạng thái thanh toán để nhân viên theo dõi.

Các báo cáo cần hỗ trợ tra cứu theo tháng, khoảng ngày hoặc tuần/tháng
tùy nghiệp vụ; chi tiết được mô tả tại Mục 4 và Mục 6.

# 3. PHÂN TÍCH CHỨC NĂNG

## 3.1. Chức năng dành cho Admin và nhân viên

| STT | Chức năng | Nội dung |
|---|---|---|
| 1 | Đăng nhập và phân quyền | Xác thực tài khoản; giới hạn chức năng theo vai trò Admin hoặc nhân viên. |
| 2 | Quản lý sinh viên | Xem, thêm, cập nhật và tra cứu hồ sơ sinh viên. |
| 3 | Quản lý loại phòng | Quản lý tên loại phòng, đơn giá và số người tối đa. |
| 4 | Quản lý phòng | Quản lý số phòng, loại phòng và tình trạng sử dụng. |
| 5 | Phân phòng | Ghi nhận sinh viên vào/rời phòng; kiểm tra sức chứa và thời gian phân phòng. |
| 6 | Quản lý khách | Quản lý thông tin khách đến thăm. |
| 7 | Ghi nhận lượt thăm | Ghi nhận khách, sinh viên được thăm, thời gian đến và thời gian rời đi. |
| 8 | Quản lý dịch vụ | Quản lý danh mục dịch vụ, đơn giá và đơn vị tính. |
| 9 | Ghi nhận sử dụng dịch vụ | Lưu từng lần sử dụng, số lượng, thời gian và đơn giá áp dụng. |
| 10 | Quản lý xe tháng | Quản lý xe, đăng ký vé tháng và kiểm tra giới hạn tối đa 2 xe/sinh viên/tháng. |
| 11 | Ghi nhận lượt xe | Ghi nhận lượt gửi/lấy của xe tháng và tính lượt miễn phí/phí phát sinh. |
| 12 | Quản lý hóa đơn | Tổng hợp chi phí, lập hóa đơn tháng và cập nhật trạng thái thanh toán. |
| 13 | Tra cứu và báo cáo | Tra cứu sinh viên, dịch vụ, khách thăm, phòng, hóa đơn và doanh thu. |

## 3.2. Phân quyền

| Chức năng | Admin | Nhân viên |
|---|---:|---:|
| Quản lý tài khoản và phân quyền | Có | Không |
| Quản lý dữ liệu sinh viên, phòng và dịch vụ | Có | Theo quyền được cấp |
| Ghi nhận khách thăm, sử dụng dịch vụ và lượt xe | Có | Theo quyền được cấp |
| Lập và tra cứu hóa đơn | Có | Theo quyền được cấp |
| Xem báo cáo | Có | Theo quyền được cấp |

Các quyền của nhân viên được cấu hình bởi Admin. Hệ thống không cho
phép người chưa đăng nhập hoặc không đủ quyền thực hiện thao tác quản
trị.

## 3.3. Trạng thái nghiệp vụ

### Tình trạng phân phòng

- **Đang ở:** ngày rời phòng chưa được ghi nhận.
- **Đã kết thúc:** ngày rời phòng đã được ghi nhận.

### Trạng thái hóa đơn

- **Chưa thanh toán**
- **Đã thanh toán**

### Trạng thái lượt gửi/lấy xe

Mỗi bản ghi là một sự kiện thuộc một trong hai loại:

- **Gửi xe**
- **Lấy xe**

Hệ thống xác định lượt miễn phí hay phí phát sinh dựa trên thứ tự sự
kiện của xe trong ngày.

# 4. THIẾT KẾ KIẾN TRÚC VÀ LUỒNG HỆ THỐNG

## 4.1. Kiến trúc tổng thể

Hệ thống được thiết kế theo mô hình Frontend – Backend – Database:

Frontend: React + Vite

↓ HTTP/JSON

Backend: Django REST Framework

↓ ORM / truy vấn dữ liệu

Database: MySQL

Frontend gửi yêu cầu qua REST API. Backend xác thực, kiểm tra dữ liệu,
xử lý quy tắc nghiệp vụ và trả kết quả cho Frontend.

## 4.2. Các thành phần trong Backend

- **View / ViewSet:** tiếp nhận yêu cầu HTTP, kiểm tra quyền truy cập và
  trả phản hồi.
- **Serializer:** kiểm tra dữ liệu đầu vào và định dạng dữ liệu trả về.
- **Service:** xử lý quy tắc nghiệp vụ như phân phòng, tính tiền và lập
  hóa đơn.
- **Model:** biểu diễn dữ liệu và quan hệ được lưu trong MySQL thông qua
  Django ORM.
- **Tầng truy cập dữ liệu:** thực hiện truy vấn, tạo và cập nhật dữ liệu.
  Có thể tách thành Repository khi cần tổ chức mã nguồn.

## 4.3. Luồng xử lý dữ liệu

Người dùng

↓

Frontend

↓

View / ViewSet

↓

Serializer kiểm tra dữ liệu

↓

Service xử lý nghiệp vụ

↓

Model / tầng truy cập dữ liệu

↓

MySQL

↓

Kết quả trả về Frontend

## 4.4. Luồng phân phòng

Nhân viên chọn sinh viên và phòng

↓

Frontend gửi yêu cầu phân phòng

↓

Backend kiểm tra sinh viên và phòng hợp lệ

↓

Kiểm tra sinh viên không có lượt ở trùng thời gian

↓

Đếm số người đang ở và so sánh với sức chứa

↓

Lưu lịch sử phân phòng

↓

Trả kết quả cho Frontend

Nếu sinh viên rời hoặc chuyển phòng, hệ thống cập nhật ngày kết thúc
của lượt phân phòng hiện tại và lưu lượt phân phòng tiếp theo (nếu có).

## 4.5. Luồng ghi nhận dịch vụ

Nhân viên chọn sinh viên và dịch vụ

↓

Nhập số lượng và thời gian sử dụng

↓

Backend kiểm tra dữ liệu và dịch vụ

↓

Lưu lần sử dụng cùng đơn giá áp dụng

↓

Cộng chi phí vào kỳ hóa đơn tương ứng

## 4.6. Luồng ghi nhận lượt gửi/lấy xe

Nhân viên chọn đăng ký vé tháng và loại lượt

↓

Backend xác định ngày và đếm các lượt trước đó của xe trong ngày

↓

Nếu là lượt 1 hoặc 2: miễn phí

↓

Nếu từ lượt 3: tính 3.000 đồng/lượt

↓

Lưu sự kiện và phí phát sinh

↓

Cộng phí vào hóa đơn tháng của sinh viên

Xe không có vé tháng được xử lý thu phí riêng theo từng lượt và không
tạo bản ghi xe hoặc lượt trong CSDL.

## 4.7. Luồng lập hóa đơn tháng

Chọn tháng/năm cần lập hóa đơn

↓

Lấy sinh viên có phát sinh ở ký túc xá trong kỳ

↓

Tổng hợp tiền phòng, dịch vụ, vé tháng và phí lượt xe

↓

Kiểm tra hóa đơn đã tồn tại hay chưa

↓

Tạo mới hoặc cập nhật hóa đơn theo quy trình được phân quyền

↓

Trả danh sách hóa đơn và tổng tiền

# 5. THIẾT KẾ CƠ SỞ DỮ LIỆU

## 5.1. Mục đích

MySQL lưu trữ hồ sơ và các giao dịch của ký túc xá. Các nhóm dữ liệu
chính gồm:

- Sinh viên.
- Loại phòng, phòng và lịch sử phân phòng.
- Khách và lượt thăm.
- Dịch vụ và các lần sử dụng dịch vụ.
- Xe, đăng ký vé tháng và lượt gửi/lấy xe.
- Hóa đơn tháng.

## 5.2. Quy ước thiết kế

- `PK`: khóa chính; `FK`: khóa ngoại; `UQ`: duy nhất; `NN`: không NULL.
- Các trường tiền sử dụng `DECIMAL(12,2)` và được tính bằng đồng Việt Nam.
- Mã tự tăng sử dụng kiểu số nguyên tự tăng phù hợp với MySQL.
- Các giá trị trạng thái và loại lượt chỉ nhận giá trị thuộc tập được quy
  định trong tài liệu.
- Tên bảng dưới đây là tên logic; tên vật lý có thể được ánh xạ theo quy
  ước Django hoặc dự án.

## 5.3. Bảng SINHVIEN

Bảng lưu hồ sơ sinh viên.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaSV | Mã sinh viên | VARCHAR(15) | PK |
| HoTen | Họ tên sinh viên | VARCHAR(100) | NN |
| SoCMT | Số CMT/CCCD | VARCHAR(20) | UQ |
| NgaySinh | Ngày sinh | DATE |  |
| Lop | Lớp | VARCHAR(30) |  |
| QueQuan | Quê quán | VARCHAR(150) |  |

## 5.4. Bảng LOAIPHONG

Bảng lưu loại phòng, đơn giá tháng và sức chứa.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaLoaiPhong | Mã loại phòng | INT | PK, AUTO_INCREMENT |
| TenLoaiPhong | Tên loại phòng | VARCHAR(50) | NN, UQ |
| DonGia | Đơn giá phòng theo tháng | DECIMAL(12,2) | NN, không âm |
| SoNguoiToiDa | Sức chứa tối đa | INT | NN, lớn hơn 0 |

## 5.5. Bảng PHONG

Bảng lưu danh mục phòng. Đơn giá và sức chứa được xác định theo loại
phòng.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaPhong | Mã/số phòng | VARCHAR(15) | PK |
| MaLoaiPhong | Loại phòng | INT | FK → LOAIPHONG.MaLoaiPhong |
| TenPhong | Tên hiển thị của phòng | VARCHAR(30) | NN |
| Tang | Tầng | INT |  |

## 5.6. Bảng PHANPHONG

Bảng lưu lịch sử sinh viên ở phòng.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaPhanPhong | Mã lượt phân phòng | INT | PK, AUTO_INCREMENT |
| MaSV | Sinh viên | VARCHAR(15) | FK → SINHVIEN.MaSV |
| MaPhong | Phòng | VARCHAR(15) | FK → PHONG.MaPhong |
| NgayVao | Ngày bắt đầu ở | DATE | NN |
| NgayRa | Ngày kết thúc ở | DATE | NULL |

`NgayRa` để trống nghĩa là lượt ở còn hiệu lực. Một sinh viên có thể có
nhiều lượt phân phòng trong lịch sử, nhưng không được có các lượt ở
trùng thời gian.

## 5.7. Bảng KHACH

Bảng lưu thông tin khách đến thăm.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaKhach | Mã khách | INT | PK, AUTO_INCREMENT |
| HoTen | Họ tên khách | VARCHAR(100) | NN |
| SoCMT | Số CMT/CCCD | VARCHAR(20) | UQ |
| NgaySinh | Ngày sinh | DATE |  |

## 5.8. Bảng LUOTTHAM

Bảng lưu từng lượt khách đến thăm sinh viên.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaLuotTham | Mã lượt thăm | INT | PK, AUTO_INCREMENT |
| MaKhach | Khách | INT | FK → KHACH.MaKhach |
| MaSV | Sinh viên được thăm | VARCHAR(15) | FK → SINHVIEN.MaSV |
| NgayDen | Thời gian đến | DATETIME | NN |
| NgayDi | Thời gian rời đi | DATETIME | NULL |

## 5.9. Bảng DICHVU

Bảng lưu danh mục dịch vụ.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaDV | Mã dịch vụ | INT | PK, AUTO_INCREMENT |
| TenDV | Tên dịch vụ | VARCHAR(100) | NN |
| DonGia | Đơn giá hiện tại | DECIMAL(12,2) | NN, không âm |
| DonViTinh | Đơn vị tính | VARCHAR(30) |  |

## 5.10. Bảng SUDUNGDICHVU

Bảng lưu từng lần sinh viên sử dụng dịch vụ. `DonGiaApDung` là giá tại
thời điểm ghi nhận.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaSuDung | Mã lần sử dụng | INT | PK, AUTO_INCREMENT |
| MaSV | Sinh viên | VARCHAR(15) | FK → SINHVIEN.MaSV |
| MaDV | Dịch vụ | INT | FK → DICHVU.MaDV |
| ThoiGianSuDung | Thời điểm sử dụng | DATETIME | NN |
| SoLuong | Số lượng sử dụng | INT | NN, lớn hơn 0 |
| DonGiaApDung | Đơn giá tại thời điểm sử dụng | DECIMAL(12,2) | NN, không âm |

## 5.11. Bảng XE

Bảng chỉ lưu thông tin xe đăng ký vé tháng.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| BienSo | Biển số xe | VARCHAR(20) | PK |
| LoaiXe | Loại xe | VARCHAR(50) | NN |

## 5.12. Bảng DANGKYVEXE

Bảng lưu đăng ký xe vé tháng theo sinh viên và kỳ đăng ký. Đơn giá mặc
định theo yêu cầu là 100.000 đồng/xe/tháng; giá được lưu tại đăng ký để
bảo toàn lịch sử.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaDangKy | Mã đăng ký | INT | PK, AUTO_INCREMENT |
| MaSV | Sinh viên đăng ký | VARCHAR(15) | FK → SINHVIEN.MaSV |
| BienSo | Xe đăng ký | VARCHAR(20) | FK → XE.BienSo |
| Thang | Tháng hiệu lực | INT | NN, từ 1 đến 12 |
| Nam | Năm hiệu lực | INT | NN |
| DonGia | Giá vé tháng | DECIMAL(12,2) | NN, mặc định 100.000 |

Ràng buộc duy nhất:

- `UNIQUE (MaSV, BienSo, Thang, Nam)`.
- `UNIQUE (BienSo, Thang, Nam)` để một xe không đăng ký cho nhiều sinh
  viên trong cùng tháng.
- Mỗi sinh viên đăng ký tối đa 2 xe trong cùng tháng/năm; cần kiểm tra
  bằng transaction ở Backend.

## 5.13. Bảng LUOTGUIXE

Bảng chỉ lưu sự kiện gửi/lấy của xe đã đăng ký vé tháng.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaLuot | Mã lượt xe | INT | PK, AUTO_INCREMENT |
| MaDangKy | Đăng ký vé tháng | INT | FK → DANGKYVEXE.MaDangKy |
| ThoiGian | Thời điểm gửi/lấy | DATETIME | NN |
| LoaiLuot | Loại sự kiện | ENUM('GUI','LAY') | NN |
| MienPhi | Lượt có được miễn phí không | BOOLEAN | NN |
| TienPhat | Phí lượt xe | DECIMAL(12,2) | NN, mặc định 0 |

Hai lượt đầu tiên mỗi ngày trên mỗi xe được đánh dấu miễn phí; các lượt
từ lượt thứ ba có `TienPhat` là 3.000 đồng. Việc xác định lượt phải được
thực hiện nhất quán khi có các thao tác đồng thời.

## 5.14. Bảng HOADON

Bảng lưu tổng hợp chi phí của sinh viên theo tháng/năm.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaHD | Mã hóa đơn | INT | PK, AUTO_INCREMENT |
| MaSV | Sinh viên | VARCHAR(15) | FK → SINHVIEN.MaSV |
| Thang | Tháng hóa đơn | INT | NN, từ 1 đến 12 |
| Nam | Năm hóa đơn | INT | NN |
| TienPhong | Tiền phòng | DECIMAL(12,2) | NN, không âm |
| TienDichVu | Tiền dịch vụ | DECIMAL(12,2) | NN, không âm |
| TienXe | Tiền vé tháng | DECIMAL(12,2) | NN, không âm |
| PhiGuiXe | Phí gửi/lấy xe | DECIMAL(12,2) | NN, không âm |
| TongTien | Tổng tiền phải trả | DECIMAL(12,2) | NN, không âm |
| TrangThai | Trạng thái thanh toán | ENUM('CHUA_THANH_TOAN','DA_THANH_TOAN') | NN |

Ràng buộc: `UNIQUE (MaSV, Thang, Nam)`.

`TongTien` bằng tổng `TienPhong`, `TienDichVu`, `TienXe` và `PhiGuiXe`.
Tiền phòng được tính trọn tháng nếu sinh viên ở ít nhất một ngày trong
tháng. Phí xe không vé tháng không được ghi vào CSDL theo yêu cầu.

## 5.15. Ràng buộc toàn vẹn dữ liệu

| Ràng buộc | Ý nghĩa |
|---|---|
| Khóa chính trên mỗi bảng | Không cho phép bản ghi trùng định danh. |
| Khóa ngoại | Không cho phép giao dịch tham chiếu sinh viên, phòng, dịch vụ, khách hoặc đăng ký xe không tồn tại. |
| Sức chứa phòng | Số sinh viên có thời gian ở giao với thời điểm phân phòng không vượt quá sức chứa loại phòng. |
| Thời gian phân phòng | Ngày kết thúc không được trước ngày bắt đầu; sinh viên không có hai lượt ở trùng thời gian. |
| Số lượng dịch vụ | `SoLuong` phải lớn hơn 0; đơn giá và các khoản tiền không âm. |
| Giới hạn đăng ký xe | Tối đa 2 xe vé tháng cho mỗi sinh viên trong một tháng/năm. |
| Đăng ký xe duy nhất | Một xe chỉ thuộc một đăng ký trong cùng tháng/năm. |
| Phí lượt xe | Hai lượt đầu trong ngày được miễn; lượt từ thứ ba tính 3.000 đồng. |
| Hóa đơn tháng | Mỗi sinh viên chỉ có một hóa đơn trong một tháng/năm; tổng tiền bằng tổng các khoản thành phần. |

Các kiểm tra cần đếm dữ liệu hiện có như sức chứa phòng, số xe đăng ký
và thứ tự lượt gửi/lấy phải được bảo vệ bằng transaction phù hợp. Ràng
buộc khóa ngoại, duy nhất và kiểm tra giá trị phải được đặt ở Database
khi hệ quản trị hỗ trợ.

## 5.16. Quan hệ giữa các bảng

| Bảng cha | Quan hệ | Bảng con | Cột tham chiếu |
|---|---|---|---|
| LOAIPHONG | 1-N | PHONG | PHONG.MaLoaiPhong |
| SINHVIEN | 1-N | PHANPHONG | PHANPHONG.MaSV |
| PHONG | 1-N | PHANPHONG | PHANPHONG.MaPhong |
| KHACH | 1-N | LUOTTHAM | LUOTTHAM.MaKhach |
| SINHVIEN | 1-N | LUOTTHAM | LUOTTHAM.MaSV |
| SINHVIEN | 1-N | SUDUNGDICHVU | SUDUNGDICHVU.MaSV |
| DICHVU | 1-N | SUDUNGDICHVU | SUDUNGDICHVU.MaDV |
| SINHVIEN | 1-N | DANGKYVEXE | DANGKYVEXE.MaSV |
| XE | 1-N | DANGKYVEXE | DANGKYVEXE.BienSo |
| DANGKYVEXE | 1-N | LUOTGUIXE | LUOTGUIXE.MaDangKy |
| SINHVIEN | 1-N | HOADON | HOADON.MaSV |

# 6. API

## 6.1. Khái niệm API

Frontend và Backend trao đổi dữ liệu qua REST API sử dụng HTTP và JSON.
Các API dưới đây mô tả giao diện dự kiến của hệ thống, không khẳng định
rằng các endpoint đã được triển khai.

| Phương thức | Mục đích |
|---|---|
| GET | Lấy danh sách hoặc chi tiết dữ liệu |
| POST | Tạo dữ liệu hoặc ghi nhận nghiệp vụ |
| PUT/PATCH | Cập nhật dữ liệu |
| DELETE | Xóa dữ liệu khi không làm mất tính toàn vẹn lịch sử |

Các API quản trị yêu cầu đăng nhập và kiểm tra quyền phù hợp. Danh sách
có thể hỗ trợ phân trang, tìm kiếm, lọc và sắp xếp.

## 6.2. API xác thực và tài khoản

| Method | API dự kiến | Chức năng |
|---|---|---|
| POST | `/api/auth/login` | Đăng nhập Admin/nhân viên |
| POST | `/api/auth/logout` | Kết thúc phiên đăng nhập |
| GET | `/api/auth/me` | Lấy thông tin tài khoản hiện tại |
| GET | `/api/admin/users` | Xem danh sách tài khoản |
| POST | `/api/admin/users` | Tạo tài khoản nhân viên |
| PATCH | `/api/admin/users/{id}/role` | Cập nhật vai trò hoặc quyền |

## 6.3. API sinh viên và phân phòng

| Method | API dự kiến | Chức năng |
|---|---|---|
| GET | `/api/students` | Tìm kiếm và liệt kê sinh viên |
| POST | `/api/students` | Tạo hồ sơ sinh viên |
| GET | `/api/students/{id}` | Xem hồ sơ và thông tin liên quan |
| PUT | `/api/students/{id}` | Cập nhật hồ sơ |
| GET | `/api/rooms` | Liệt kê phòng và tình trạng sức chứa |
| POST | `/api/room-assignments` | Phân phòng cho sinh viên |
| PATCH | `/api/room-assignments/{id}/end` | Ghi nhận ngày rời phòng |
| GET | `/api/students/{id}/room-history` | Xem lịch sử phân phòng |

## 6.4. API khách thăm

| Method | API dự kiến | Chức năng |
|---|---|---|
| GET | `/api/visitors` | Tìm kiếm hồ sơ khách |
| POST | `/api/visitors` | Tạo hồ sơ khách |
| POST | `/api/visits` | Ghi nhận lượt khách đến thăm |
| PATCH | `/api/visits/{id}/departure` | Ghi nhận thời gian khách rời đi |
| GET | `/api/reports/visits` | Báo cáo lượt thăm theo tuần/tháng |

## 6.5. API dịch vụ

| Method | API dự kiến | Chức năng |
|---|---|---|
| GET | `/api/services` | Liệt kê danh mục dịch vụ |
| POST | `/api/services` | Thêm dịch vụ |
| PUT | `/api/services/{id}` | Cập nhật dịch vụ và đơn giá |
| POST | `/api/service-usages` | Ghi nhận lần sử dụng dịch vụ |
| GET | `/api/reports/service-usage` | Tổng hợp tiền theo sinh viên, dịch vụ và khoảng ngày |
| GET | `/api/reports/service-revenue` | Báo cáo doanh thu từng dịch vụ theo tháng |

## 6.6. API xe tháng và lượt gửi/lấy

| Method | API dự kiến | Chức năng |
|---|---|---|
| GET | `/api/vehicles` | Tra cứu xe đã đăng ký vé tháng |
| POST | `/api/monthly-vehicle-registrations` | Đăng ký xe vé tháng; kiểm tra giới hạn |
| GET | `/api/monthly-vehicle-registrations` | Tra cứu đăng ký theo sinh viên/tháng |
| POST | `/api/monthly-vehicle-registrations/{id}/events` | Ghi nhận lượt gửi hoặc lấy xe |

## 6.7. API hóa đơn và báo cáo

| Method | API dự kiến | Chức năng |
|---|---|---|
| POST | `/api/invoices/generate` | Tổng hợp và tạo hóa đơn theo tháng/năm |
| GET | `/api/invoices` | Liệt kê hóa đơn, lọc theo tháng và trạng thái |
| GET | `/api/invoices/{id}` | Xem chi tiết hóa đơn |
| PATCH | `/api/invoices/{id}/status` | Cập nhật trạng thái thanh toán |
| GET | `/api/reports/monthly-student-costs` | Sinh viên đang ở KTX và tổng tiền tháng, sắp xếp theo họ tên |
| GET | `/api/reports/room-capacity` | Kiểm tra số người ở và sức chứa phòng |

## 6.8. Yêu cầu dữ liệu truy vấn

1. Liệt kê thông tin sinh viên đang ở KTX cùng tổng tiền phải trả trong
   tháng, bao gồm tiền phòng, dịch vụ, vé tháng và phí gửi/lấy xe. Danh
   sách được sắp xếp theo họ tên sinh viên.
2. Liệt kê sinh viên, tên dịch vụ và tổng tiền mỗi sinh viên sử dụng cho
   từng dịch vụ trong khoảng từ ngày bắt đầu đến ngày kết thúc.
3. Liệt kê sinh viên, khách đến thăm và số lần khách đến theo tuần hoặc
   tháng.
4. Liệt kê danh mục dịch vụ và doanh thu của từng dịch vụ trong mỗi
   tháng.
5. Kiểm tra ràng buộc số người ở trong phòng không vượt sức chứa và
   mỗi sinh viên không đăng ký quá 2 xe vé tháng trong cùng tháng/năm.

# 7. YÊU CẦU PHI CHỨC NĂNG

## 7.1. Bảo mật

- Người dùng phải đăng nhập trước khi truy cập chức năng quản trị.
- Backend phải kiểm tra quyền trên từng thao tác; không chỉ ẩn chức năng
  trên giao diện.
- Mật khẩu không được lưu dưới dạng văn bản thuần và không được trả về
  trong API response.
- Dữ liệu đầu vào phải được xác thực; truy vấn cơ sở dữ liệu phải tránh
  SQL injection.
- Thông tin kết nối CSDL và khóa bí mật không được đưa vào mã nguồn công
  khai hoặc API response.

## 7.2. Hiệu năng và khả năng sử dụng

- Các thao tác thông thường nên phản hồi trong 3 giây ở điều kiện tải
  bình thường.
- Danh sách lớn cần hỗ trợ phân trang, lọc và tìm kiếm phù hợp.
- Báo cáo cần cho phép chọn tháng hoặc khoảng thời gian cần tra cứu.
- Giao diện cần hiển thị thông báo rõ ràng khi thao tác thành công hoặc
  khi dữ liệu không hợp lệ.

## 7.3. Tính toàn vẹn dữ liệu

- Khóa chính và khóa ngoại phải đảm bảo dữ liệu tham chiếu hợp lệ.
- Không để phân phòng vượt sức chứa hoặc tạo lượt ở trùng thời gian.
- Không để một sinh viên đăng ký quá 2 xe vé tháng trong một tháng.
- Việc tính lượt miễn phí và phí phát sinh phải nhất quán khi có nhiều
  thao tác đồng thời.
- Tiền hóa đơn phải bằng tổng các khoản thành phần; mỗi sinh viên chỉ
  có một hóa đơn trong một tháng/năm.
- Thao tác tổng hợp hóa đơn và các nghiệp vụ cần nhiều bước phải dùng
  transaction để tránh lưu dữ liệu dở dang.

## 7.4. Khả năng bảo trì

Backend cần tổ chức tách biệt phần tiếp nhận yêu cầu, xác thực dữ liệu,
xử lý nghiệp vụ và truy cập dữ liệu. Quy tắc tính tiền và kiểm tra giới
hạn cần được tập trung, có thể kiểm thử và không lặp lại không cần thiết
giữa các API.

## 7.5. Khả năng mở rộng

Thiết kế cần cho phép mở rộng thêm loại báo cáo, dịch vụ, trạng thái
thanh toán và quy tắc quản lý ký túc xá mà không làm mất dữ liệu lịch sử.
Các chức năng không thuộc phạm vi hiện tại chỉ được bổ sung khi có yêu
cầu và quy tắc nghiệp vụ được xác nhận.

# 8. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 8.1. Kết luận

Hệ thống quản lý ký túc xá sinh viên tập trung các nghiệp vụ quản lý
sinh viên, phòng, khách thăm, dịch vụ, xe tháng, hóa đơn và báo cáo.
Các quy tắc về sức chứa, chi phí hàng tháng và lượt gửi/lấy xe là cơ sở
để Backend và Database đảm bảo dữ liệu chính xác, nhất quán.

Hệ thống được định hướng triển khai theo mô hình:

React + Vite

↓

Django REST Framework

↓

MySQL

## 8.2. Phạm vi và hạn chế

Phiên bản yêu cầu hiện tại tập trung vào quản lý nghiệp vụ nội trú và
tổng hợp chi phí. Các lượt gửi/lấy của xe không đăng ký vé tháng không
được lưu trong CSDL. Tài khoản dành cho sinh viên, cổng thanh toán trực
tuyến và ứng dụng di động không nằm trong phạm vi đã xác định.

Các chi tiết vận hành chưa được quy định trong yêu cầu gốc, chẳng hạn
phương thức thanh toán thực tế hoặc quy trình xử lý khi chuyển phòng
nhiều lần trong cùng tháng, cần được thống nhất trước khi triển khai
nghiệp vụ tương ứng.

## 8.3. Hướng phát triển

Trong các phiên bản tiếp theo có thể xem xét:

- Bổ sung cổng thông tin để sinh viên tự tra cứu hóa đơn và dịch vụ.
- Tích hợp thanh toán điện tử nếu có yêu cầu.
- Bổ sung xuất báo cáo ra Excel/PDF.
- Mở rộng thống kê công suất phòng và doanh thu theo nhiều kỳ.
- Bổ sung thông báo tự động về hóa đơn hoặc các khoản chưa thanh toán.
