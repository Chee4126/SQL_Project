from datetime import date
from decimal import Decimal

from django.db.models import DecimalField, F, Q, Sum
from django.db import migrations
from django.utils import timezone


def create_invoices_for_existing_charges(apps, schema_editor):
    Invoice = apps.get_model("invoices", "Invoice")
    InvoiceServiceLine = apps.get_model("invoices", "InvoiceServiceLine")
    RoomAssignment = apps.get_model("rooms", "RoomAssignment")
    ServiceUsage = apps.get_model("services", "ServiceUsage")
    MonthlyVehicleRegistration = apps.get_model(
        "vehicles",
        "MonthlyVehicleRegistration",
    )
    database = schema_editor.connection.alias
    periods = set()

    assignments = RoomAssignment.objects.using(database).select_related("room")
    today = timezone.localdate()
    for assignment in assignments.iterator():
        periods.add(
            (
                assignment.student_id,
                assignment.start_date.month,
                assignment.start_date.year,
            )
        )
        if (
            assignment.start_date <= today
            and (assignment.end_date is None or assignment.end_date > today)
        ):
            periods.add((assignment.student_id, today.month, today.year))

    periods.update(
        ServiceUsage.objects.using(database)
        .values_list("student_id", "used_at__month", "used_at__year")
        .distinct()
    )
    periods.update(
        MonthlyVehicleRegistration.objects.using(database)
        .values_list("student_id", "month", "year")
        .distinct()
    )

    for student_id, month, year in sorted(periods):
        if Invoice.objects.using(database).filter(
            student_id=student_id,
            month=month,
            year=year,
        ).exists():
            continue

        period_start = date(year, month, 1)
        period_end = (
            date(year + 1, 1, 1)
            if month == 12 and year < 9999
            else date(year, month + 1, 1)
            if month < 12
            else None
        )
        assignments = RoomAssignment.objects.using(database).filter(
            student_id=student_id,
        )
        if period_end is not None:
            assignments = assignments.filter(start_date__lt=period_end)
        assignments = assignments.filter(
            (Q(end_date__isnull=True) | Q(end_date__gt=period_start))
            & (Q(end_date__isnull=True) | Q(end_date__gt=F("start_date")))
        ).select_related("room")
        room_amount = sum(
            (assignment.room.monthly_price for assignment in assignments),
            Decimal("0.00"),
        )

        service_rows = (
            ServiceUsage.objects.using(database)
            .filter(
                student_id=student_id,
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
                    output_field=DecimalField(max_digits=24, decimal_places=2),
                ),
            )
        )
        service_rows = list(service_rows)
        service_amount = sum(
            (row["amount"] or Decimal("0.00") for row in service_rows),
            Decimal("0.00"),
        )
        vehicle_amount = (
            MonthlyVehicleRegistration.objects.using(database)
            .filter(student_id=student_id, month=month, year=year)
            .aggregate(total=Sum("monthly_price"))["total"]
            or Decimal("0.00")
        )
        invoice = Invoice.objects.using(database).create(
            student_id=student_id,
            month=month,
            year=year,
            room_amount=room_amount,
            service_amount=service_amount,
            vehicle_amount=vehicle_amount,
            parking_amount=Decimal("0.00"),
            total_amount=room_amount + service_amount + vehicle_amount,
        )
        InvoiceServiceLine.objects.using(database).bulk_create(
            [
                InvoiceServiceLine(
                    invoice_id=invoice.pk,
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


class Migration(migrations.Migration):

    dependencies = [
        ("invoices", "0002_invoiceserviceline"),
        ("rooms", "0002_remove_room_room_price_nonnegative_and_more"),
        ("services", "0001_initial"),
        ("vehicles", "0002_alter_vehicleevent_fee_alter_vehicleevent_is_free"),
    ]

    operations = [
        migrations.RunPython(
            create_invoices_for_existing_charges,
            migrations.RunPython.noop,
        ),
    ]
