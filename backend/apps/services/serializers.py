from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.services.models import Service, ServiceUsage
from apps.students.models import Student


# Chuyển đổi và kiểm tra dữ liệu danh mục dịch vụ.
class ServiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    # Khai báo các trường dịch vụ được phép trao đổi qua API.
    class Meta:
        model = Service
        fields = ["id", "name", "price", "unit"]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Đơn giá không được âm.")
        return value


# Kiểm tra dữ liệu sử dụng và lưu đơn giá tại thời điểm ghi nhận.
class ServiceUsageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        source="student",
        queryset=Student.objects.all(),
    )
    service_id = serializers.PrimaryKeyRelatedField(
        source="service",
        queryset=Service.objects.all(),
    )
    applied_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    amount = serializers.DecimalField(
        max_digits=24,
        decimal_places=2,
        read_only=True,
    )

    # Khai báo dữ liệu sử dụng dịch vụ được trao đổi qua API.
    class Meta:
        model = ServiceUsage
        fields = [
            "id",
            "student_id",
            "service_id",
            "used_at",
            "quantity",
            "applied_price",
            "amount",
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Số lượng phải lớn hơn 0.")
        return value

    def validate_used_at(self, value):
        if timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return value

    @transaction.atomic
    def create(self, validated_data):
        service = Service.objects.select_for_update().get(
            pk=validated_data["service"].pk
        )
        return ServiceUsage.objects.create(
            **validated_data,
            applied_price=service.price,
        )
