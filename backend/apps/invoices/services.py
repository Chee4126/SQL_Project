from datetime import date
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import DecimalField, F, Q, Sum
from rest_framework import serializers, status
from rest_framework.exceptions import APIException

from apps.invoices.models import Invoice, InvoiceServiceLine
from apps.rooms.models import RoomAssignment
from apps.services.models import ServiceUsage
from apps.students.models import Student
from apps.vehicles.models import MonthlyVehicleRegistration


class InvoiceConflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Không thể tạo hoặc cập nhật hóa đơn ở trạng thái hiện tại."
    default_code = "invoice_conflict"


def refresh_invoice_for_period(
    student,
    month,
    year,
    *,
    room_amount=None,
    use_assignment_room=False,
):
    try:
        with transaction.atomic():
            student = Student.objects.select_for_update().get(pk=student.pk)
            invoice = (
                Invoice.objects.select_for_update()
                .filter(student=student, month=month, year=year)
                .first()
            )
            if invoice and invoice.status == Invoice.PaymentStatus.PAID:
                raise InvoiceConflict(
                    "Hóa đơn đã thanh toán; không thể ghi nhận thêm khoản thu trong kỳ."
                )

            if use_assignment_room:
                room_total = _room_total(student, month, year)
            elif room_amount is not None:
                room_total = room_amount
            elif invoice is not None:
                room_total = invoice.room_amount
            else:
                raise serializers.ValidationError(
                    {"room_amount": "Cần nhập tiền phòng khi lập hóa đơn lần đầu."}
                )

            service_rows = list(
                ServiceUsage.objects.filter(
                    student=student,
                    used_at__year=year,
                    used_at__month=month,
                )
                .values(
                    "service_id",
                    "service__name",
                    "service__unit",
                    "applied_price",
                )
                .annotate(
                    total_quantity=Sum("quantity"),
                    amount=Sum(
                        F("quantity") * F("applied_price"),
                        output_field=DecimalField(
                            max_digits=24,
                            decimal_places=2,
                        ),
                    ),
                )
                .order_by("service__name", "applied_price")
            )
            service_total = sum(
                (row["amount"] or Decimal("0.00") for row in service_rows),
                Decimal("0.00"),
            )
            vehicle_total = (
                MonthlyVehicleRegistration.objects.filter(
                    student=student,
                    month=month,
                    year=year,
                ).aggregate(total=Sum("monthly_price"))["total"]
                or Decimal("0.00")
            )
            amounts = {
                "room_amount": room_total,
                "service_amount": service_total,
                "vehicle_amount": vehicle_total,
                "parking_amount": Decimal("0.00"),
            }
            total = sum(amounts.values(), Decimal("0.00"))

            created = invoice is None
            if created:
                invoice = Invoice(
                    student=student,
                    month=month,
                    year=year,
                    **amounts,
                    total_amount=total,
                )
            else:
                for field, amount in amounts.items():
                    setattr(invoice, field, amount)
                invoice.total_amount = total
            invoice.save()

            invoice.service_lines.all().delete()
            InvoiceServiceLine.objects.bulk_create(
                [
                    InvoiceServiceLine(
                        invoice=invoice,
                        service_id=row["service_id"],
                        service_name=row["service__name"],
                        unit=row["service__unit"],
                        quantity=row["total_quantity"],
                        applied_price=row["applied_price"],
                        amount=row["amount"],
                    )
                    for row in service_rows
                ]
            )
            return invoice, created
    except IntegrityError as exc:
        raise InvoiceConflict(
            "Hóa đơn cho sinh viên và kỳ này vừa được tạo ở yêu cầu khác."
        ) from exc


def _room_total(student, month, year):
    period_start = date(year, month, 1)
    period_end = (
        date(year + 1, 1, 1)
        if month == 12 and year < 9999
        else date(year, month + 1, 1)
        if month < 12
        else None
    )
    assignments = RoomAssignment.objects.filter(student=student)
    if period_end is not None:
        assignments = assignments.filter(start_date__lt=period_end)
    assignments = assignments.filter(
        (Q(end_date__isnull=True) | Q(end_date__gt=period_start))
        & (Q(end_date__isnull=True) | Q(end_date__gt=F("start_date")))
    ).select_related("room")
    return sum(
        (assignment.room.monthly_price for assignment in assignments),
        Decimal("0.00"),
    )
