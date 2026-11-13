from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.students.models import Student
from apps.vehicles.models import MonthlyVehicleRegistration, Vehicle, VehicleEvent


# Kiểm tra đăng ký vé tháng, tra cứu xe và ghi nhận lượt gửi/lấy.
class VehicleApiTests(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="staff", password="test-pass")
        self.client.force_authenticate(user=user)
        self.student = Student.objects.create(student_id="SV001", name="Nguyen An")

    def register(self, plate, month=11, year=2026, student_id=None, vehicle_type="Xe máy"):
        return self.client.post(
            "/api/monthly-vehicle-registrations",
            {
                "student_id": student_id or self.student.pk,
                "plate_number": plate,
                "vehicle_type": vehicle_type,
                "month": month,
                "year": year,
            },
            format="json",
        )

    def test_registration_creates_vehicle_at_monthly_price(self):
        response = self.register("51A-12345")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Decimal(response.data["monthly_price"]), Decimal("100000.00"))
        self.assertTrue(
            Vehicle.objects.filter(plate_number="51A-12345", vehicle_type="Xe máy").exists()
        )

    def test_student_cannot_register_more_than_two_vehicles_per_month(self):
        self.assertEqual(self.register("51A-00001").status_code, 201)
        self.assertEqual(self.register("51A-00002").status_code, 201)
        response = self.register("51A-00003")

        self.assertEqual(response.status_code, 400)
        self.assertIn("student_id", response.data)

    def test_vehicle_cannot_be_registered_twice_in_same_period(self):
        self.assertEqual(self.register("51A-10000").status_code, 201)
        response = self.register("51A-10000")

        self.assertEqual(response.status_code, 400)

    def test_registration_lookup_and_vehicle_list(self):
        self.register("51A-22222")

        registrations = self.client.get(
            "/api/monthly-vehicle-registrations",
            {"student_id": self.student.pk, "month": 11, "year": 2026},
        )
        vehicles = self.client.get("/api/vehicles", {"month": 11, "year": 2026})

        self.assertEqual(registrations.status_code, 200)
        self.assertEqual(len(registrations.data), 1)
        self.assertEqual(registrations.data[0]["student_name"], self.student.name)
        self.assertEqual(vehicles.status_code, 200)
        self.assertEqual(vehicles.data[0]["plate_number"], "51A-22222")

    def test_vehicle_events_are_recorded_without_fee_policy(self):
        registration_response = self.register("51A-33333")
        registration_id = registration_response.data["id"]
        event_url = f"/api/monthly-vehicle-registrations/{registration_id}/events"
        for event_type in ["GUI", "LAY", "GUI"]:
            response = self.client.post(
                event_url,
                {
                    "event_at": "2026-11-06T09:00:00+07:00",
                    "event_type": event_type,
                },
                format="json",
            )
            self.assertEqual(response.status_code, 201)
            self.assertNotIn("is_free", response.data)
            self.assertNotIn("fee", response.data)

        self.assertEqual(VehicleEvent.objects.count(), 3)
        self.assertEqual(
            VehicleEvent.objects.filter(is_free__isnull=True, fee__isnull=True).count(),
            3,
        )

    def test_event_rejects_invalid_type_and_unknown_registration(self):
        registration_response = self.register("51A-55555")
        event_url = (
            f"/api/monthly-vehicle-registrations/{registration_response.data['id']}/events"
        )
        invalid_event = self.client.post(
            event_url,
            {"event_at": "2026-11-06T09:00:00+07:00", "event_type": "OTHER"},
            format="json",
        )
        missing_registration = self.client.post(
            "/api/monthly-vehicle-registrations/99999/events",
            {"event_at": "2026-11-06T09:00:00+07:00", "event_type": "GUI"},
            format="json",
        )
        outside_registration_period = self.client.post(
            event_url,
            {"event_at": "2026-12-01T00:00:00+07:00", "event_type": "GUI"},
            format="json",
        )

        self.assertEqual(invalid_event.status_code, 400)
        self.assertEqual(missing_registration.status_code, 400)
        self.assertEqual(outside_registration_period.status_code, 400)

    def test_registration_limit_report_flags_students_over_limit(self):
        other_student = Student.objects.create(student_id="SV002", name="Tran Binh")
        for plate in ("51A-01001", "51A-01002", "51A-01003"):
            MonthlyVehicleRegistration.objects.create(
                student=other_student,
                vehicle=Vehicle.objects.create(
                    plate_number=plate,
                    vehicle_type="Xe máy",
                ),
                month=11,
                year=2026,
            )
        MonthlyVehicleRegistration.objects.create(
            student=self.student,
            vehicle=Vehicle.objects.create(
                plate_number="51A-00001",
                vehicle_type="Xe máy",
            ),
            month=11,
            year=2026,
        )
        response = self.client.get(
            "/api/reports/vehicle-registration-limits",
            {"month": 11, "year": 2026},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["student_id"], self.student.pk)
        self.assertEqual(response.data[0]["student_name"], self.student.name)
        self.assertTrue(response.data[0]["within_limit"])
        self.assertEqual(response.data[1]["student_id"], other_student.pk)
        self.assertEqual(response.data[1]["registration_count"], 3)
        self.assertFalse(response.data[1]["within_limit"])

    def test_registration_limit_report_requires_valid_period(self):
        missing_month = self.client.get(
            "/api/reports/vehicle-registration-limits",
            {"year": 2026},
        )
        invalid_month = self.client.get(
            "/api/reports/vehicle-registration-limits",
            {"month": 13, "year": 2026},
        )

        self.assertEqual(missing_month.status_code, 400)
        self.assertEqual(invalid_month.status_code, 400)
