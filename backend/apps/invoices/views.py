from datetime import date
from decimal import Decimal

from django.db.models import DecimalField, F, Q, Sum
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.invoices.models import Invoice
from apps.invoices.serializers import (
    InvoiceGenerationSerializer,
    InvoiceSerializer,
    InvoiceStatusSerializer,
)
from apps.invoices.services import refresh_invoice_for_period
from apps.rooms.models import RoomAssignment
from apps.students.models import Student
from apps.services.models import ServiceUsage
from apps.vehicles.models import MonthlyVehicleRegistration


# Tạo hóa đơn từ các giao dịch đã lưu; tiền phòng có thể nhập thủ công.
class InvoiceGenerateView(APIView):
    def post(self, request):
        request_serializer = InvoiceGenerationSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        values = request_serializer.validated_data
        invoice, created = refresh_invoice_for_period(
            student=values["student"],
            month=values["month"],
            year=values["year"],
            room_amount=values.get("room_amount"),
        )
        return Response(
            InvoiceSerializer(invoice).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


# Tra cứu hóa đơn theo sinh viên, kỳ và tình trạng thanh toán.
class InvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        queryset = Invoice.objects.select_related("student").prefetch_related(
            "service_lines"
        )
        for field in ("month", "year"):
            value = self.request.query_params.get(field)
            if value is not None:
                try:
                    number = int(value)
                except ValueError as exc:
                    raise serializers.ValidationError(
                        {field: "Giá trị phải là số nguyên."}
                    ) from exc
                lower_bound, upper_bound = (1, 12) if field == "month" else (1, 9999)
                if not lower_bound <= number <= upper_bound:
                    raise serializers.ValidationError({field: "Giá trị không hợp lệ."})
                queryset = queryset.filter(**{field: number})

        student_id = self.request.query_params.get("student_id")
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        payment_status = self.request.query_params.get("status")
        if payment_status:
            if payment_status not in Invoice.PaymentStatus.values:
                raise serializers.ValidationError({"status": "Trạng thái không hợp lệ."})
            queryset = queryset.filter(status=payment_status)
        return queryset


# Trả về chi tiết một hóa đơn theo mã.
class InvoiceDetailView(generics.RetrieveAPIView):
    queryset = Invoice.objects.select_related("student").prefetch_related(
        "service_lines"
    )
    serializer_class = InvoiceSerializer


# Chỉ cập nhật tình trạng thanh toán, không cho sửa số tiền trực tiếp.
class InvoiceStatusUpdateView(generics.UpdateAPIView):
    queryset = Invoice.objects.select_related("student")
    serializer_class = InvoiceStatusSerializer
    http_method_names = ["patch", "options", "head"]


# Báo cáo chi phí theo sinh viên nội trú trong tháng, không phụ thuộc hóa đơn.
class MonthlyStudentCostReportView(APIView):
    def get(self, request):
        month = self._parse_period_value(request.query_params.get("month"), "month")
        year = self._parse_period_value(request.query_params.get("year"), "year")
        if not 1 <= month <= 12:
            raise serializers.ValidationError(
                {"month": "Tháng phải nằm trong khoảng 1 đến 12."}
            )
        if not 1 <= year <= 9999:
            raise serializers.ValidationError({"year": "Năm không hợp lệ."})

        period_start = date(year, month, 1)
        period_end = (
            date(year + 1, 1, 1)
            if month == 12 and year < 9999
            else date(year, month + 1, 1)
            if month < 12
            else None
        )

        costs = {}
        assignments = RoomAssignment.objects.all()
        if period_end is not None:
            assignments = assignments.filter(start_date__lt=period_end)
        assignments = assignments.filter(
            (Q(end_date__isnull=True) | Q(end_date__gt=period_start))
            & (Q(end_date__isnull=True) | Q(end_date__gt=F("start_date")))
        ).select_related("student", "room")
        for assignment in assignments:
            student_id = assignment.student_id
            if student_id not in costs:
                costs[student_id] = {
                    "student_id": student_id,
                    "student_name": assignment.student.name,
                    "room_amount": Decimal("0.00"),
                    "service_amount": Decimal("0.00"),
                    "vehicle_amount": Decimal("0.00"),
                }
            costs[student_id]["room_amount"] += assignment.room.monthly_price

        service_totals = (
            ServiceUsage.objects.filter(
                used_at__year=year,
                used_at__month=month,
                student_id__in=costs,
            )
            .values("student_id")
            .annotate(
                total=Sum(
                    F("quantity") * F("applied_price"),
                    output_field=DecimalField(max_digits=24, decimal_places=2),
                )
            )
        )
        for row in service_totals:
            costs[row["student_id"]]["service_amount"] = row["total"] or Decimal("0.00")

        vehicle_totals = (
            MonthlyVehicleRegistration.objects.filter(
                month=month,
                year=year,
                student_id__in=costs,
            )
            .values("student_id")
            .annotate(total=Sum("monthly_price"))
        )
        for row in vehicle_totals:
            costs[row["student_id"]]["vehicle_amount"] = (
                row["total"] or Decimal("0.00")
            )

        students = Student.objects.filter(pk__in=costs).order_by("name", "student_id")
        return Response(
            [
                {
                    **costs[student.pk],
                    "total_amount": (
                        costs[student.pk]["room_amount"]
                        + costs[student.pk]["service_amount"]
                        + costs[student.pk]["vehicle_amount"]
                    ),
                }
                for student in students
            ]
        )

    @staticmethod
    def _parse_period_value(value, parameter):
        if value is None:
            raise serializers.ValidationError(
                {parameter: "Tham số này là bắt buộc."}
            )
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise serializers.ValidationError(
                {parameter: "Giá trị phải là số nguyên."}
            ) from exc
