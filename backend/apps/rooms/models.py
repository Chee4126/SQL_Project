from django.db import models

from apps.students.models import Student


# Loại phòng quy định đơn giá tháng và sức chứa tối đa.
class RoomType(models.Model):
    id = models.AutoField(primary_key=True, db_column="MaLoaiPhong")
    name = models.CharField(max_length=50, unique=True, db_column="TenLoaiPhong")
    monthly_price = models.DecimalField(
        max_digits=12, decimal_places=2, db_column="DonGia"
    )
    max_occupants = models.PositiveIntegerField(db_column="SoNguoiToiDa")

    # Ánh xạ bảng loại phòng và áp đặt đơn giá không âm, sức chứa dương.
    class Meta:
        db_table = "LOAIPHONG"
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(monthly_price__gte=0),
                name="room_type_price_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(max_occupants__gte=1),
                name="room_type_capacity_positive",
            ),
        ]

    def __str__(self):
        return self.name


# Danh mục phòng; đơn giá và sức chứa lấy theo loại phòng.
class Room(models.Model):
    room_id = models.CharField(max_length=15, primary_key=True, db_column="MaPhong")
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,
        related_name="rooms",
        db_column="MaLoaiPhong",
    )
    name = models.CharField(max_length=30, db_column="TenPhong")
    floor = models.IntegerField(null=True, blank=True, db_column="Tang")

    # Ánh xạ bảng phòng và sắp xếp theo mã phòng.
    class Meta:
        db_table = "PHONG"
        ordering = ["room_id"]

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