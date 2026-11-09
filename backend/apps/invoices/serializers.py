from rest_framework import serializers

from apps.invoices.models import Invoice
from apps.students.models import Student


# Hiển thị hóa đơn cùng tên sinh viên, không cho client sửa các khoản tiền.
class InvoiceSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(read_only=True)
    student_name = serializers.CharField(source="student.name", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "student_id",
            "student_name",
            "month",
            "year",
            "room_amount",
            "service_amount",
            "vehicle_amount",
            "parking_amount",
            "total_amount",
            "status",
        ]


# Nhận kỳ lập hóa đơn và khoản tiền phòng do quản lý nhập.
class InvoiceGenerationSerializer(serializers.Serializer):
    student_id = serializers.PrimaryKeyRelatedField(
        source="student",
        queryset=Student.objects.all(),
    )
    month = serializers.IntegerField(min_value=1, max_value=12)
    year = serializers.IntegerField(min_value=1, max_value=9999)
    room_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        required=False,
    )


# Trạng thái thanh toán là trường duy nhất được cập nhật riêng.
class InvoiceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ["status"]
