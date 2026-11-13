from decimal import Decimal

from django.db import models

from apps.students.models import Student


# Lưu thông tin xe chỉ khi xe được đăng ký vé tháng.
class Vehicle(models.Model):
    plate_number = models.CharField(
        max_length=20,
        primary_key=True,
        db_column="BienSo",
    )
    vehicle_type = models.CharField(max_length=50, db_column="LoaiXe")

    # Ánh xạ model vào bảng xe theo thiết kế SRS.
    # Ánh xạ model vào bảng xe và sắp xếp theo biển số.
    class Meta:
        db_table = "XE"
        ordering = ["plate_number"]

    def __str__(self):
        return self.plate_number


# Lưu đăng ký xe tháng và giá vé được áp dụng cho kỳ đó.
class MonthlyVehicleRegistration(models.Model):
    id = models.AutoField(primary_key=True, db_column="MaDangKy")
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="monthly_vehicle_registrations",
        db_column="MaSV",
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="registrations",
        db_column="BienSo",
    )
    month = models.PositiveSmallIntegerField(db_column="Thang")
    year = models.PositiveSmallIntegerField(db_column="Nam")
    monthly_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("100000.00"),
        db_column="DonGia",
    )

    # Bảo đảm xe chỉ đăng ký một lần mỗi kỳ và lưu lịch sử giá.
    # Khai báo bảng, thứ tự hiển thị và các ràng buộc đăng ký.
    class Meta:
        db_table = "DANGKYVEXE"
        ordering = ["-year", "-month", "student_id", "vehicle_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "vehicle", "month", "year"],
                name="vehicle_reg_student_vehicle_period_uq",
            ),
            models.UniqueConstraint(
                fields=["vehicle", "month", "year"],
                name="vehicle_reg_vehicle_period_uq",
            ),
            models.CheckConstraint(
                condition=models.Q(month__gte=1, month__lte=12),
                name="vehicle_reg_month_range",
            ),
            models.CheckConstraint(
                condition=models.Q(monthly_price__gte=0),
                name="vehicle_reg_price_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(year__gte=1),
                name="vehicle_reg_year_positive",
            ),
        ]

    def __str__(self):
        return f"{self.vehicle_id} - {self.month:02d}/{self.year}"


# Lưu lượt gửi/lấy của xe đăng ký vé tháng.
class VehicleEvent(models.Model):
    # Quy định hai loại sự kiện xe được phép ghi nhận.
    class EventType(models.TextChoices):
        PARK = "GUI", "Gửi xe"
        PICKUP = "LAY", "Lấy xe"

    id = models.AutoField(primary_key=True, db_column="MaLuot")
    registration = models.ForeignKey(
        MonthlyVehicleRegistration,
        on_delete=models.PROTECT,
        related_name="events",
        db_column="MaDangKy",
    )
    event_at = models.DateTimeField(db_column="ThoiGian")
    event_type = models.CharField(
        max_length=3,
        choices=EventType.choices,
        db_column="LoaiLuot",
    )
    is_free = models.BooleanField(null=True, blank=True, db_column="MienPhi")
    fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        db_column="TienPhat",
    )

    # Fee columns remain nullable to preserve values recorded by older versions.
    class Meta:
        db_table = "LUOTGUIXE"
        ordering = ["-event_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(fee__gte=0),
                name="vehicle_event_fee_nonnegative",
            ),
        ]
