from django.db import transaction
from django.db.models import Count
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.invoices.services import refresh_invoice_for_period
from apps.vehicles.models import MonthlyVehicleRegistration, Vehicle, VehicleEvent
from apps.vehicles.serializers import (
    MonthlyVehicleRegistrationSerializer,
    VehicleEventSerializer,
    VehicleSerializer,
)


# Tra cứu danh sách xe có đăng ký vé tháng.
class VehicleListView(generics.ListAPIView):
    serializer_class = VehicleSerializer

    def get_queryset(self):
        queryset = Vehicle.objects.filter(registrations__isnull=False).distinct()
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")
        if month is not None:
            month_value = self._parse_period_value(month, "month")
            if not 1 <= month_value <= 12:
                raise ValidationError({"month": "Tháng phải nằm trong khoảng 1 đến 12."})
            queryset = queryset.filter(registrations__month=month_value)
        if year is not None:
            year_value = self._parse_period_value(year, "year")
            if not 1 <= year_value <= 9999:
                raise ValidationError({"year": "Năm không hợp lệ."})
            queryset = queryset.filter(registrations__year=year_value)
        return queryset

    @staticmethod
    def _parse_period_value(value, parameter):
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError({parameter: "Giá trị phải là số nguyên."}) from exc


# Tra cứu đăng ký theo sinh viên, tháng và năm.
class MonthlyVehicleRegistrationListCreateView(generics.ListCreateAPIView):
    serializer_class = MonthlyVehicleRegistrationSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        registration = serializer.save()
        refresh_invoice_for_period(
            student=registration.student,
            month=registration.month,
            year=registration.year,
            use_assignment_room=True,
        )

    def get_queryset(self):
        queryset = MonthlyVehicleRegistration.objects.select_related(
            "student",
            "vehicle",
        )
        student_id = self.request.query_params.get("student_id")
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if month is not None:
            month_value = VehicleListView._parse_period_value(month, "month")
            if not 1 <= month_value <= 12:
                raise ValidationError({"month": "Tháng phải nằm trong khoảng 1 đến 12."})
            queryset = queryset.filter(month=month_value)
        if year is not None:
            year_value = VehicleListView._parse_period_value(year, "year")
            if not 1 <= year_value <= 9999:
                raise ValidationError({"year": "Năm không hợp lệ."})
            queryset = queryset.filter(year=year_value)
        return queryset


# Ghi nhận lượt gửi hoặc lấy thuộc một đăng ký vé tháng.
class VehicleEventCreateView(generics.CreateAPIView):
    serializer_class = VehicleEventSerializer

    def get_queryset(self):
        return VehicleEvent.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        registration_id = self.kwargs["registration_id"]
        if not MonthlyVehicleRegistration.objects.filter(pk=registration_id).exists():
            raise ValidationError({"registration_id": "Không tìm thấy đăng ký vé tháng."})
        context["registration_id"] = registration_id
        return context


# Báo cáo số xe đăng ký của mỗi sinh viên trong kỳ để rà soát giới hạn SRS.
class VehicleRegistrationLimitReportView(APIView):
    def get(self, request):
        month = VehicleListView._parse_period_value(
            request.query_params.get("month"), "month"
        )
        year = VehicleListView._parse_period_value(
            request.query_params.get("year"), "year"
        )
        if not 1 <= month <= 12:
            raise ValidationError({"month": "Tháng phải nằm trong khoảng 1 đến 12."})
        if not 1 <= year <= 9999:
            raise ValidationError({"year": "Năm không hợp lệ."})

        # Nhóm theo sinh viên để phát hiện trường hợp vượt giới hạn 2 xe/kỳ.
        rows = (
            MonthlyVehicleRegistration.objects.filter(month=month, year=year)
            .values("student_id", "student__name")
            .annotate(registration_count=Count("id"))
            .order_by("student__name", "student_id")
        )
        return Response(
            [
                {
                    "student_id": row["student_id"],
                    "student_name": row["student__name"],
                    "registration_count": row["registration_count"],
                    "within_limit": row["registration_count"] <= 2,
                }
                for row in rows
            ]
        )
