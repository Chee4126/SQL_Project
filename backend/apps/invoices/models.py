from django.db import models

from apps.services.models import Service
from apps.students.models import Student


# Lưu bản chụp các khoản phí của sinh viên theo từng kỳ hóa đơn.
class Invoice(models.Model):
    class PaymentStatus(models.TextChoices):
        UNPAID = "CHUA_THANH_TOAN", "Chưa thanh toán"
        PAID = "DA_THANH_TOAN", "Đã thanh toán"

    id = models.AutoField(primary_key=True, db_column="MaHD")
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="invoices",
        db_column="MaSV",
    )
    month = models.PositiveSmallIntegerField(db_column="Thang")
    year = models.PositiveSmallIntegerField(db_column="Nam")
    room_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="TienPhong",
    )
    service_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="TienDichVu",
    )
    vehicle_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="TienXe",
    )
    parking_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="PhiGuiXe",
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="TongTien",
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        db_column="TrangThai",
    )

    # Mỗi sinh viên chỉ có một hóa đơn trong một tháng/năm; mọi khoản tiền
    # và tổng tiền đều được giữ không âm và tổng phải bằng tổng các khoản.
    class Meta:
        db_table = "HOADON"
        ordering = ["-year", "-month", "student__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "month", "year"],
                name="invoice_student_period_uq",
            ),
            models.CheckConstraint(
                condition=models.Q(month__gte=1, month__lte=12),
                name="invoice_month_range",
            ),
            models.CheckConstraint(
                condition=models.Q(year__gte=1),
                name="invoice_year_positive",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(room_amount__gte=0)
                    & models.Q(service_amount__gte=0)
                    & models.Q(vehicle_amount__gte=0)
                    & models.Q(parking_amount__gte=0)
                    & models.Q(total_amount__gte=0)
                ),
                name="invoice_amounts_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    total_amount=(
                        models.F("room_amount")
                        + models.F("service_amount")
                        + models.F("vehicle_amount")
                        + models.F("parking_amount")
                    )
                ),
                name="invoice_total_matches_parts",
            ),
        ]

    def __str__(self):
        return f"{self.student_id} - {self.month:02d}/{self.year}"


class InvoiceServiceLine(models.Model):
    id = models.AutoField(primary_key=True, db_column="MaCTHD")
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="service_lines",
        db_column="MaHD",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoice_lines",
        db_column="MaDV",
    )
    service_name = models.CharField(max_length=100, db_column="TenDV")
    unit = models.CharField(max_length=30, blank=True, db_column="DonViTinh")
    quantity = models.PositiveIntegerField(db_column="SoLuong")
    applied_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="DonGiaApDung",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="ThanhTien",
    )

    class Meta:
        db_table = "CHITIETHOADON"
        ordering = ["service_name", "applied_price", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="invoice_service_line_quantity_positive",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(applied_price__gte=0)
                    & models.Q(amount__gte=0)
                ),
                name="invoice_service_line_amounts_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    amount=models.F("quantity") * models.F("applied_price")
                ),
                name="invoice_service_line_total_matches",
            ),
        ]
