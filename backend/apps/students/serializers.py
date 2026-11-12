from datetime import date

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.students.models import Student


# Kiểm tra dữ liệu hồ sơ sinh viên khi tạo và cập nhật.
class StudentSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(
        max_length=15,
        validators=[
            UniqueValidator(
                queryset=Student.objects.all(),
                message="Mã sinh viên đã tồn tại.",
            )
        ],
    )
    identity_number = serializers.CharField(
        max_length=20,
        required=False,
        allow_null=True,
        validators=[
            UniqueValidator(
                queryset=Student.objects.all(),
                message="Số CMT/CCCD đã được dùng cho sinh viên khác.",
            )
        ],
    )

    # Khai báo các trường hồ sơ sinh viên trao đổi qua API.
    class Meta:
        model = Student
        fields = [
            "student_id",
            "name",
            "identity_number",
            "birth_date",
            "class_name",
            "hometown",
        ]

    def validate_student_id(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Mã sinh viên không được để trống.")
        # Mã sinh viên là khóa chính nên không cho đổi khi cập nhật.
        if self.instance and value != self.instance.pk:
            raise serializers.ValidationError("Không được thay đổi mã sinh viên.")
        return value

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Họ tên không được để trống.")
        return value

    def validate_birth_date(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("Ngày sinh không được ở tương lai.")
        return value