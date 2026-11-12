from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.rooms.models import Room, RoomAssignment, RoomType
from apps.rooms.services import assign_room
from apps.students.models import Student


# Kiểm tra dữ liệu loại phòng.
class RoomTypeSerializer(serializers.ModelSerializer):
    # Khai báo các trường loại phòng trao đổi qua API.
    class Meta:
        model = RoomType
        fields = ["id", "name", "monthly_price", "max_occupants"]
        read_only_fields = ["id"]

    def validate_monthly_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Đơn giá không được âm.")
        return value

    def validate_max_occupants(self, value):
        if value < 1:
            raise serializers.ValidationError("Số người tối đa phải lớn hơn 0.")
        return value


# Hiển thị phòng kèm đơn giá, sức chứa và số người đang ở.
class RoomSerializer(serializers.ModelSerializer):
    room_id = serializers.CharField(
        max_length=15,
        validators=[
            UniqueValidator(
                queryset=Room.objects.all(), message="Số phòng đã tồn tại."
            )
        ],
    )
    room_type_id = serializers.PrimaryKeyRelatedField(
        source="room_type", queryset=RoomType.objects.all()
    )
    room_type_name = serializers.CharField(source="room_type.name", read_only=True)
    monthly_price = serializers.DecimalField(
        source="room_type.monthly_price",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    max_occupants = serializers.IntegerField(
        source="room_type.max_occupants", read_only=True
    )
    current_occupants = serializers.IntegerField(read_only=True)

    # Khai báo các trường phòng trao đổi qua API.
    class Meta:
        model = Room
        fields = [
            "room_id",
            "name",
            "floor",
            "room_type_id",
            "room_type_name",
            "monthly_price",
            "max_occupants",
            "current_occupants",
        ]

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