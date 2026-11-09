from datetime import datetime
from decimal import Decimal

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.students.models import Student
from apps.vehicles.models import MonthlyVehicleRegistration, Vehicle, VehicleEvent


# Kiểm tra đăng ký vé tháng, tra cứu xe và phí sự kiện gửi/lấy.
class VehicleApiTests(APITestCase):
    def setUp(self):
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
        self.assertEqual(vehicles.status_code, 200)
        self.assertEqual(vehicles.data[0]["plate_number"], "51A-22222")

    def test_first_two_daily_events_are_free_and_third_is_charged(self):
        registration_response = self.register("51A-33333")
        registration_id = registration_response.data["id"]
        event_url = f"/api/monthly-vehicle-registrations/{registration_id}/events"
        fees = []
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
            fees.append((response.data["is_free"], Decimal(response.data["fee"])))

        self.assertEqual(
            fees,
            [
                (True, Decimal("0.00")),
                (True, Decimal("0.00")),
                (False, Decimal("3000.00")),
            ],
        )

    def test_event_fee_counter_resets_next_local_day(self):
        registration = MonthlyVehicleRegistration.objects.create(
            student=self.student,
            vehicle=Vehicle.objects.create(
                plate_number="51A-44444",
                vehicle_type="Xe máy",
            ),
            month=11,
            year=2026,
        )
        previous_day = timezone.make_aware(datetime(2026, 11, 6, 23, 55))
        VehicleEvent.objects.create(
            registration=registration,
            event_at=previous_day,
            event_type=VehicleEvent.EventType.PARK,
            is_free=True,
            fee=Decimal("0.00"),
        )
        next_day_event = timezone.make_aware(datetime(2026, 11, 7, 0, 5))

        response = self.client.post(
            f"/api/monthly-vehicle-registrations/{registration.pk}/events",
            {
                "event_at": next_day_event.isoformat(),
                "event_type": "LAY",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["is_free"])
        self.assertEqual(Decimal(response.data["fee"]), Decimal("0.00"))

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

        self.assertEqual(invalid_event.status_code, 400)
        self.assertEqual(missing_registration.status_code, 400)

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
