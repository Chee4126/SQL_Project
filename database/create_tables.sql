
-- Chay sau create_database.sql va chon database ql_ktx.
USE ql_ktx;

CREATE TABLE IF NOT EXISTS SINHVIEN (
    MaSV VARCHAR(15) NOT NULL,
    HoTen VARCHAR(100) NOT NULL,
    SoCMT VARCHAR(20) NULL,
    NgaySinh DATE NULL,
    Lop VARCHAR(30) NULL,
    QueQuan VARCHAR(150) NULL,
    CONSTRAINT pk_sinhvien PRIMARY KEY (MaSV),
    CONSTRAINT uq_sinhvien_socmt UNIQUE (SoCMT)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS LOAIPHONG (
    MaLoaiPhong INT NOT NULL AUTO_INCREMENT,
    TenLoaiPhong VARCHAR(50) NOT NULL,
    DonGia DECIMAL(12,2) NOT NULL,
    SoNguoiToiDa INT NOT NULL,
    CONSTRAINT pk_loaiphong PRIMARY KEY (MaLoaiPhong),
    CONSTRAINT uq_loaiphong_ten UNIQUE (TenLoaiPhong),
    CONSTRAINT chk_loaiphong_dongia CHECK (DonGia >= 0),
    CONSTRAINT chk_loaiphong_succhua CHECK (SoNguoiToiDa > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS PHONG (
    MaPhong VARCHAR(15) NOT NULL,
    MaLoaiPhong INT NOT NULL,
    TenPhong VARCHAR(30) NOT NULL,
    Tang INT NULL,
    CONSTRAINT pk_phong PRIMARY KEY (MaPhong),
    INDEX idx_phong_maloaiphong (MaLoaiPhong),
    CONSTRAINT fk_phong_loaiphong
        FOREIGN KEY (MaLoaiPhong) REFERENCES LOAIPHONG (MaLoaiPhong)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS PHANPHONG (
    MaPhanPhong INT NOT NULL AUTO_INCREMENT,
    MaSV VARCHAR(15) NOT NULL,
    MaPhong VARCHAR(15) NOT NULL,
    NgayVao DATE NOT NULL,
    NgayRa DATE NULL,
    CONSTRAINT pk_phanphong PRIMARY KEY (MaPhanPhong),
    INDEX idx_phanphong_masv (MaSV),
    INDEX idx_phanphong_maphong (MaPhong),
    CONSTRAINT fk_phanphong_sinhvien
        FOREIGN KEY (MaSV) REFERENCES SINHVIEN (MaSV),
    CONSTRAINT fk_phanphong_phong
        FOREIGN KEY (MaPhong) REFERENCES PHONG (MaPhong),
    CONSTRAINT chk_phanphong_ngay
        CHECK (NgayRa IS NULL OR NgayRa >= NgayVao)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS KHACH (
    MaKhach INT NOT NULL AUTO_INCREMENT,
    HoTen VARCHAR(100) NOT NULL,
    SoCMT VARCHAR(20) NULL,
    NgaySinh DATE NULL,
    CONSTRAINT pk_khach PRIMARY KEY (MaKhach),
    CONSTRAINT uq_khach_socmt UNIQUE (SoCMT)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS LUOTTHAM (
    MaLuotTham INT NOT NULL AUTO_INCREMENT,
    MaKhach INT NOT NULL,
    MaSV VARCHAR(15) NOT NULL,
    NgayDen DATETIME NOT NULL,
    NgayDi DATETIME NULL,
    CONSTRAINT pk_luottham PRIMARY KEY (MaLuotTham),
    INDEX idx_luottham_makhach (MaKhach),
    INDEX idx_luottham_masv (MaSV),
    CONSTRAINT fk_luottham_khach
        FOREIGN KEY (MaKhach) REFERENCES KHACH (MaKhach),
    CONSTRAINT fk_luottham_sinhvien
        FOREIGN KEY (MaSV) REFERENCES SINHVIEN (MaSV),
    CONSTRAINT chk_luottham_thoigian
        CHECK (NgayDi IS NULL OR NgayDi >= NgayDen)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS DICHVU (
    MaDV INT NOT NULL AUTO_INCREMENT,
    TenDV VARCHAR(100) NOT NULL,
    DonGia DECIMAL(12,2) NOT NULL,
    DonViTinh VARCHAR(30) NULL,
    CONSTRAINT pk_dichvu PRIMARY KEY (MaDV),
    CONSTRAINT chk_dichvu_dongia CHECK (DonGia >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS SUDUNGDICHVU (
    MaSuDung INT NOT NULL AUTO_INCREMENT,
    MaSV VARCHAR(15) NOT NULL,
    MaDV INT NOT NULL,
    ThoiGianSuDung DATETIME NOT NULL,
    SoLuong INT NOT NULL,
    DonGiaApDung DECIMAL(12,2) NOT NULL,
    CONSTRAINT pk_sudungdichvu PRIMARY KEY (MaSuDung),
    INDEX idx_sudungdichvu_masv (MaSV),
    INDEX idx_sudungdichvu_madv_thoigian (MaDV, ThoiGianSuDung),
    CONSTRAINT fk_sudungdichvu_sinhvien
        FOREIGN KEY (MaSV) REFERENCES SINHVIEN (MaSV),
    CONSTRAINT fk_sudungdichvu_dichvu
        FOREIGN KEY (MaDV) REFERENCES DICHVU (MaDV),
    CONSTRAINT chk_sudungdichvu_soluong CHECK (SoLuong > 0),
    CONSTRAINT chk_sudungdichvu_dongia CHECK (DonGiaApDung >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS XE (
    BienSo VARCHAR(20) NOT NULL,
    LoaiXe VARCHAR(50) NOT NULL,
    CONSTRAINT pk_xe PRIMARY KEY (BienSo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS DANGKYVEXE (
    MaDangKy INT NOT NULL AUTO_INCREMENT,
    MaSV VARCHAR(15) NOT NULL,
    BienSo VARCHAR(20) NOT NULL,
    Thang INT NOT NULL,
    Nam INT NOT NULL,
    DonGia DECIMAL(12,2) NOT NULL DEFAULT 100000.00,
    CONSTRAINT pk_dangkyvexe PRIMARY KEY (MaDangKy),
    CONSTRAINT uq_dangkyvexe_sinhvien_xe_ky
        UNIQUE (MaSV, BienSo, Thang, Nam),
    CONSTRAINT uq_dangkyvexe_xe_ky
        UNIQUE (BienSo, Thang, Nam),
    INDEX idx_dangkyvexe_sinhvien_ky (MaSV, Nam, Thang),
    CONSTRAINT fk_dangkyvexe_sinhvien
        FOREIGN KEY (MaSV) REFERENCES SINHVIEN (MaSV),
    CONSTRAINT fk_dangkyvexe_xe
        FOREIGN KEY (BienSo) REFERENCES XE (BienSo),
    CONSTRAINT chk_dangkyvexe_thang CHECK (Thang BETWEEN 1 AND 12),
    CONSTRAINT chk_dangkyvexe_nam CHECK (Nam >= 1),
    CONSTRAINT chk_dangkyvexe_dongia CHECK (DonGia >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS LUOTGUIXE (
    MaLuot INT NOT NULL AUTO_INCREMENT,
    MaDangKy INT NOT NULL,
    ThoiGian DATETIME NOT NULL,
    LoaiLuot ENUM('GUI', 'LAY') NOT NULL,
    MienPhi BOOLEAN NOT NULL,
    TienPhat DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT pk_luotguixe PRIMARY KEY (MaLuot),
    INDEX idx_luotguixe_dangky_thoigian (MaDangKy, ThoiGian),
    CONSTRAINT fk_luotguixe_dangky
        FOREIGN KEY (MaDangKy) REFERENCES DANGKYVEXE (MaDangKy),
    CONSTRAINT chk_luotguixe_tienphat CHECK (TienPhat >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS HOADON (
    MaHD INT NOT NULL AUTO_INCREMENT,
    MaSV VARCHAR(15) NOT NULL,
    Thang INT NOT NULL,
    Nam INT NOT NULL,
    TienPhong DECIMAL(12,2) NOT NULL,
    TienDichVu DECIMAL(12,2) NOT NULL,
    TienXe DECIMAL(12,2) NOT NULL,
    PhiGuiXe DECIMAL(12,2) NOT NULL,
    TongTien DECIMAL(12,2) NOT NULL,
    TrangThai ENUM('CHUA_THANH_TOAN', 'DA_THANH_TOAN') NOT NULL
        DEFAULT 'CHUA_THANH_TOAN',
    CONSTRAINT pk_hoadon PRIMARY KEY (MaHD),
    CONSTRAINT uq_hoadon_sinhvien_ky UNIQUE (MaSV, Thang, Nam),
    CONSTRAINT fk_hoadon_sinhvien
        FOREIGN KEY (MaSV) REFERENCES SINHVIEN (MaSV),
    CONSTRAINT chk_hoadon_thang CHECK (Thang BETWEEN 1 AND 12),
    CONSTRAINT chk_hoadon_nam CHECK (Nam >= 1),
    CONSTRAINT chk_hoadon_cackhoan CHECK (
        TienPhong >= 0
        AND TienDichVu >= 0
        AND TienXe >= 0
        AND PhiGuiXe >= 0
        AND TongTien >= 0
    ),
    CONSTRAINT chk_hoadon_tongtien CHECK (
        TongTien = TienPhong + TienDichVu + TienXe + PhiGuiXe
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Suc chua phong, thoi gian phan phong khong trung va gioi han 2 xe
-- can duoc kiem tra bang transaction trong Backend (muc 5.15 cua SRS).
