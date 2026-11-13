from decimal import Decimal

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.rooms.models import Room, RoomAssignment
from apps.rooms.services import assign_room
from apps.students.models import Student


# Hiển thị và kiểm tra dữ liệu phòng.
class RoomSerializer(serializers.ModelSerializer):
    room_id = serializers.CharField(
        max_length=15,
        validators=[
            UniqueValidator(
                queryset=Room.objects.all(), message="Số phòng đã tồn tại."
            )
        ],
    )
    current_occupants = serializers.IntegerField(read_only=True)

    # Khai báo các trường phòng trao đổi qua API.
    class Meta:
        model = Room
        fields = [
            "room_id",
            "name",
            "floor",
            "monthly_price",
            "max_occupants",
            "current_occupants",
        ]

    def validate_monthly_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Đơn giá không được âm.")
        return value

    def validate_max_occupants(self, value):
        if value < 1:
            raise serializers.ValidationError("Sức chứa phải lớn hơn 0.")
        return value

    def validate(self, attrs):
        price = attrs.get(
            "monthly_price",
            self.instance.monthly_price if self.instance else None,
        )
        capacity = attrs.get(
            "max_occupants",
            self.instance.max_occupants if self.instance else None,
        )
        valid_pairs = {
            (Decimal("1800000.00"), 4),
            (Decimal("250000.00"), 8),
        }
        if (
            price is not None
            and capacity is not None
            and (price, capacity) not in valid_pairs
        ):
            raise serializers.ValidationError(
                {
                    "monthly_price": (
                        "Chỉ hỗ trợ 1.800.000 đồng với sức chứa 4 người "
                        "hoặc 250.000 đồng với sức chứa 8 người."
                    )
                }
            )
        return attrs

    def validate_room_id(self, value):
        value = value.strip()
        if self.instance and value != self.instance.pk:
            raise serializers.ValidationError("Không được thay đổi số phòng.")
        return value


# Nhận yêu cầu phân phòng và giao việc kiểm tra cho tầng service.
class RoomAssignmentSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(
        source="student", queryset=Student.objects.all()
    )
    student_name = serializers.CharField(source="student.name", read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        source="room", queryset=Room.objects.all()
    )
    end_date = serializers.DateField(required=False, allow_null=True)
    is_active = serializers.SerializerMethodField()

    # Khai báo các trường phân phòng trao đổi qua API.
    class Meta:
        model = RoomAssignment
        fields = [
            "id",
            "student_id",
            "student_name",
            "room_id",
            "start_date",
            "end_date",
            "is_active",
        ]
        read_only_fields = ["id"]

    def get_is_active(self, obj):
        return obj.end_date is None

    def create(self, validated_data):
        return assign_room(
            student=validated_data["student"],
            room=validated_data["room"],
            start_date=validated_data["start_date"],
            end_date=validated_data.get("end_date"),
        )


# Nhận ngày rời phòng; nếu bỏ trống thì lấy ngày hôm nay.
class RoomAssignmentEndSerializer(serializers.Serializer):
    end_date = serializers.DateField(required=False)