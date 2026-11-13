from django.db import models

from apps.students.models import Student


# Danh mục phòng; đơn giá và sức chứa được lưu trực tiếp trên từng phòng.
class Room(models.Model):
    room_id = models.CharField(max_length=15, primary_key=True, db_column="MaPhong")
    name = models.CharField(max_length=30, db_column="TenPhong")
    floor = models.IntegerField(null=True, blank=True, db_column="Tang")
    monthly_price = models.DecimalField(
        max_digits=12, decimal_places=2, db_column="DonGia"
    )
    max_occupants = models.PositiveIntegerField(db_column="SoNguoiToiDa")

    # Each room uses one of the supported monthly price/capacity pairs.
    class Meta:
        db_table = "PHONG"
        ordering = ["room_id"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(monthly_price="1800000.00", max_occupants=4)
                    | models.Q(monthly_price="250000.00", max_occupants=8)
                ),
                name="room_price_capacity_pair_valid",
            ),
        ]

    def __str__(self):
        return self.room_id


# Lịch sử sinh viên ở phòng; end_date trống nghĩa là lượt ở còn hiệu lực.
class RoomAssignment(models.Model):
    id = models.AutoField(primary_key=True, db_column="MaPhanPhong")
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="room_assignments",
        db_column="MaSV",
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name="assignments",
        db_column="MaPhong",
    )
    start_date = models.DateField(db_column="NgayVao")
    end_date = models.DateField(null=True, blank=True, db_column="NgayRa")

    # Ánh xạ bảng phân phòng và bảo đảm ngày ra không trước ngày vào.
    class Meta:
        db_table = "PHANPHONG"
        ordering = ["-start_date", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__isnull=True)
                | models.Q(end_date__gte=models.F("start_date")),
                name="room_assignment_end_after_start",
            ),
        ]

    def __str__(self):
        return f"{self.student_id} - {self.room_id}"