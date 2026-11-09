-- Cac truy van theo muc "Cac yeu cau truy van" cua Project 2.
USE ql_ktx;

-- 1. Sinh vien dang o KTX va cac khoan phai tra trong mot thang.
-- Doi hai gia tri nay de xem ky hoa don khac.
SET @Thang = 3;
SET @Nam = 2025;
SET @NgayDauThang = STR_TO_DATE(
    CONCAT(@Nam, '-', LPAD(@Thang, 2, '0'), '-01'),
    '%Y-%m-%d'
);
SET @NgayDauThangSau = DATE_ADD(@NgayDauThang, INTERVAL 1 MONTH);

SELECT
    sv.MaSV,
    sv.HoTen,
    COALESCE(hd.TienPhong, 0.00) AS TienPhong,
    COALESCE(hd.TienDichVu, 0.00) AS TienDichVu,
    COALESCE(hd.TienXe, 0.00) AS TienXe,
    COALESCE(hd.PhiGuiXe, 0.00) AS PhiGuiXe,
    COALESCE(hd.TongTien, 0.00) AS TongTien
FROM SINHVIEN AS sv
LEFT JOIN HOADON AS hd
    ON hd.MaSV = sv.MaSV
    AND hd.Thang = @Thang
    AND hd.Nam = @Nam
WHERE EXISTS (
    SELECT 1
    FROM PHANPHONG AS pp
    WHERE pp.MaSV = sv.MaSV
      AND pp.NgayVao < @NgayDauThangSau
      AND (pp.NgayRa IS NULL OR pp.NgayRa >= @NgayDauThang)
)
ORDER BY sv.HoTen, sv.MaSV;

-- 2. Tong tien moi sinh vien su dung theo tung dich vu trong khoang ngay.
-- Ngay ket thuc duoc tinh tron ngay.
SET @TuNgay = '2025-03-01';
SET @DenNgay = '2025-03-31';

SELECT
    sv.MaSV,
    sv.HoTen,
    dv.MaDV,
    dv.TenDV,
    SUM(sd.SoLuong) AS TongSoLuong,
    SUM(sd.SoLuong * sd.DonGiaApDung) AS TongTien
FROM SUDUNGDICHVU AS sd
JOIN SINHVIEN AS sv ON sv.MaSV = sd.MaSV
JOIN DICHVU AS dv ON dv.MaDV = sd.MaDV
WHERE sd.ThoiGianSuDung >= @TuNgay
  AND sd.ThoiGianSuDung < DATE_ADD(@DenNgay, INTERVAL 1 DAY)
GROUP BY sv.MaSV, sv.HoTen, dv.MaDV, dv.TenDV
ORDER BY sv.HoTen, dv.TenDV;

-- 3a. Luot khach tham theo tuan ISO trong khoang ngay.
SELECT
    sv.MaSV,
    sv.HoTen AS SinhVien,
    k.MaKhach,
    k.HoTen AS Khach,
    YEARWEEK(lt.NgayDen, 3) AS TuanISO,
    COUNT(*) AS SoLanDen
FROM LUOTTHAM AS lt
JOIN SINHVIEN AS sv ON sv.MaSV = lt.MaSV
JOIN KHACH AS k ON k.MaKhach = lt.MaKhach
WHERE lt.NgayDen >= @TuNgay
  AND lt.NgayDen < DATE_ADD(@DenNgay, INTERVAL 1 DAY)
GROUP BY
    sv.MaSV, sv.HoTen, k.MaKhach, k.HoTen, YEARWEEK(lt.NgayDen, 3)
ORDER BY TuanISO, sv.HoTen, k.HoTen;

-- 3b. Luot khach tham theo thang trong khoang ngay.
SELECT
    sv.MaSV,
    sv.HoTen AS SinhVien,
    k.MaKhach,
    k.HoTen AS Khach,
    DATE_FORMAT(lt.NgayDen, '%Y-%m') AS Thang,
    COUNT(*) AS SoLanDen
FROM LUOTTHAM AS lt
JOIN SINHVIEN AS sv ON sv.MaSV = lt.MaSV
JOIN KHACH AS k ON k.MaKhach = lt.MaKhach
WHERE lt.NgayDen >= @TuNgay
  AND lt.NgayDen < DATE_ADD(@DenNgay, INTERVAL 1 DAY)
GROUP BY
    sv.MaSV, sv.HoTen, k.MaKhach, k.HoTen,
    DATE_FORMAT(lt.NgayDen, '%Y-%m')
ORDER BY Thang, sv.HoTen, k.HoTen;

-- 4. Doanh thu moi dich vu trong tung thang cua nam.
SET @NamDoanhThu = 2025;

SELECT
    thang.Thang,
    dv.MaDV,
    dv.TenDV,
    COALESCE(SUM(sd.SoLuong * sd.DonGiaApDung), 0.00) AS DoanhThu
FROM (
    SELECT 1 AS Thang UNION ALL SELECT 2 UNION ALL SELECT 3
    UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6
    UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9
    UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12
) AS thang
CROSS JOIN DICHVU AS dv
LEFT JOIN SUDUNGDICHVU AS sd
    ON sd.MaDV = dv.MaDV
    AND sd.ThoiGianSuDung >= STR_TO_DATE(
        CONCAT(@NamDoanhThu, '-', LPAD(thang.Thang, 2, '0'), '-01'),
        '%Y-%m-%d'
    )
    AND sd.ThoiGianSuDung < DATE_ADD(
        STR_TO_DATE(
            CONCAT(@NamDoanhThu, '-', LPAD(thang.Thang, 2, '0'), '-01'),
            '%Y-%m-%d'
        ),
        INTERVAL 1 MONTH
    )
GROUP BY thang.Thang, dv.MaDV, dv.TenDV
ORDER BY thang.Thang, dv.TenDV;

-- 5a. Kiem tra suc chua phong tai ngay can kiem tra.
-- Ket qua hien thi tat ca phong; TrangThai cho biet co vuot suc chua khong.
SET @NgayKiemTra = '2025-03-15';

SELECT
    p.MaPhong,
    p.TenPhong,
    lp.SoNguoiToiDa,
    COUNT(pp.MaPhanPhong) AS SoNguoiDangO,
    CASE
        WHEN COUNT(pp.MaPhanPhong) > lp.SoNguoiToiDa THEN 'VUOT_SUC_CHUA'
        ELSE 'HOP_LE'
    END AS TrangThai
FROM PHONG AS p
JOIN LOAIPHONG AS lp ON lp.MaLoaiPhong = p.MaLoaiPhong
LEFT JOIN PHANPHONG AS pp
    ON pp.MaPhong = p.MaPhong
    AND pp.NgayVao <= @NgayKiemTra
    AND (pp.NgayRa IS NULL OR pp.NgayRa >= @NgayKiemTra)
GROUP BY p.MaPhong, p.TenPhong, lp.SoNguoiToiDa
ORDER BY p.MaPhong;

-- 5b. Kiem tra sinh vien dang ky qua 2 xe ve thang trong cung ky.
-- Truy van chi tra ve cac truong hop vi pham (neu co).
SELECT
    sv.MaSV,
    sv.HoTen,
    dk.Thang,
    dk.Nam,
    COUNT(*) AS SoXeDangKy
FROM DANGKYVEXE AS dk
JOIN SINHVIEN AS sv ON sv.MaSV = dk.MaSV
GROUP BY sv.MaSV, sv.HoTen, dk.Thang, dk.Nam
HAVING COUNT(*) > 2
ORDER BY dk.Nam, dk.Thang, sv.HoTen;

-- Hai truy van kiem tra tren phuc vu doi soat. Backend van phai kiem tra
-- suc chua va gioi han dang ky trong transaction de tranh cap nhat dong thoi.
