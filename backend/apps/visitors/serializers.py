from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.students.models import Student
from apps.visitors.models import Visit, Visitor


# Kiểm tra dữ liệu hồ sơ khách.
class VisitorSerializer(serializers.ModelSerializer):
    identity_number = serializers.CharField(
        max_length=20,
        required=False,
        allow_null=True,
        validators=[
            UniqueValidator(
                queryset=Visitor.objects.all(),
                message="Số CMT/CCCD đã được dùng cho khách khác.",
            )
        ],
    )

    # Khai báo các trường khách trao đổi qua API.
    class Meta:
        model = Visitor
        fields = ["id", "name", "identity_number", "birth_date"]
        read_only_fields = ["id"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Họ tên khách không được để trống.")
        return value


# Ghi nhận lượt thăm và kiểm tra khách chưa có lượt thăm nào đang mở.
class VisitSerializer(serializers.ModelSerializer):
    visitor_id = serializers.PrimaryKeyRelatedField(
        source="visitor", queryset=Visitor.objects.all()
    )
    visitor_name = serializers.CharField(source="visitor.name", read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        source="student", queryset=Student.objects.all()
    )
    student_name = serializers.CharField(source="student.name", read_only=True)
    left_at = serializers.DateTimeField(required=False, allow_null=True)

    # Khai báo các trường lượt thăm trao đổi qua API.
    class Meta:
        model = Visit
        fields = [
            "id",
            "visitor_id",
            "visitor_name",
            "student_id",
            "student_name",
            "arrived_at",
            "left_at",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        arrived_at = attrs.get("arrived_at")
        left_at = attrs.get("left_at")
        if left_at is not None and arrived_at is not None and left_at < arrived_at:
            raise serializers.ValidationError(
                {"left_at": "Thời gian rời đi không được trước thời gian đến."}
            )
        visitor = attrs.get("visitor")
        if visitor and Visit.objects.filter(
            visitor=visitor, left_at__isnull=True
        ).exists():
            raise serializers.ValidationError(
                {"visitor_id": "Khách này đang có lượt thăm chưa ghi nhận rời đi."}
            )
        return attrs