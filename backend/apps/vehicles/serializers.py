from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers

from apps.students.models import Student
from apps.vehicles.models import (
    MonthlyVehicleRegistration,
    Vehicle,
    VehicleEvent,
)


# Hiển thị xe đã có ít nhất một đăng ký vé tháng.
class VehicleSerializer(serializers.ModelSerializer):
    plate_number = serializers.CharField(source="pk", read_only=True)

    # Khai báo các trường xe trả về qua API.
    class Meta:
        model = Vehicle
        fields = ["plate_number", "vehicle_type"]


# Kiểm tra đăng ký và giới hạn tối đa hai xe mỗi sinh viên trong kỳ.
class MonthlyVehicleRegistrationSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(
        source="student",
        queryset=Student.objects.all(),
    )
    student_name = serializers.CharField(source="student.name", read_only=True)
    plate_number = serializers.CharField(
        source="vehicle_id",
        max_length=20,
        write_only=True,
    )
    vehicle_type = serializers.CharField(max_length=50, write_only=True)
    vehicle = VehicleSerializer(read_only=True)
    monthly_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    # Khai báo các trường đăng ký vé tháng trao đổi qua API.
    class Meta:
        model = MonthlyVehicleRegistration
        fields = [
            "id",
            "student_id",
            "student_name",
            "plate_number",
            "vehicle_type",
            "vehicle",
            "month",
            "year",
            "monthly_price",
        ]
        read_only_fields = ["id"]

    def validate_month(self, value):
        if not 1 <= value <= 12:
            raise serializers.ValidationError("Tháng phải nằm trong khoảng 1 đến 12.")
        return value

    def validate_year(self, value):
        if not 1 <= value <= 9999:
            raise serializers.ValidationError("Năm không hợp lệ.")
        return value

    def validate(self, attrs):
        plate_number = attrs.get("vehicle_id", "").strip()
        if not plate_number:
            raise serializers.ValidationError(
                {"plate_number": "Biển số xe không được để trống."}
            )
        attrs["vehicle_id"] = plate_number
        student = attrs.get("student")
        month = attrs.get("month")
        year = attrs.get("year")
        if student and month and year:
            if MonthlyVehicleRegistration.objects.filter(
                student=student,
                vehicle_id=plate_number,
                month=month,
                year=year,
            ).exists():
                raise serializers.ValidationError(
                    {"plate_number": "Xe này đã được đăng ký cho sinh viên trong kỳ."}
                )
            if MonthlyVehicleRegistration.objects.filter(
                vehicle_id=plate_number,
                month=month,
                year=year,
            ).exists():
                raise serializers.ValidationError(
                    {"plate_number": "Xe này đã được đăng ký trong kỳ."}
                )
        return attrs

    def create(self, validated_data):
        try:
            with transaction.atomic():
                student = Student.objects.select_for_update().get(
                    pk=validated_data["student"].pk
                )
                month = validated_data["month"]
                year = validated_data["year"]
                if MonthlyVehicleRegistration.objects.filter(
                    student=student,
                    month=month,
                    year=year,
                ).count() >= 2:
                    raise serializers.ValidationError(
                        {
                            "student_id": (
                                "Sinh viên chỉ được đăng ký tối đa 2 xe mỗi tháng."
                            )
                        }
                    )

                vehicle_id = validated_data.pop("vehicle_id")
                vehicle_type = validated_data.pop("vehicle_type").strip()
                if not vehicle_type:
                    raise serializers.ValidationError(
                        {"vehicle_type": "Loại xe không được để trống."}
                    )
                vehicle, created = Vehicle.objects.get_or_create(
                    pk=vehicle_id,
                    defaults={"vehicle_type": vehicle_type},
                )
                if not created and vehicle.vehicle_type != vehicle_type:
                    raise serializers.ValidationError(
                        {
                            "vehicle_type": (
                                "Biển số này đã được đăng ký với loại xe khác."
                            )
                        }
                    )
                validated_data.pop("student")
                return MonthlyVehicleRegistration.objects.create(
                    **validated_data,
                    student=student,
                    vehicle=vehicle,
                )
        except serializers.ValidationError:
            raise
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {"plate_number": "Biển số xe đã được đăng ký trong kỳ này."}
            ) from exc


# Ghi nhận lượt gửi/lấy thuộc một đăng ký vé tháng.
class VehicleEventSerializer(serializers.ModelSerializer):
    registration_id = serializers.IntegerField(read_only=True)

    # Khai báo dữ liệu lượt gửi/lấy được trả về qua API.
    class Meta:
        model = VehicleEvent
        fields = [
            "id",
            "registration_id",
            "event_at",
            "event_type",
        ]
        read_only_fields = ["id"]

    def validate_event_at(self, value):
        if timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return value

    def create(self, validated_data):
        registration = MonthlyVehicleRegistration.objects.get(
            pk=self.context["registration_id"],
        )
        event_at = validated_data["event_at"]
        local_event_at = timezone.localtime(event_at)
        if (local_event_at.year, local_event_at.month) != (
            registration.year,
            registration.month,
        ):
            raise serializers.ValidationError(
                {"event_at": "Thời điểm phải thuộc kỳ đăng ký vé tháng."}
            )
        return VehicleEvent.objects.create(
            **validated_data,
            registration=registration,
        )
