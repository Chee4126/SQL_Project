-- Du lieu mau cho ky thang 03/2025.
-- Co the chay lai script ma khong tao ban ghi trung.
USE ql_ktx;

INSERT INTO SINHVIEN (MaSV, HoTen, SoCMT, NgaySinh, Lop, QueQuan) VALUES
    ('SV001', 'Nguyen Minh Anh', '001203000001', '2003-04-12', 'CNTT01', 'Ha Noi'),
    ('SV002', 'Tran Quoc Bao', '001203000002', '2003-08-20', 'CNTT02', 'Hai Phong'),
    ('SV003', 'Le Thu Chi', '001203000003', '2004-01-05', 'QTKD01', 'Da Nang')
ON DUPLICATE KEY UPDATE
    HoTen = VALUES(HoTen),
    SoCMT = VALUES(SoCMT),
    NgaySinh = VALUES(NgaySinh),
    Lop = VALUES(Lop),
    QueQuan = VALUES(QueQuan);

INSERT INTO LOAIPHONG (MaLoaiPhong, TenLoaiPhong, DonGia, SoNguoiToiDa) VALUES
    (1, 'Phong 2 nguoi', 500000.00, 2),
    (2, 'Phong 4 nguoi', 350000.00, 4)
ON DUPLICATE KEY UPDATE
    TenLoaiPhong = VALUES(TenLoaiPhong),
    DonGia = VALUES(DonGia),
    SoNguoiToiDa = VALUES(SoNguoiToiDa);

INSERT INTO PHONG (MaPhong, MaLoaiPhong, TenPhong, Tang) VALUES
    ('A101', 1, 'Phong A101', 1),
    ('A102', 1, 'Phong A102', 1),
    ('B201', 2, 'Phong B201', 2)
ON DUPLICATE KEY UPDATE
    MaLoaiPhong = VALUES(MaLoaiPhong),
    TenPhong = VALUES(TenPhong),
    Tang = VALUES(Tang);

INSERT INTO PHANPHONG (MaPhanPhong, MaSV, MaPhong, NgayVao, NgayRa) VALUES
    (1, 'SV001', 'A101', '2025-01-01', NULL),
    (2, 'SV002', 'A101', '2025-01-01', NULL),
    (3, 'SV003', 'B201', '2025-02-01', NULL)
ON DUPLICATE KEY UPDATE
    MaSV = VALUES(MaSV),
    MaPhong = VALUES(MaPhong),
    NgayVao = VALUES(NgayVao),
    NgayRa = VALUES(NgayRa);

INSERT INTO KHACH (MaKhach, HoTen, SoCMT, NgaySinh) VALUES
    (1, 'Pham Van Dung', '079203000001', '2002-07-14'),
    (2, 'Do Ngoc Ha', '079203000002', '2003-11-02'),
    (3, 'Vu Thanh Long', '079203000003', '2002-02-18')
ON DUPLICATE KEY UPDATE
    HoTen = VALUES(HoTen),
    SoCMT = VALUES(SoCMT),
    NgaySinh = VALUES(NgaySinh);

INSERT INTO LUOTTHAM (MaLuotTham, MaKhach, MaSV, NgayDen, NgayDi) VALUES
    (1, 1, 'SV001', '2025-03-03 10:00:00', '2025-03-03 12:00:00'),
    (2, 1, 'SV001', '2025-03-05 14:00:00', '2025-03-05 16:00:00'),
    (3, 2, 'SV001', '2025-03-06 09:00:00', '2025-03-06 11:00:00'),
    (4, 3, 'SV002', '2025-03-12 15:00:00', '2025-03-12 17:00:00'),
    (5, 1, 'SV001', '2025-02-10 10:00:00', '2025-02-10 12:00:00')
ON DUPLICATE KEY UPDATE
    MaKhach = VALUES(MaKhach),
    MaSV = VALUES(MaSV),
    NgayDen = VALUES(NgayDen),
    NgayDi = VALUES(NgayDi);

INSERT INTO DICHVU (MaDV, TenDV, DonGia, DonViTinh) VALUES
    (1, 'Giat ui', 25000.00, 'kg'),
    (2, 'An uong', 40000.00, 'suat'),
    (3, 'Thue xe dap', 50000.00, 'ngay')
ON DUPLICATE KEY UPDATE
    TenDV = VALUES(TenDV),
    DonGia = VALUES(DonGia),
    DonViTinh = VALUES(DonViTinh);

INSERT INTO SUDUNGDICHVU
    (MaSuDung, MaSV, MaDV, ThoiGianSuDung, SoLuong, DonGiaApDung)
VALUES
    (1, 'SV001', 1, '2025-03-02 08:00:00', 2, 25000.00),
    (2, 'SV001', 2, '2025-03-05 12:00:00', 1, 40000.00),
    (3, 'SV001', 1, '2025-03-20 08:00:00', 1, 25000.00),
    (4, 'SV002', 1, '2025-03-08 08:00:00', 1, 25000.00),
    (5, 'SV003', 2, '2025-03-10 12:00:00', 2, 40000.00),
    (6, 'SV001', 2, '2025-02-10 12:00:00', 1, 38000.00)
ON DUPLICATE KEY UPDATE
    MaSV = VALUES(MaSV),
    MaDV = VALUES(MaDV),
    ThoiGianSuDung = VALUES(ThoiGianSuDung),
    SoLuong = VALUES(SoLuong),
    DonGiaApDung = VALUES(DonGiaApDung);

INSERT INTO XE (BienSo, LoaiXe) VALUES
    ('29A-11111', 'Xe may'),
    ('29A-22222', 'Xe may'),
    ('29B-33333', 'Xe dap dien')
ON DUPLICATE KEY UPDATE
    LoaiXe = VALUES(LoaiXe);

INSERT INTO DANGKYVEXE
    (MaDangKy, MaSV, BienSo, Thang, Nam, DonGia)
VALUES
    (1, 'SV001', '29A-11111', 3, 2025, 100000.00),
    (2, 'SV001', '29A-22222', 3, 2025, 100000.00),
    (3, 'SV002', '29B-33333', 3, 2025, 100000.00)
ON DUPLICATE KEY UPDATE
    MaSV = VALUES(MaSV),
    BienSo = VALUES(BienSo),
    Thang = VALUES(Thang),
    Nam = VALUES(Nam),
    DonGia = VALUES(DonGia);

INSERT INTO LUOTGUIXE
    (MaLuot, MaDangKy, ThoiGian, LoaiLuot, MienPhi, TienPhat)
VALUES
    (1, 1, '2025-03-03 07:00:00', 'GUI', TRUE, 0.00),
    (2, 1, '2025-03-03 11:00:00', 'LAY', TRUE, 0.00),
    (3, 1, '2025-03-03 13:00:00', 'GUI', FALSE, 3000.00),
    (4, 1, '2025-03-03 17:00:00', 'LAY', FALSE, 3000.00),
    (5, 2, '2025-03-03 08:00:00', 'GUI', TRUE, 0.00),
    (6, 2, '2025-03-03 18:00:00', 'LAY', TRUE, 0.00),
    (7, 3, '2025-03-04 08:00:00', 'GUI', TRUE, 0.00),
    (8, 3, '2025-03-04 18:00:00', 'LAY', TRUE, 0.00)
ON DUPLICATE KEY UPDATE
    MaDangKy = VALUES(MaDangKy),
    ThoiGian = VALUES(ThoiGian),
    LoaiLuot = VALUES(LoaiLuot),
    MienPhi = VALUES(MienPhi),
    TienPhat = VALUES(TienPhat);

INSERT INTO HOADON
    (MaHD, MaSV, Thang, Nam, TienPhong, TienDichVu, TienXe, PhiGuiXe, TongTien, TrangThai)
VALUES
    (1, 'SV001', 3, 2025, 500000.00, 115000.00, 200000.00, 6000.00, 821000.00, 'CHUA_THANH_TOAN'),
    (2, 'SV002', 3, 2025, 500000.00, 25000.00, 100000.00, 0.00, 625000.00, 'DA_THANH_TOAN'),
    (3, 'SV003', 3, 2025, 350000.00, 80000.00, 0.00, 0.00, 430000.00, 'CHUA_THANH_TOAN')
ON DUPLICATE KEY UPDATE
    MaSV = VALUES(MaSV),
    Thang = VALUES(Thang),
    Nam = VALUES(Nam),
    TienPhong = VALUES(TienPhong),
    TienDichVu = VALUES(TienDichVu),
    TienXe = VALUES(TienXe),
    PhiGuiXe = VALUES(PhiGuiXe),
    TongTien = VALUES(TongTien),
    TrangThai = VALUES(TrangThai);
