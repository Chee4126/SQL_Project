# ĐẶC TẢ YÊU CẦU PHẦN MỀM (SRS)
# HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ SINH VIÊN

**Phiên bản:** 2.3 · **Ngày cập nhật:** 13/11/2026
**Công nghệ:** React + Vite, Python, Django REST Framework, SQLite (mặc định) hoặc MySQL

# 1. TỔNG QUAN HỆ THỐNG

## 1.1. Giới thiệu

Hệ thống quản lý ký túc xá sinh viên được xây dựng để hỗ trợ ban quản lý
theo dõi sinh viên đang ở, phòng ở, khách đến thăm, dịch vụ sử dụng, xe
đăng ký vé tháng, lượt gửi/lấy xe và hóa đơn hàng tháng.

Hệ thống giúp tập trung dữ liệu, hỗ trợ thực hiện các quy tắc nghiệp vụ
về sức chứa phòng, chi phí dịch vụ, vé xe tháng và cung cấp các báo cáo
phục vụ công tác quản lý.

Nhân viên có thể tự đăng ký bằng họ tên, email, số điện
thoại và mật khẩu.

Frontend và Backend được xây dựng tách biệt. Frontend cung cấp giao diện
cho nhân viên; Backend tiếp nhận yêu cầu, kiểm tra quy tắc nghiệp vụ
và làm việc với cơ sở dữ liệu. Các chức năng tài khoản gồm đăng ký,
đăng nhập bằng email, quản lý hồ sơ cá nhân và danh sách tài khoản Staff.

## 1.2. Mục tiêu của hệ thống

Hệ thống hướng tới các mục tiêu:

- Quản lý hồ sơ sinh viên và lịch sử ở phòng.
- Quản lý phòng, đơn giá và sức chứa.
- Theo dõi khách đến thăm sinh viên theo thời gian.
- Quản lý danh mục dịch vụ và các lần sinh viên sử dụng dịch vụ.
- Quản lý đăng ký vé xe tháng và ghi nhận lượt gửi/lấy xe.
- Tổng hợp chi phí hàng tháng, lập hóa đơn và theo dõi trạng thái thanh toán.
- Đăng ký tài khoản Staff, đăng nhập bằng email và quản lý hồ sơ tài khoản.
- Cung cấp truy vấn, báo cáo về sinh viên, doanh thu, khách thăm và
  tình trạng phòng.
- Đảm bảo các ràng buộc nghiệp vụ được kiểm tra nhất quán ở Backend và
  Database.

## 1.3. Đối tượng sử dụng

### Nhân viên (vai trò `STAFF`)

Mọi tài khoản nhân viên đều có cùng vai trò `STAFF`, đăng nhập bằng email
và có thể thực hiện các nghiệp vụ quản lý gồm:

- Cập nhật hồ sơ sinh viên và tình trạng ở.
- Ghi nhận khách đến thăm và thời gian đến/rời đi.
- Quản lý danh mục dịch vụ và ghi nhận sử dụng dịch vụ.
- Ghi nhận đăng ký vé tháng và các lượt gửi/lấy xe thuộc diện lưu trữ.
- Tra cứu hóa đơn, tình trạng phòng và các báo cáo.
- Xem danh sách và tạo tài khoản Staff khác; không thể gán vai trò khác.
- Cập nhật hồ sơ cá nhân và đổi mật khẩu.

### Sinh viên và khách

Sinh viên là đối tượng được quản lý về hồ sơ, chỗ ở, dịch vụ, xe tháng,
khách thăm và công nợ. Khách là đối tượng được ghi nhận khi đến thăm
sinh viên. Hai nhóm này không có tài khoản truy cập riêng theo phạm vi
hiện tại; tài khoản Staff dùng cho người vận hành hệ thống.

## 1.4. Công nghệ và công cụ sử dụng

| Công nghệ/Công cụ | Mục đích |
|---|---|
| React | Xây dựng giao diện Frontend |
| Vite | Phục vụ phát triển và đóng gói Frontend |
| JavaScript | Phát triển Frontend |
| Python | Ngôn ngữ lập trình Backend |
| Django | Xây dựng nền tảng Backend |
| Django REST Framework | Xây dựng REST API |
| SQLite / MySQL | Lưu trữ dữ liệu; SQLite được cấu hình mặc định, có thể cấu hình MySQL qua môi trường |
| npm | Quản lý thư viện Frontend |
| pip / `requirements.txt` | Quản lý thư viện Backend |
| VS Code | Môi trường phát triển |
| Postman | Kiểm thử API |
| Git | Quản lý mã nguồn |

## 1.5. Các quy tắc nghiệp vụ chính

- Mã sinh viên định danh duy nhất cho mỗi sinh viên.
- Email tài khoản là duy nhất và được dùng để đăng nhập; tên đăng nhập
  được tạo từ phần trước ký tự `@`, thêm số nếu bị trùng, và không tự đổi
  khi email được cập nhật.
- Mọi tài khoản được tạo qua đăng ký hoặc chức năng quản lý tài khoản đều
  có vai trò `STAFF`; hệ thống không hỗ trợ cấp hoặc đổi vai trò.
- Email, họ tên và số điện thoại phải hợp lệ; mật khẩu được lưu dạng băm,
  có độ dài tối thiểu 6 ký tự.
- Đổi mật khẩu yêu cầu mật khẩu hiện tại và xác nhận mật khẩu mới; token
  đăng nhập cũ bị thu hồi và token mới được cấp sau khi đổi thành công.
- Người dùng chỉ được chỉnh sửa hồ sơ của chính mình; không thể tự sửa
  tên đăng nhập hoặc vai trò từ chức năng hồ sơ.
- Mỗi phòng lưu đơn giá tháng và sức chứa tối đa trực tiếp trên hồ sơ.
- Không được phân phòng làm số người ở vượt quá sức chứa; một sinh viên
  không được ở đồng thời tại nhiều phòng.
- Nếu sinh viên ở phòng ít nhất một ngày trong tháng thì tiền phòng
  được tính trọn tháng theo đơn giá phòng.
- Một sinh viên có thể sử dụng một dịch vụ nhiều lần; tiền dịch vụ được
  cộng dồn theo tháng và theo giá tại thời điểm sử dụng.
- Một sinh viên được đăng ký tối đa 2 xe vé tháng trong một tháng. Giá
  vé là 100.000 đồng/xe/tháng.
- Chỉ lưu xe và lịch sử lượt gửi/lấy của xe đăng ký vé tháng. Thời điểm
  một lượt phải thuộc kỳ đăng ký; lượt gửi/lấy không phát sinh phí.
- Mỗi sinh viên có tối đa một hóa đơn trong một tháng/năm. Hóa đơn gồm
  tiền phòng, dịch vụ và vé tháng.
- Các thay đổi có ảnh hưởng tới sức chứa phòng và số xe đăng ký phải
  được kiểm tra nhất quán ở Backend; không chỉ dựa vào giao diện.

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
Khoảng thời gian một lượt ở được tính từ ngày vào (bao gồm) đến ngày rời
phòng (không bao gồm); khi ghi nhận rời phòng, sức chứa của phòng giảm
ngay trong ngày đó.

Phòng được quản lý theo số phòng, tên, tầng, đơn giá tháng và sức chứa
tối đa; không phân loại phòng. Khi phân phòng, hệ thống phải xác định số
người đang ở trong khoảng thời gian tương ứng và từ chối thao tác nếu
vượt sức chứa hoặc sinh viên đang có một lượt phân phòng còn hiệu lực.
Hệ thống chỉ hỗ trợ hai mức cấu hình phòng: **1.800.000 đồng/tháng với
sức chứa 4 người** và **250.000 đồng/tháng với sức chứa 8 người**. Nhân
viên chọn một trong hai mức khi tạo phòng; không nhập riêng đơn giá và
sức chứa.

Tiền phòng được tính trọn tháng nếu sinh viên ở phòng ít nhất một ngày
trong tháng. Lịch sử phân phòng phải được giữ lại sau khi sinh viên
chuyển phòng hoặc rời ký túc xá.

Nhân viên có thể xóa hồ sơ sinh viên hoặc phòng chưa được dùng trong bất
kỳ giao dịch nào. Nếu hồ sơ sinh viên đã có hóa đơn, lượt sử dụng dịch vụ,
lượt thăm, đăng ký xe hoặc lịch sử phân phòng, hoặc phòng đã có lịch sử
phân phòng, hệ thống từ chối xóa và thông báo nguyên nhân. Không xóa hay
thay đổi dữ liệu lịch sử để thực hiện thao tác này.

## 2.3. Nghiệp vụ khách thăm

Hệ thống lưu hồ sơ khách gồm họ tên, số CMT/CCCD và ngày sinh. Khi ghi
nhận lượt thăm, nhân viên nhập trực tiếp thông tin khách, sinh viên được
thăm và thời gian đến; thời gian rời đi được ghi nhận sau hoặc mặc định
là thời điểm hiện tại. Nếu có số CMT/CCCD, hồ sơ được tái sử dụng khi
số giấy tờ và họ tên khớp. Nếu không có số giấy tờ, hệ thống đối chiếu
họ tên và ngày sinh (nếu được nhập); khi có nhiều hồ sơ trùng tên/ngày
sinh, nhân viên phải nhập CMT/CCCD để tránh gộp nhầm. Hồ sơ chưa có thì
được tạo cùng lượt thăm. Một khách không thể có đồng thời nhiều lượt
thăm chưa ghi nhận rời đi.

Dữ liệu khách chỉ được tạo hoặc tái sử dụng khi ghi nhận lượt thăm; không
có API hoặc giao diện quản lý danh mục khách riêng. Lịch sử lượt thăm
được dùng để tra cứu và thống kê số lần thăm theo tuần hoặc tháng.

## 2.4. Nghiệp vụ dịch vụ

Hệ thống quản lý danh mục dịch vụ, đơn giá và đơn vị tính. Các dịch vụ
có thể gồm giặt là, nước uống hoặc các dịch vụ khác của ký túc xá.

Mỗi lần sử dụng dịch vụ được ghi nhận riêng, gồm sinh viên, dịch vụ,
thời gian sử dụng, số lượng và đơn giá áp dụng. Một sinh viên có thể sử
dụng cùng dịch vụ nhiều lần. Chi phí dịch vụ trong tháng được tính bằng
tổng số lượng nhân với đơn giá áp dụng của từng lần sử dụng trong tháng.

Đơn giá áp dụng được lưu cùng giao dịch để các lần sử dụng trước đó
không bị thay đổi khi giá trong danh mục được cập nhật.
Dịch vụ chỉ được xóa khi chưa có lượt sử dụng; các lượt sử dụng và đơn
giá lịch sử phải được giữ nguyên. Chi phí không được cộng ngay vào hóa
đơn khi ghi nhận sử dụng; được tổng hợp khi lập hóa đơn hoặc xem báo cáo.

## 2.5. Nghiệp vụ gửi/lấy xe

Sinh viên có thể đăng ký tối đa 2 xe vé tháng trong một tháng. Mỗi đăng
ký gồm xe, sinh viên, tháng/năm áp dụng và đơn giá vé tháng là 100.000
đồng.

Với xe có vé tháng, hệ thống lưu từng lượt gửi hoặc lấy trong đúng tháng
đăng ký. Ghi nhận lượt xe chỉ lưu loại lượt và thời điểm, không tính phí
và không làm thay đổi hóa đơn.

Xe không có vé tháng và các lượt tương ứng không được lưu trong cơ sở
dữ liệu.
Xe vé tháng gắn với đăng ký và lịch sử lượt xe; hệ thống không xóa xe,
đăng ký vé tháng hoặc lượt gửi/lấy thông qua chức năng xóa danh mục.

## 2.6. Nghiệp vụ hóa đơn và báo cáo

Hệ thống có hai chức năng riêng: lập hóa đơn theo từng sinh viên và báo
cáo chi phí tháng cho sinh viên có lượt phân phòng giao với tháng được chọn.

Khi lập hóa đơn, Staff chọn sinh viên, tháng/năm và nhập tiền phòng.
Backend tổng hợp tiền dịch vụ từ các lần sử dụng và tiền vé tháng từ các
đăng ký. Lượt gửi/lấy xe không phát sinh phí. Nếu chưa thanh toán, hóa
đơn có thể lập lại để cập nhật dịch vụ/vé xe; nếu tiền phòng không được
nhập lại thì giữ nguyên giá trị đã nhập. Hóa đơn đã thanh toán không thể
lập lại.

Mỗi sinh viên có tối đa một hóa đơn trong một tháng/năm. Hóa đơn lưu
tiền phòng, tiền dịch vụ, tiền vé xe tháng, khoản phí gửi xe bằng 0 cho
hóa đơn mới, tổng tiền và trạng thái thanh toán. Báo cáo chi phí tháng
được tổng hợp trực tiếp từ lượt phân phòng, sử dụng dịch vụ và đăng ký
vé tháng; không yêu cầu hóa đơn đã được lập. Báo cáo chỉ liệt kê sinh
viên có lượt phân phòng giao với tháng được chọn; tiền phòng tính trọn
tháng theo đơn giá phòng nếu ở ít nhất một ngày. Nếu sinh viên chuyển
phòng trong tháng, báo cáo cộng tiền tháng của từng lượt phân phòng giao
với kỳ theo đơn giá của phòng tương ứng. Có thể chọn tháng/năm, xem danh
sách theo tên và in toàn danh sách.

Các báo cáo cần hỗ trợ tra cứu theo tháng, khoảng ngày hoặc tuần/tháng
tùy nghiệp vụ; chi tiết được mô tả tại Mục 4 và Mục 6.

## 2.7. Nghiệp vụ tài khoản và hồ sơ

Người chưa có tài khoản có thể đăng ký công khai với vai trò `STAFF` bằng
họ tên, email, số điện thoại, mật khẩu và xác nhận mật khẩu. Email phải
hợp lệ và duy nhất không phân biệt chữ hoa/chữ thường; số điện thoại
phải có từ 7 đến 15
chữ số (có thể kèm dấu `+`, khoảng trắng hoặc dấu phân cách). Mật khẩu
có tối thiểu 6 ký tự. Đăng ký thành công tạo tài khoản vai trò `STAFF` và
trả token để đăng nhập ngay. Dữ liệu gửi lên không thể thay đổi vai trò.

Tên đăng nhập nội bộ được sinh từ phần trước `@` trong email. Nếu tên
đã tồn tại thì hệ thống nối số thứ tự để tạo tên duy nhất. Tên đăng nhập
được hiển thị trong giao diện và không tự thay đổi khi email được cập
nhật. Việc xác thực luôn dùng email và mật khẩu, không dùng tên đăng
nhập.

Nhân viên đăng nhập bằng email và mật khẩu. Email được so sánh không
phân biệt chữ hoa/chữ thường. Khi đăng nhập thành công, hệ thống trả
token xác thực và thông tin tài khoản;
mật khẩu không được trả về.

Người dùng đã đăng nhập có thể xem và cập nhật họ tên, email, số điện
thoại của chính mình. Email mới phải hợp lệ và chưa được tài khoản khác
sử dụng. Tên đăng nhập và vai trò `STAFF` không thể sửa từ hồ sơ cá nhân.

Người dùng có thể đổi mật khẩu trong hồ sơ bằng cách nhập mật khẩu hiện
tại, mật khẩu mới và xác nhận mật khẩu mới. Backend xác minh mật khẩu
hiện tại, yêu cầu mật khẩu mới tối thiểu 6 ký tự và hai giá trị xác nhận
phải khớp. Khi đổi thành công, các token cũ của tài khoản bị thu hồi và
token mới được cấp để tiếp tục phiên hiện tại.

Mọi tài khoản Staff đã đăng nhập có thể xem danh sách và tạo tài khoản
Staff. Có thể xóa tài khoản Staff khác nhưng không thể xóa tài khoản đang
đăng nhập. Hệ thống không có thao tác phân quyền hay đổi vai trò.

Các danh mục chỉ được xóa cứng khi không có dữ liệu lịch sử tham chiếu.
Thao tác xóa bị từ chối kèm lý do nếu dữ liệu đã được sử dụng; không xóa
giao dịch, hóa đơn hay lịch sử để cho phép xóa danh mục.

# 3. PHÂN TÍCH CHỨC NĂNG

## 3.1. Chức năng dành cho Staff

| STT | Chức năng | Nội dung |
|---|---|---|
| 1 | Đăng ký và đăng nhập | Nhân viên đăng ký bằng họ tên, email, số điện thoại, mật khẩu; mọi tài khoản đăng nhập bằng email và mật khẩu với vai trò `STAFF`. |
| 2 | Quản lý sinh viên | Xem, tìm kiếm, thêm, cập nhật và xóa hồ sơ chưa có dữ liệu nghiệp vụ tham chiếu. |
| 3 | Quản lý phòng và phân phòng | Tạo/xem/xóa phòng; phân phòng, ghi nhận rời phòng, xem người đang ở và kiểm tra sức chứa theo ngày. |
| 4 | Ghi nhận lượt thăm | Nhập thông tin khách trực tiếp, ghi nhận đến/rời đi, xem lịch sử và thống kê khách theo tuần/tháng; không có danh mục khách riêng. |
| 5 | Quản lý dịch vụ | Thêm, xem, sửa, xóa dịch vụ chưa được sử dụng; ghi nhận sử dụng và xem báo cáo sử dụng/doanh thu. |
| 6 | Quản lý xe tháng | Đăng ký tối đa 2 xe mỗi sinh viên trong tháng, ghi nhận lượt gửi/lấy xe trong kỳ; không xóa xe/đăng ký/lịch sử. |
| 7 | Hóa đơn và báo cáo | Lập/cập nhật hóa đơn chưa thanh toán, đổi trạng thái thanh toán; xem chi phí tháng, dịch vụ, doanh thu, giới hạn xe và sức chứa phòng. |
| 8 | Hồ sơ tài khoản | Người dùng cập nhật họ tên, email, số điện thoại và đổi mật khẩu của chính mình. |
| 9 | Quản lý tài khoản | Staff đã đăng nhập tạo, xem và xóa tài khoản Staff khác; không thể xóa tài khoản đang đăng nhập hoặc đổi vai trò. |

## 3.2. Vai trò tài khoản

Hệ thống chỉ có vai trò `STAFF`. Mọi nhân viên đã đăng nhập có cùng quyền
truy cập các chức năng nghiệp vụ và quản lý tài khoản; không có phân cấp
vai trò. Chỉ đăng ký và đăng nhập được công khai; các API còn lại yêu
cầu tài khoản đã xác thực.

## 3.3. Trạng thái nghiệp vụ

### Tình trạng phân phòng

- **Đang ở:** ngày rời phòng chưa được ghi nhận.
- **Đã kết thúc:** ngày rời phòng đã được ghi nhận.

### Trạng thái hóa đơn

- **Chưa thanh toán**
- **Đã thanh toán**

### Trạng thái lượt gửi/lấy xe

Mỗi bản ghi là một sự kiện thuộc một trong hai loại, trong kỳ đăng ký và
không phát sinh phí:

- **Gửi xe**
- **Lấy xe**

# 4. THIẾT KẾ KIẾN TRÚC VÀ LUỒNG HỆ THỐNG

## 4.1. Kiến trúc tổng thể

Hệ thống được thiết kế theo mô hình Frontend – Backend – Database:

Frontend: React + Vite

↓ HTTP/JSON

Backend: Django REST Framework

↓ ORM / truy vấn dữ liệu

Database: SQLite (mặc định) hoặc MySQL theo cấu hình môi trường

Frontend gửi yêu cầu qua REST API. Backend xác thực, kiểm tra dữ liệu,
xử lý quy tắc nghiệp vụ và trả kết quả cho Frontend.

## 4.2. Các thành phần trong Backend

- **View / ViewSet:** tiếp nhận yêu cầu HTTP, kiểm tra quyền truy cập và
  trả phản hồi.
- **Serializer:** kiểm tra dữ liệu đầu vào và định dạng dữ liệu trả về.
- **Service:** xử lý quy tắc nghiệp vụ như phân phòng, tính tiền và lập
  hóa đơn.
- **Model:** biểu diễn dữ liệu và quan hệ được lưu trong cơ sở dữ liệu
  đang cấu hình (SQLite mặc định hoặc MySQL) thông qua Django ORM.
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

SQLite hoặc MySQL

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

Đưa giao dịch vào dữ liệu để tổng hợp khi lập hóa đơn hoặc xem báo cáo

## 4.6. Luồng ghi nhận lượt gửi/lấy xe

Nhân viên chọn đăng ký vé tháng và loại lượt

↓

Backend kiểm tra thời điểm thuộc tháng đăng ký

↓

Lưu lượt gửi/lấy; không tính hoặc cộng phí vào hóa đơn

## 4.7. Luồng lập hóa đơn tháng

Chọn một sinh viên và tháng/năm cần lập hóa đơn

↓

Nhập tiền phòng (bắt buộc khi lập hóa đơn lần đầu)

↓

Backend cộng tiền dịch vụ và vé tháng từ dữ liệu của kỳ

↓

Kiểm tra hóa đơn của sinh viên trong kỳ đã tồn tại và trạng thái thanh toán

↓

Tạo mới hoặc cập nhật hóa đơn chưa thanh toán; không lập lại hóa đơn đã thanh toán

↓

Trả hóa đơn; danh sách hóa đơn được tra cứu riêng theo tháng, năm, sinh viên hoặc trạng thái

## 4.8. Luồng đăng ký, đăng nhập và cập nhật hồ sơ

Nhân viên nhập họ tên, email, số điện thoại, mật khẩu và xác nhận mật khẩu
trên trang đăng ký

↓

Backend xác thực email, số điện thoại, mật khẩu và kiểm tra email chưa
được tài khoản khác sử dụng

↓

Tạo tài khoản `STAFF`, hồ sơ số điện thoại và token đăng nhập

↓

Staff đăng nhập bằng email và mật khẩu; backend trả thông tin tài khoản
và token

↓

Người dùng đã đăng nhập mở Hồ sơ tài khoản để cập nhật thông tin hoặc
đổi mật khẩu

↓

Nếu đổi mật khẩu, backend xác minh mật khẩu hiện tại, thu hồi token cũ,
cấp token mới và trả hồ sơ cập nhật

# 5. THIẾT KẾ CƠ SỞ DỮ LIỆU

## 5.1. Mục đích

SQLite mặc định (hoặc MySQL nếu cấu hình môi trường) lưu tài khoản, hồ sơ
và các giao dịch của ký túc xá. Các nhóm
dữ liệu chính gồm:

- Tài khoản Staff và hồ sơ liên hệ (số điện thoại).
- Sinh viên.
- Phòng và lịch sử phân phòng.
- Khách và lượt thăm.
- Dịch vụ và các lần sử dụng dịch vụ.
- Xe, đăng ký vé tháng và lượt gửi/lấy xe.
- Hóa đơn tháng.

## 5.2. Quy ước thiết kế

- `PK`: khóa chính; `FK`: khóa ngoại; `UQ`: duy nhất; `NN`: không NULL.
- Các trường tiền sử dụng `DECIMAL(12,2)` và được tính bằng đồng Việt Nam.
- Email tài khoản được chuẩn hóa chữ thường khi ghi và duy nhất không
  phân biệt chữ hoa/chữ thường.
- Mật khẩu chỉ lưu dưới dạng giá trị băm do Django quản lý; không lưu
  hoặc trả về mật khẩu thuần.
- Mã tự tăng sử dụng kiểu số nguyên tự tăng do Django ánh xạ sang hệ quản
  trị cơ sở dữ liệu đang cấu hình.
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

## 5.4. Bảng PHONG

Bảng lưu danh mục phòng cùng đơn giá và sức chứa được cấu hình riêng
trên từng phòng theo một trong hai cặp hợp lệ: 1.800.000 đồng/4 người
hoặc 250.000 đồng/8 người.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaPhong | Mã/số phòng | VARCHAR(15) | PK |
| TenPhong | Tên hiển thị của phòng | VARCHAR(30) | NN |
| Tang | Tầng | INT |  |
| DonGia | Đơn giá phòng theo tháng | DECIMAL(12,2) | NN, không âm |
| SoNguoiToiDa | Sức chứa tối đa | INT | NN, lớn hơn 0 |

Ràng buộc cấu hình: cặp `(DonGia, SoNguoiToiDa)` chỉ được là
`(1800000, 4)` hoặc `(250000, 8)`.

## 5.5. Bảng PHANPHONG

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

## 5.6. Bảng KHACH

Bảng lưu thông tin khách đến thăm.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaKhach | Mã khách | INT | PK, AUTO_INCREMENT |
| HoTen | Họ tên khách | VARCHAR(100) | NN |
| SoCMT | Số CMT/CCCD | VARCHAR(20) | UQ |
| NgaySinh | Ngày sinh | DATE |  |

## 5.7. Bảng LUOTTHAM

Bảng lưu từng lượt khách đến thăm sinh viên.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaLuotTham | Mã lượt thăm | INT | PK, AUTO_INCREMENT |
| MaKhach | Khách | INT | FK → KHACH.MaKhach |
| MaSV | Sinh viên được thăm | VARCHAR(15) | FK → SINHVIEN.MaSV |
| NgayDen | Thời gian đến | DATETIME | NN |
| NgayDi | Thời gian rời đi | DATETIME | NULL |

## 5.8. Bảng DICHVU

Bảng lưu danh mục dịch vụ.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaDV | Mã dịch vụ | INT | PK, AUTO_INCREMENT |
| TenDV | Tên dịch vụ | VARCHAR(100) | NN |
| DonGia | Đơn giá hiện tại | DECIMAL(12,2) | NN, không âm |
| DonViTinh | Đơn vị tính | VARCHAR(30) |  |

## 5.9. Bảng SUDUNGDICHVU

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

## 5.10. Bảng XE

Bảng chỉ lưu thông tin xe đăng ký vé tháng.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| BienSo | Biển số xe | VARCHAR(20) | PK |
| LoaiXe | Loại xe | VARCHAR(50) | NN |

## 5.11. Bảng DANGKYVEXE

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

## 5.12. Bảng LUOTGUIXE

Bảng chỉ lưu sự kiện gửi/lấy của xe đã đăng ký vé tháng.

| Trường | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|
| MaLuot | Mã lượt xe | INT | PK, AUTO_INCREMENT |
| MaDangKy | Đăng ký vé tháng | INT | FK → DANGKYVEXE.MaDangKy |
| ThoiGian | Thời điểm gửi/lấy | DATETIME | NN |
| LoaiLuot | Loại sự kiện | ENUM('GUI','LAY') | NN |
| MienPhi | Trường tương thích dữ liệu cũ; không dùng cho lượt mới | BOOLEAN | NULL |
| TienPhat | Trường tương thích dữ liệu cũ; không dùng cho lượt mới | DECIMAL(12,2) | NULL |

Lượt mới chỉ lưu thời điểm và loại lượt, không áp dụng miễn phí hay thu
phí. Hai cột phí cũ được giữ nullable để bảo toàn bản ghi lịch sử từ
phiên bản trước; giá trị cũ không được cộng vào hóa đơn mới.

## 5.13. Bảng HOADON

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
| PhiGuiXe | Phí gửi/lấy đã chốt trong hóa đơn cũ | DECIMAL(12,2) | NN, không âm; hóa đơn mới là 0 |
| TongTien | Tổng tiền phải trả | DECIMAL(12,2) | NN, không âm |
| TrangThai | Trạng thái thanh toán | ENUM('CHUA_THANH_TOAN','DA_THANH_TOAN') | NN |

Ràng buộc: `UNIQUE (MaSV, Thang, Nam)`.

`TongTien` bằng tổng `TienPhong`, `TienDichVu`, `TienXe` và
`PhiGuiXe`. Hóa đơn mới không tính phí lượt gửi/lấy; giá trị trong hóa
đơn cũ được giữ nguyên như lịch sử. Khi lập hóa đơn, tiền phòng do Staff
nhập (bắt buộc khi tạo mới); Backend tự tổng hợp dịch vụ và vé xe.
Riêng báo cáo chi phí tháng tính tiền phòng trọn tháng theo từng lượt
phân phòng giao với tháng nếu sinh viên ở ít nhất một ngày.

## 5.14. Ràng buộc toàn vẹn dữ liệu

| Ràng buộc | Ý nghĩa |
|---|---|
| Khóa chính trên mỗi bảng | Không cho phép bản ghi trùng định danh. |
| Khóa ngoại | Không cho phép giao dịch tham chiếu sinh viên, phòng, dịch vụ, khách hoặc đăng ký xe không tồn tại. |
| Tài khoản | Email hợp lệ và duy nhất không phân biệt hoa/thường; tài khoản đăng ký công khai luôn có vai trò `STAFF`. |
| Hồ sơ tài khoản | Người dùng chỉ sửa hồ sơ của mình; tên đăng nhập và vai trò `STAFF` không thể đổi qua hồ sơ cá nhân. |
| Tham chiếu sinh viên | Phân phòng, khách thăm, sử dụng dịch vụ, đăng ký xe và lập hóa đơn phải chọn sinh viên đã có trong danh sách hồ sơ; hệ thống lưu mã sinh viên làm khóa liên kết. |
| Mật khẩu | Mật khẩu được băm; đổi mật khẩu yêu cầu xác minh mật khẩu hiện tại và xác nhận mật khẩu mới. |
| Sức chứa phòng | Mỗi lượt phân phòng làm tăng số người ở của phòng tại khoảng thời gian tương ứng; không cho phép vượt sức chứa. Phòng đủ chỗ bị loại khỏi lựa chọn phân phòng. |
| Thời gian phân phòng | Ngày kết thúc không được trước ngày bắt đầu; sinh viên không có hai lượt ở trùng thời gian. |
| Số lượng dịch vụ | `SoLuong` phải lớn hơn 0; đơn giá và các khoản tiền không âm. |
| Giới hạn đăng ký xe | Tối đa 2 xe vé tháng cho mỗi sinh viên trong một tháng/năm. |
| Đăng ký xe duy nhất | Một xe chỉ thuộc một đăng ký trong cùng tháng/năm. |
| Hóa đơn tháng | Mỗi sinh viên chỉ có một hóa đơn trong một tháng/năm; tổng tiền bằng tổng các khoản thành phần. |

Các kiểm tra cần đếm dữ liệu hiện có như sức chứa phòng và số xe đăng ký
phải được bảo vệ bằng transaction phù hợp. Ràng
buộc khóa ngoại, duy nhất và kiểm tra giá trị phải được đặt ở Database
khi hệ quản trị hỗ trợ.

## 5.15. Quan hệ giữa các bảng

| Bảng cha | Quan hệ | Bảng con | Cột tham chiếu |
|---|---|---|---|
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
| TAIKHOAN | 1-1 | HOSOTAIKHOAN | HOSOTAIKHOAN.MaTaiKhoan |

## 5.16. Bảng TAIKHOAN và HOSOTAIKHOAN

Tài khoản xác thực sử dụng bảng User của Django (`auth_user`). Bảng hồ sơ
liên hệ mở rộng thông tin tài khoản; không tạo tài khoản đăng nhập riêng
cho sinh viên hoặc khách trong phạm vi hiện tại.

| Bảng | Trường logic | Ý nghĩa | Kiểu dữ liệu | Ràng buộc |
|---|---|---|---|---|
| TAIKHOAN | MaTaiKhoan | Mã tài khoản | BIGINT | PK |
| TAIKHOAN | TenDangNhap | Tên hiển thị nội bộ, được sinh từ phần trước `@` của email; nối số nếu trùng | VARCHAR(150) | UQ, NN |
| TAIKHOAN | Email | Địa chỉ dùng để đăng nhập và nhận diện tài khoản | VARCHAR(254) | UQ không phân biệt hoa/thường, NN |
| TAIKHOAN | HoTen | Họ tên người dùng | VARCHAR(150) | NN |
| TAIKHOAN | MatKhauBam | Mật khẩu đã băm | VARCHAR(128) trở lên | NN |
| TAIKHOAN | VaiTro | `STAFF` | VARCHAR(20) | NN |
| TAIKHOAN | TrangThai | Tài khoản được phép đăng nhập hay không | BOOLEAN | NN |
| HOSOTAIKHOAN | MaTaiKhoan | Tài khoản sở hữu hồ sơ | BIGINT | PK, FK → TAIKHOAN.MaTaiKhoan, UQ |
| HOSOTAIKHOAN | SoDienThoai | Số điện thoại liên hệ | VARCHAR(20) | NN |

Tên vật lý hiện tại ánh xạ sang `auth_user` và `apps_accounts_userprofile`.
Tên đăng nhập được giữ ổn định khi người dùng đổi email; email mới là
định danh dùng cho các lần đăng nhập tiếp theo. Đăng ký công khai và
chức năng tạo tài khoản đều tạo tài khoản `STAFF`. Mọi tài khoản có cùng
một vai trò; hệ thống không có phân cấp vai trò hoặc chức năng đổi vai
trò.

# 6. API

## 6.1. Khái niệm API

Frontend và Backend trao đổi dữ liệu qua REST API sử dụng HTTP và JSON.
Các API dưới đây mô tả hợp đồng giao tiếp của hệ thống.

| Phương thức | Mục đích |
|---|---|
| GET | Lấy danh sách hoặc chi tiết dữ liệu |
| POST | Tạo dữ liệu hoặc ghi nhận nghiệp vụ |
| PUT/PATCH | Cập nhật dữ liệu |
| DELETE | Xóa dữ liệu khi không làm mất tính toàn vẹn lịch sử |

Các API nghiệp vụ yêu cầu đăng nhập bằng token. Ngoại lệ công khai gồm
đăng ký, đăng nhập và API gốc dùng để kiểm tra trạng thái Backend. API
hồ sơ và quản lý tài khoản yêu cầu token hợp lệ.

## 6.2. API xác thực và tài khoản

| Method | API hiện có | Chức năng |
|---|---|---|
| POST | `/api/auth/register` | Đăng ký tài khoản Staff |
| POST | `/api/auth/login` | Đăng nhập Staff bằng email và mật khẩu |
| POST | `/api/auth/logout` | Kết thúc phiên đăng nhập |
| GET | `/api/auth/me` | Lấy hồ sơ tài khoản hiện tại |
| PATCH | `/api/auth/me` | Cập nhật họ tên/email/số điện thoại; tùy chọn đổi mật khẩu |
| GET | `/api/accounts` | Staff đã đăng nhập xem danh sách tài khoản |
| POST | `/api/accounts` | Staff đã đăng nhập tạo tài khoản Staff |
| DELETE | `/api/accounts/{user_id}` | Xóa tài khoản khác; không cho phép xóa tài khoản đang đăng nhập |

Đăng ký nhận `full_name`, `email`, `phone_number`, `password` và
`password_confirm`; trả mã 201 cùng thông tin tài khoản Staff và token.
Nếu dữ liệu không hợp lệ hoặc email đã được sử dụng, API trả lỗi xác
thực và không tạo tài khoản. Vai trò gửi từ client bị bỏ qua; tài khoản
mới luôn là `STAFF`.

Đăng nhập nhận `email` và `password`; email được so sánh không phân biệt
hoa/thường. Đăng nhập thành công trả token và hồ sơ tài khoản; sai thông
tin trả mã 401.

`PATCH /api/auth/me` cập nhật các trường hồ sơ của người dùng đang đăng
nhập. Khi đổi mật khẩu, request phải có `current_password`,
`new_password` và `password_confirm`; mật khẩu hiện tại phải đúng và hai
mật khẩu mới phải khớp. Khi đổi mật khẩu thành công, token cũ bị thu hồi;
response trả token mới để frontend tiếp tục phiên hiện tại. Vai trò và
tên đăng nhập không được cập nhật qua API hồ sơ.

## 6.3. API sinh viên và phân phòng

| Method | API hiện có | Chức năng |
|---|---|---|
| GET | `/api/students` | Tìm kiếm và liệt kê sinh viên |
| POST | `/api/students` | Tạo hồ sơ sinh viên |
| GET | `/api/students/{student_id}` | Xem hồ sơ sinh viên |
| PUT/PATCH | `/api/students/{student_id}` | Cập nhật hồ sơ |
| DELETE | `/api/students/{student_id}` | Xóa hồ sơ nếu chưa có dữ liệu nghiệp vụ tham chiếu |
| GET | `/api/rooms?date=YYYY-MM-DD&available=true` | Liệt kê phòng, số người đang ở tại ngày chọn và lọc phòng còn chỗ |
| POST | `/api/rooms` | Tạo phòng với cấu hình giá và sức chứa được hỗ trợ |
| GET | `/api/rooms/{room_id}` | Xem chi tiết phòng và số người ở hiện tại |
| PUT/PATCH | `/api/rooms/{room_id}` | Cập nhật thông tin phòng |
| DELETE | `/api/rooms/{room_id}` | Xóa phòng nếu chưa có lịch sử phân phòng |
| GET | `/api/room-assignments` | Liệt kê lượt phân phòng; có thể lọc theo sinh viên, phòng và lượt còn hiệu lực |
| POST | `/api/room-assignments` | Phân phòng cho sinh viên |
| PATCH | `/api/room-assignments/{id}/end` | Ghi nhận ngày rời phòng |
| GET | `/api/students/{student_id}/room-history` | Xem lịch sử phân phòng |
| GET | `/api/reports/room-capacity` | Thống kê số người ở, sức chứa và số chỗ còn lại theo ngày |

## 6.4. API lượt thăm

| Method | API hiện có | Chức năng |
|---|---|---|
| GET | `/api/visits` | Liệt kê lượt thăm; có thể lọc theo sinh viên hoặc khách |
| POST | `/api/visits` | Ghi nhận lượt thăm với thông tin khách nhập trực tiếp; tạo/tái sử dụng hồ sơ khách |
| PATCH | `/api/visits/{id}/departure` | Ghi nhận thời gian khách rời đi |
| GET | `/api/reports/visits` | Báo cáo lượt thăm theo tuần/tháng |

Không có API danh mục khách riêng. Lượt thăm đang mở không thể tạo
trùng cho cùng một khách; khi không gửi `left_at` lúc rời đi, Backend
ghi nhận thời điểm hiện tại.

## 6.5. API dịch vụ

| Method | API hiện có | Chức năng |
|---|---|---|
| GET | `/api/services` | Liệt kê danh mục dịch vụ |
| POST | `/api/services` | Thêm dịch vụ |
| GET | `/api/services/{id}` | Xem dịch vụ |
| PUT/PATCH | `/api/services/{id}` | Cập nhật dịch vụ và đơn giá |
| DELETE | `/api/services/{id}` | Xóa dịch vụ nếu chưa có lượt sử dụng |
| POST | `/api/service-usages` | Ghi nhận lần sử dụng dịch vụ |
| GET | `/api/reports/service-usage` | Tổng hợp tiền theo sinh viên, dịch vụ và khoảng ngày |
| GET | `/api/reports/service-revenue` | Báo cáo doanh thu từng dịch vụ theo tháng |

## 6.6. API xe tháng và lượt gửi/lấy

| Method | API hiện có | Chức năng |
|---|---|---|
| GET | `/api/vehicles` | Tra cứu xe đã đăng ký vé tháng; có thể lọc theo tháng/năm |
| POST | `/api/monthly-vehicle-registrations` | Đăng ký xe vé tháng; kiểm tra giới hạn |
| GET | `/api/monthly-vehicle-registrations` | Tra cứu đăng ký; có thể lọc theo sinh viên/tháng/năm |
| POST | `/api/monthly-vehicle-registrations/{registration_id}/events` | Ghi nhận lượt gửi hoặc lấy xe |
| GET | `/api/reports/vehicle-registration-limits` | Thống kê số xe theo sinh viên và kiểm tra giới hạn trong kỳ |

## 6.7. API hóa đơn và báo cáo

| Method | API hiện có | Chức năng |
|---|---|---|
| POST | `/api/invoices/generate` | Tạo/cập nhật hóa đơn của một sinh viên theo tháng/năm; tiền phòng nhập khi tạo mới |
| GET | `/api/invoices` | Liệt kê hóa đơn, lọc theo sinh viên, tháng, năm và trạng thái |
| GET | `/api/invoices/{id}` | Xem chi tiết hóa đơn |
| PATCH | `/api/invoices/{id}/status` | Cập nhật trạng thái thanh toán |
| GET | `/api/reports/monthly-student-costs` | Chi phí theo sinh viên nội trú trong tháng, không phụ thuộc hóa đơn |

## 6.8. Yêu cầu dữ liệu truy vấn

1. Liệt kê thông tin sinh viên có thời gian ở KTX giao với tháng được chọn,
   cùng tiền phòng, dịch vụ, vé tháng và tổng tiền phải trả. Tiền phòng
   tính trọn tháng nếu sinh viên ở ít nhất một ngày; kết quả sắp xếp theo
   họ tên và có thể in toàn bộ danh sách.
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

- Người dùng phải đăng nhập trước khi truy cập chức năng nghiệp vụ hoặc
  quản lý tài khoản.
- Chỉ đăng ký và đăng nhập được công khai; mọi API còn lại yêu cầu token
  hợp lệ. Tất cả tài khoản đã xác thực có cùng vai trò `STAFF`.
- Backend phải kiểm tra quyền trên từng thao tác; không chỉ ẩn chức năng
  trên giao diện.
- Mật khẩu không được lưu dưới dạng văn bản thuần và không được trả về
  trong API response.
- Email phải được xác thực và duy nhất không phân biệt hoa/thường. Mọi
  tài khoản mới có vai trò cố định `STAFF`.
- API cập nhật hồ sơ chỉ tác động đến tài khoản đang đăng nhập. Đổi mật
  khẩu phải xác minh mật khẩu hiện tại, thu hồi token cũ và cấp token mới.
- Không cho phép người dùng tự đổi tên đăng nhập hoặc vai trò qua hồ sơ.
- Dữ liệu đầu vào phải được xác thực; truy vấn cơ sở dữ liệu phải tránh
  SQL injection.
- Thông tin kết nối CSDL và khóa bí mật không được đưa vào mã nguồn công
  khai hoặc API response.

## 7.2. Hiệu năng và khả năng sử dụng

- Các thao tác thông thường nên phản hồi trong 3 giây ở điều kiện tải
  bình thường.
- Danh sách hiện tải toàn bộ kết quả; danh sách sinh viên hỗ trợ tìm kiếm,
  còn hóa đơn, lượt thăm, phòng và xe hỗ trợ các bộ lọc được mô tả trong
  hợp đồng API. Phân trang chưa được triển khai.
- Báo cáo cần cho phép chọn tháng hoặc khoảng thời gian cần tra cứu.
- Giao diện cần hiển thị thông báo rõ ràng khi thao tác thành công hoặc
  khi dữ liệu không hợp lệ.

## 7.3. Tính toàn vẹn dữ liệu

- Khóa chính và khóa ngoại phải đảm bảo dữ liệu tham chiếu hợp lệ.
- Không để phân phòng vượt sức chứa hoặc tạo lượt ở trùng thời gian.
- Không để một sinh viên đăng ký quá 2 xe vé tháng trong một tháng.
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

Hệ thống quản lý ký túc xá sinh viên tập trung các nghiệp vụ tài khoản
(đăng ký Staff, đăng nhập bằng email, hồ sơ cá nhân, một vai trò Staff), quản lý
sinh viên, phòng, khách thăm, dịch vụ, xe tháng, hóa đơn và báo cáo.
Các quy tắc về sức chứa, chi phí hàng tháng và lượt gửi/lấy xe là cơ sở
để Backend và Database đảm bảo dữ liệu chính xác, nhất quán.

Hệ thống được định hướng triển khai theo mô hình:

React + Vite

↓

Django REST Framework

↓

SQLite mặc định hoặc MySQL theo cấu hình

## 8.2. Phạm vi và hạn chế

Phiên bản yêu cầu hiện tại chỉ có một vai trò tài khoản Staff phục vụ
nhân viên ban quản lý; mọi tài khoản có quyền như nhau và có thể tự đăng
ký. Tài khoản đăng nhập riêng cho sinh viên và khách, các lượt gửi/lấy
của xe không đăng ký vé tháng, cổng thanh toán trực tuyến và ứng dụng di
động không nằm trong phạm vi đã xác định.

Phương thức thanh toán thực tế chưa được triển khai; trạng thái hóa đơn
được Staff cập nhật thủ công. Khi chuyển phòng trong tháng, báo cáo chi
phí hiện cộng tiền tháng của từng lượt phân phòng giao với kỳ; hóa đơn
được lập riêng theo một khoản tiền phòng do Staff nhập.

## 8.3. Hướng phát triển

Trong các phiên bản tiếp theo có thể xem xét:

- Bổ sung cổng thông tin để sinh viên tự tra cứu hóa đơn và dịch vụ.
- Tích hợp thanh toán điện tử nếu có yêu cầu.
- Bổ sung xuất báo cáo ra Excel/PDF.
- Mở rộng thống kê công suất phòng và doanh thu theo nhiều kỳ.
- Bổ sung thông báo tự động về hóa đơn hoặc các khoản chưa thanh toán.
