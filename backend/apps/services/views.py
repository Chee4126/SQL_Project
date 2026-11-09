from datetime import date
from decimal import Decimal

from django.db.models import DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.services.models import Service, ServiceUsage
from apps.services.serializers import ServiceSerializer, ServiceUsageSerializer


# Liệt kê danh mục dịch vụ hoặc tạo dịch vụ mới.
class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


# Xem hoặc cập nhật thông tin một dịch vụ.
class ServiceDetailView(generics.RetrieveUpdateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    http_method_names = ["get", "put", "head", "options"]


# Ghi nhận một lần sử dụng dịch vụ của sinh viên.
class ServiceUsageCreateView(generics.CreateAPIView):
    queryset = ServiceUsage.objects.select_related("student", "service")
    serializer_class = ServiceUsageSerializer


# Tổng hợp số lượng và chi phí theo sinh viên, dịch vụ và khoảng ngày.
class ServiceUsageReportView(APIView):
    def get(self, request):
        start_date = self._parse_date(request.query_params.get("date_from"), "date_from")
        end_date = self._parse_date(request.query_params.get("date_to"), "date_to")
        if start_date > end_date:
            raise ValidationError({"date_to": "Phải bằng hoặc sau date_from."})

        amount_expression = F("quantity") * F("applied_price")
        rows = (
            ServiceUsage.objects.filter(used_at__date__range=(start_date, end_date))
            .values(
                "student_id",
                "student__name",
                "service_id",
                "service__name",
            )
            .annotate(
                total_quantity=Sum("quantity"),
                total_amount=Sum(
                    amount_expression,
                    output_field=DecimalField(max_digits=24, decimal_places=2),
                ),
            )
            .order_by("student__name", "service__name")
        )
        return Response(
            [
                {
                    "student_id": row["student_id"],
                    "student_name": row["student__name"],
                    "service_id": row["service_id"],
                    "service_name": row["service__name"],
                    "total_quantity": row["total_quantity"],
                    "total_amount": row["total_amount"],
                }
                for row in rows
            ]
        )

    @staticmethod
    def _parse_date(value, parameter):
        if value is None:
            raise ValidationError({parameter: "Tham số này là bắt buộc (YYYY-MM-DD)."})
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValidationError({parameter: "Ngày không hợp lệ, dùng YYYY-MM-DD."}) from exc


# Tổng hợp số lượng và doanh thu của từng dịch vụ theo tháng.
class ServiceRevenueReportView(APIView):
    def get(self, request):
        year = self._parse_integer(request.query_params.get("year"), "year")
        month = self._parse_integer(request.query_params.get("month"), "month")
        if not 1 <= month <= 12:
            raise ValidationError({"month": "Tháng phải nằm trong khoảng 1 đến 12."})
        if not 1 <= year <= 9999:
            raise ValidationError({"year": "Năm không hợp lệ."})

        revenue_expression = F("usages__quantity") * F("usages__applied_price")
        usage_period = Q(
            usages__used_at__year=year,
            usages__used_at__month=month,
        )
        services = Service.objects.annotate(
            total_quantity=Coalesce(
                Sum(
                    "usages__quantity",
                    filter=usage_period,
                ),
                Value(0),
            ),
            total_revenue=Coalesce(
                Sum(
                    revenue_expression,
                    filter=usage_period,
                    output_field=DecimalField(max_digits=24, decimal_places=2),
                ),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=24, decimal_places=2),
            ),
        )
        return Response(
            [
                {
                    "service_id": service.pk,
                    "service_name": service.name,
                    "unit": service.unit,
                    "total_quantity": service.total_quantity,
                    "total_revenue": service.total_revenue,
                }
                for service in services
            ]
        )

    @staticmethod
    def _parse_integer(value, parameter):
        if value is None:
            raise ValidationError({parameter: "Tham số này là bắt buộc."})
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError({parameter: "Giá trị phải là số nguyên."}) from exc
