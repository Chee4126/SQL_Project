from datetime import date, datetime, timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.invoices.models import Invoice
from apps.rooms.models import Room, RoomAssignment
from apps.services.models import Service, ServiceUsage
from apps.students.models import Student
from apps.vehicles.models import MonthlyVehicleRegistration, Vehicle, VehicleEvent


# Kiểm tra tổng hợp từng khoản và các ràng buộc lập hóa đơn theo SRS.
class InvoiceApiTests(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="staff", password="test-pass")
        self.client.force_authenticate(user=user)
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
        self.assertEqual(Decimal(response.data["parking_amount"]), Decimal("0.00"))
        self.assertEqual(Decimal(response.data["total_amount"]), Decimal("630000.00"))
        self.assertEqual(response.data["status"], Invoice.PaymentStatus.UNPAID)
        self.assertEqual(len(response.data["service_lines"]), 1)
        service_line = response.data["service_lines"][0]
        self.assertEqual(service_line["service_id"], service.pk)
        self.assertEqual(service_line["service_name"], "Giặt là")
        self.assertEqual(service_line["unit"], "kg")
        self.assertEqual(service_line["quantity"], 2)
        self.assertEqual(Decimal(service_line["applied_price"]), Decimal("15000.00"))
        self.assertEqual(Decimal(service_line["amount"]), Decimal("30000.00"))

    def test_room_service_and_vehicle_registrations_update_one_invoice(self):
        room = Room.objects.create(
            room_id="P110",
            name="Phòng 110",
            monthly_price=Decimal("1800000.00"),
            max_occupants=4,
        )
        assignment = self.client.post(
            "/api/room-assignments",
            {
                "student_id": self.student.pk,
                "room_id": room.pk,
                "start_date": "2026-11-06",
            },
            format="json",
        )
        service = Service.objects.create(
            name="Giặt là",
            price=Decimal("15000.00"),
            unit="kg",
        )
        usage = self.client.post(
            "/api/service-usages",
            {
                "student_id": self.student.pk,
                "service_id": service.pk,
                "used_at": "2026-11-07T09:00:00Z",
                "quantity": 2,
            },
            format="json",
        )
        registration = self.client.post(
            "/api/monthly-vehicle-registrations",
            {
                "student_id": self.student.pk,
                "plate_number": "51A-11000",
                "vehicle_type": "Xe máy",
                "month": 11,
                "year": 2026,
            },
            format="json",
        )

        self.assertEqual(assignment.status_code, 201, assignment.data)
        self.assertEqual(usage.status_code, 201, usage.data)
        self.assertEqual(registration.status_code, 201, registration.data)
        invoice = Invoice.objects.get(
            student=self.student,
            month=11,
            year=2026,
        )
        self.assertEqual(invoice.room_amount, Decimal("1800000.00"))
        self.assertEqual(invoice.service_amount, Decimal("30000.00"))
        self.assertEqual(invoice.vehicle_amount, Decimal("100000.00"))
        self.assertEqual(invoice.total_amount, Decimal("1930000.00"))
        self.assertEqual(invoice.service_lines.get().amount, Decimal("30000.00"))
        self.assertEqual(Invoice.objects.count(), 1)

    def test_regeneration_updates_unpaid_invoice_and_keeps_room_amount(self):
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
        first = self.generate()
        ServiceUsage.objects.create(
            student=self.student,
            service=service,
            used_at=datetime(2026, 11, 7, 9, tzinfo=timezone.utc),
            quantity=1,
            applied_price=Decimal("15000.00"),
        )
        second = self.generate()

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data["id"], second.data["id"])
        self.assertEqual(Decimal(second.data["room_amount"]), Decimal("500000.00"))
        self.assertEqual(first.data["service_lines"][0]["quantity"], 2)
        self.assertEqual(second.data["service_lines"][0]["quantity"], 3)
        self.assertEqual(Decimal(second.data["service_lines"][0]["amount"]), Decimal("45000.00"))
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

    def test_monthly_student_cost_report_sums_residents_without_invoices(self):
        second_student = Student.objects.create(
            student_id="SV002",
            name="Tran Binh",
        )
        first_room = Room.objects.create(
            room_id="P101",
            name="Phòng 101",
            monthly_price=Decimal("1800000.00"),
            max_occupants=4,
        )
        second_room = Room.objects.create(
            room_id="P102",
            name="Phòng 102",
            monthly_price=Decimal("250000.00"),
            max_occupants=8,
        )
        RoomAssignment.objects.create(
            student=self.student,
            room=first_room,
            start_date=date(2026, 11, 6),
        )
        RoomAssignment.objects.create(
            student=self.student,
            room=first_room,
            start_date=date(2026, 11, 6),
            end_date=date(2026, 11, 6),
        )
        RoomAssignment.objects.create(
            student=second_student,
            room=second_room,
            start_date=date(2026, 10, 31),
            end_date=date(2026, 11, 1),
        )
        RoomAssignment.objects.create(
            student=second_student,
            room=second_room,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 12, 1),
        )
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
        MonthlyVehicleRegistration.objects.create(
            student=self.student,
            vehicle=Vehicle.objects.create(
                plate_number="51A-12345",
                vehicle_type="Xe máy",
            ),
            month=11,
            year=2026,
            monthly_price=Decimal("100000.00"),
        )
        response = self.client.get(
            "/api/reports/monthly-student-costs",
            {"month": 11, "year": 2026},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [row["student_id"] for row in response.data],
            ["SV001", "SV002"],
        )
        self.assertEqual(
            Decimal(response.data[0]["total_amount"]),
            Decimal("1930000.00"),
        )
        self.assertEqual(Decimal(response.data[0]["room_amount"]), Decimal("1800000.00"))
        self.assertEqual(Decimal(response.data[0]["service_amount"]), Decimal("30000.00"))
        self.assertEqual(Decimal(response.data[0]["vehicle_amount"]), Decimal("100000.00"))
        self.assertEqual(Decimal(response.data[1]["total_amount"]), Decimal("250000.00"))
        self.assertNotIn("status", response.data[0])

    def test_monthly_student_cost_report_excludes_residents_outside_period(self):
        room = Room.objects.create(
            room_id="P103",
            name="Phòng 103",
            monthly_price=Decimal("1800000.00"),
            max_occupants=4,
        )
        RoomAssignment.objects.create(
            student=self.student,
            room=room,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 11, 1),
        )

        response = self.client.get(
            "/api/reports/monthly-student-costs",
            {"month": 11, "year": 2026},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

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
