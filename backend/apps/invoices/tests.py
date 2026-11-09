from datetime import datetime, timezone
from decimal import Decimal

from rest_framework.test import APITestCase

from apps.invoices.models import Invoice
from apps.services.models import Service, ServiceUsage
from apps.students.models import Student
from apps.vehicles.models import MonthlyVehicleRegistration, Vehicle, VehicleEvent


# Kiểm tra tổng hợp từng khoản và các ràng buộc lập hóa đơn theo SRS.
class InvoiceApiTests(APITestCase):
    def setUp(self):
        self.student = Student.objects.create(student_id="SV001", name="Nguyen An")

    def generate(self, **overrides):
        payload = {
            "student_id": self.student.pk,
            "month": 11,
            "year": 2026,
            "room_amount": "500000.00",
        }
        payload.update(overrides)
        return self.client.post("/api/invoices/generate", payload, format="json")

    def test_generate_invoice_sums_all_monthly_charges(self):
        service = Service.objects.create(
            name="Giặt là",
            price=Decimal("15000.00"),
            unit="kg",
        )
        ServiceUsage.objects.create(
            student=self.student,
            service=service,
            used_at=datetime(2026, 11, 6, 9, tzinfo=timezone.utc),
            quantity=2,
            applied_price=Decimal("15000.00"),
        )
        registration = MonthlyVehicleRegistration.objects.create(
            student=self.student,
            vehicle=Vehicle.objects.create(
                plate_number="51A-12345",
                vehicle_type="Xe máy",
            ),
            month=11,
            year=2026,
            monthly_price=Decimal("100000.00"),
        )
        VehicleEvent.objects.create(
            registration=registration,
            event_at=datetime(2026, 11, 6, 9, tzinfo=timezone.utc),
            event_type=VehicleEvent.EventType.PARK,
            is_free=False,
            fee=Decimal("3000.00"),
        )

        response = self.generate()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Decimal(response.data["room_amount"]), Decimal("500000.00"))
        self.assertEqual(Decimal(response.data["service_amount"]), Decimal("30000.00"))
        self.assertEqual(Decimal(response.data["vehicle_amount"]), Decimal("100000.00"))
        self.assertEqual(Decimal(response.data["parking_amount"]), Decimal("3000.00"))
        self.assertEqual(Decimal(response.data["total_amount"]), Decimal("633000.00"))
        self.assertEqual(response.data["status"], Invoice.PaymentStatus.UNPAID)

    def test_regeneration_updates_unpaid_invoice_and_keeps_room_amount(self):
        first = self.generate()
        second = self.generate()

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data["id"], second.data["id"])
        self.assertEqual(Decimal(second.data["room_amount"]), Decimal("500000.00"))
        self.assertEqual(Invoice.objects.count(), 1)

    def test_paid_invoice_cannot_be_regenerated(self):
        response = self.generate()
        invoice = Invoice.objects.get(pk=response.data["id"])
        invoice.status = Invoice.PaymentStatus.PAID
        invoice.save()

        response = self.generate()

        self.assertEqual(response.status_code, 409)

    def test_invalid_period_and_negative_room_amount_are_rejected(self):
        invalid_month = self.generate(month=13)
        negative_room = self.generate(room_amount="-1.00")
        missing_room = self.client.post(
            "/api/invoices/generate",
            {"student_id": self.student.pk, "month": 11, "year": 2026},
            format="json",
        )

        self.assertEqual(invalid_month.status_code, 400)
        self.assertEqual(negative_room.status_code, 400)
        self.assertEqual(missing_room.status_code, 400)
        self.assertEqual(Invoice.objects.count(), 0)

    def test_list_filters_and_payment_status_update(self):
        response = self.generate()
        invoice_id = response.data["id"]
        update_response = self.client.patch(
            f"/api/invoices/{invoice_id}/status",
            {"status": Invoice.PaymentStatus.PAID},
            format="json",
        )
        filtered_response = self.client.get(
            "/api/invoices",
            {"month": 11, "year": 2026, "status": Invoice.PaymentStatus.PAID},
        )

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(filtered_response.status_code, 200)
        self.assertEqual(len(filtered_response.data), 1)
        self.assertEqual(
            filtered_response.data[0]["status"],
            Invoice.PaymentStatus.PAID,
        )

    def test_unknown_student_is_rejected(self):
        response = self.generate(student_id="NOT-FOUND")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Invoice.objects.count(), 0)

    def test_monthly_student_cost_report_is_sorted_and_filtered(self):
        second_student = Student.objects.create(
            student_id="SV002",
            name="Tran Binh",
        )
        first_invoice = self.generate()
        second_invoice = self.client.post(
            "/api/invoices/generate",
            {
                "student_id": second_student.pk,
                "month": 11,
                "year": 2026,
                "room_amount": "300000.00",
            },
            format="json",
        )
        response = self.client.get(
            "/api/reports/monthly-student-costs",
            {"month": 11, "year": 2026},
        )

        self.assertEqual(first_invoice.status_code, 201)
        self.assertEqual(second_invoice.status_code, 201)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [row["student_id"] for row in response.data],
            ["SV001", "SV002"],
        )
        self.assertEqual(
            Decimal(response.data[0]["total_amount"]),
            Decimal("500000.00"),
        )

    def test_monthly_student_cost_report_requires_valid_period(self):
        missing_month = self.client.get(
            "/api/reports/monthly-student-costs",
            {"year": 2026},
        )
        invalid_month = self.client.get(
            "/api/reports/monthly-student-costs",
            {"month": 13, "year": 2026},
        )

        self.assertEqual(missing_month.status_code, 400)
        self.assertEqual(invalid_month.status_code, 400)
