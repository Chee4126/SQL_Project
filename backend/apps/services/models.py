from django.db import models

from apps.students.models import Student


# Lưu danh mục dịch vụ và đơn giá hiện hành.
class Service(models.Model):
    id = models.AutoField(primary_key=True, db_column="MaDV")
    name = models.CharField(max_length=100, db_column="TenDV")
    price = models.DecimalField(max_digits=12, decimal_places=2, db_column="DonGia")
    unit = models.CharField(max_length=30, blank=True, db_column="DonViTinh")

    # Cấu hình tên bảng và thứ tự danh sách dịch vụ.
    class Meta:
        db_table = "DICHVU"
        ordering = ["name"]

    def __str__(self):
        return self.name


# Lưu từng lần sinh viên sử dụng dịch vụ cùng đơn giá đã áp dụng.
class ServiceUsage(models.Model):
    id = models.AutoField(primary_key=True, db_column="MaSuDung")
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="service_usages",
        db_column="MaSV",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="usages",
        db_column="MaDV",
    )
    used_at = models.DateTimeField(db_column="ThoiGianSuDung")
    quantity = models.PositiveIntegerField(db_column="SoLuong")
    applied_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_column="DonGiaApDung",
    )

    # Cấu hình bảng, thứ tự bản ghi và ràng buộc dữ liệu sử dụng.
    class Meta:
        db_table = "SUDUNGDICHVU"
        ordering = ["-used_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="service_usage_quantity_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(applied_price__gte=0),
                name="service_usage_price_nonnegative",
            ),
        ]

    @property
    def amount(self):
        return self.quantity * self.applied_price
