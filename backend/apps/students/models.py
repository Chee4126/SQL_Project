from django.db import models


class Student(models.Model):
    student_id = models.CharField(max_length=15, primary_key=True, db_column="MaSV")
    name = models.CharField(max_length=100, db_column="HoTen")
    identity_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        db_column="SoCMT",
    )
    birth_date = models.DateField(null=True, blank=True, db_column="NgaySinh")
    class_name = models.CharField(max_length=30, blank=True, db_column="Lop")
    hometown = models.CharField(max_length=150, blank=True, db_column="QueQuan")

    class Meta:
        db_table = "SINHVIEN"
        ordering = ["name"]

    def __str__(self):
        return f"{self.student_id} - {self.name}"
