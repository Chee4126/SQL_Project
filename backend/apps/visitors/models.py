from django.db import models

from apps.students.models import Student


# Hồ sơ khách đến thăm sinh viên.
class Visitor(models.Model):
    id = models.AutoField(primary_key=True, db_column="MaKhach")
    name = models.CharField(max_length=100, db_column="HoTen")
    identity_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        db_column="SoCMT",
    )
    birth_date = models.DateField(null=True, blank=True, db_column="NgaySinh")

    # Ánh xạ bảng khách và sắp xếp theo họ tên.
    class Meta:
        db_table = "KHACH"
        ordering = ["name", "id"]

    def __str__(self):
        return f"{self.id} - {self.name}"


# Từng lượt khách đến thăm; left_at trống nghĩa là khách chưa rời đi.
class Visit(models.Model):
    id = models.AutoField(primary_key=True, db_column="MaLuotTham")
    visitor = models.ForeignKey(
        Visitor,
        on_delete=models.PROTECT,
        related_name="visits",
        db_column="MaKhach",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="visits",
        db_column="MaSV",
    )
    arrived_at = models.DateTimeField(db_column="NgayDen")
    left_at = models.DateTimeField(null=True, blank=True, db_column="NgayDi")

    # Ánh xạ bảng lượt thăm và bảo đảm giờ rời không trước giờ đến.
    class Meta:
        db_table = "LUOTTHAM"
        ordering = ["-arrived_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(left_at__isnull=True)
                | models.Q(left_at__gte=models.F("arrived_at")),
                name="visit_left_after_arrived",
            ),
        ]

    def __str__(self):
        return f"{self.visitor_id} -> {self.student_id}"