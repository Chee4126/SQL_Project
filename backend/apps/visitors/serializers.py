from django.db import transaction
from rest_framework import serializers
from apps.students.models import Student
from apps.visitors.models import Visit, Visitor


def find_visitor_by_name(name, birth_date):
    candidates = [
        visitor
        for visitor in Visitor.objects.filter(name__iexact=name)
        if visitor.name.strip().casefold() == name.casefold()
        and (birth_date is None or visitor.birth_date == birth_date)
    ]
    if len(candidates) > 1:
        raise serializers.ValidationError(
            {
                "visitor_identity_number": (
                    "Có nhiều khách trùng họ tên; vui lòng nhập số CMT/CCCD."
                )
            }
        )
    return candidates[0] if candidates else None


# Ghi nhận lượt thăm và kiểm tra khách chưa có lượt thăm nào đang mở.
class VisitSerializer(serializers.ModelSerializer):
    visitor_id = serializers.PrimaryKeyRelatedField(
        source="visitor", queryset=Visitor.objects.all(), required=False
    )
    visitor_name = serializers.CharField(source="visitor.name", read_only=True)
    visitor_name_input = serializers.CharField(
        write_only=True,
        required=False,
        max_length=100,
    )
    visitor_identity_number = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=20,
    )
    visitor_birth_date = serializers.DateField(
        write_only=True,
        required=False,
        allow_null=True,
    )
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
            "visitor_name_input",
            "visitor_identity_number",
            "visitor_birth_date",
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
        visitor_name = attrs.get("visitor_name_input", "").strip()
        identity_number = attrs.get("visitor_identity_number")
        identity_number = identity_number.strip() if identity_number else None
        if visitor is None and not visitor_name:
            raise serializers.ValidationError(
                {"visitor_name_input": "Họ tên khách không được để trống."}
            )
        if visitor is not None and (visitor_name or identity_number):
            raise serializers.ValidationError(
                {"visitor_id": "Chỉ nhập mã khách hoặc thông tin khách mới."}
            )
        attrs["visitor_name_input"] = visitor_name
        attrs["visitor_identity_number"] = identity_number
        if visitor is None and identity_number:
            visitor = Visitor.objects.filter(identity_number=identity_number).first()
            if visitor and visitor.name.strip().casefold() != visitor_name.casefold():
                raise serializers.ValidationError(
                    {
                        "visitor_name_input": (
                            "Số CMT/CCCD này đã thuộc hồ sơ khách có họ tên khác."
                        )
                    }
                )
        elif visitor is None:
            visitor = find_visitor_by_name(
                visitor_name,
                attrs.get("visitor_birth_date"),
            )
        attrs["visitor"] = visitor
        if visitor and Visit.objects.filter(
            visitor=visitor,
            left_at__isnull=True,
        ).exists():
            raise serializers.ValidationError(
                {"visitor_id": "Khách này đang có lượt thăm chưa ghi nhận rời đi."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        visitor = validated_data.pop("visitor", None)
        visitor_name = validated_data.pop("visitor_name_input", "")
        identity_number = validated_data.pop("visitor_identity_number", None)
        birth_date = validated_data.pop("visitor_birth_date", None)
        if visitor is None:
            if not identity_number:
                visitor = find_visitor_by_name(visitor_name, birth_date)
            if visitor is None:
                defaults = {
                    "name": visitor_name,
                    "birth_date": birth_date,
                }
                if identity_number:
                    visitor, _ = Visitor.objects.get_or_create(
                        identity_number=identity_number,
                        defaults=defaults,
                    )
                else:
                    visitor = Visitor.objects.create(**defaults)
            if visitor.name.strip().casefold() != visitor_name.casefold():
                raise serializers.ValidationError(
                    {
                        "visitor_name_input": (
                            "Số CMT/CCCD này đã thuộc hồ sơ khách có họ tên khác."
                        )
                    }
                )
        if Visit.objects.filter(visitor=visitor, left_at__isnull=True).exists():
            raise serializers.ValidationError(
                {
                    "visitor_name_input": (
                        "Khách này đang có lượt thăm chưa ghi nhận rời đi."
                    )
                }
            )
        return Visit.objects.create(visitor=visitor, **validated_data)