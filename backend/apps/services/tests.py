from datetime import datetime, timezone
from decimal import Decimal

from rest_framework.test import APITestCase

from apps.services.models import Service, ServiceUsage
from apps.students.models import Student


# Kiểm tra ghi nhận sử dụng dịch vụ và các báo cáo.
class ServiceApiTests(APITestCase):
    def setUp(self):
        self.student = Student.objects.create(student_id="SV001", name="Nguyen An")
        self.service = Service.objects.create(
            name="Giặt là",
            price=Decimal("15000.00"),
            unit="kg",
        )

    def test_create_service_usage_snapshots_current_price(self):
        response = self.client.post(
            "/api/service-usages",
            {
                "student_id": self.student.pk,
                "service_id": self.service.pk,
                "used_at": "2026-11-06T09:00:00Z",
                "quantity": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Decimal(response.data["applied_price"]), Decimal("15000.00"))
        self.service.price = Decimal("20000.00")
        self.service.save()
        usage = ServiceUsage.objects.get(pk=response.data["id"])
        self.assertEqual(usage.applied_price, Decimal("15000.00"))
        self.assertEqual(usage.amount, Decimal("30000.00"))

    def test_usage_requires_positive_quantity_and_existing_student(self):
        payload = {
            "student_id": self.student.pk,
            "service_id": self.service.pk,
            "used_at": "2026-11-06T09:00:00Z",
            "quantity": 0,
        }
        response = self.client.post("/api/service-usages", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("quantity", response.data)

        payload["quantity"] = 1
        payload["student_id"] = "NOT-FOUND"
        response = self.client.post("/api/service-usages", payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("student_id", response.data)

    def test_missing_service_usage_fields_have_vietnamese_errors(self):
        response = self.client.post("/api/service-usages", {}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["student_id"][0], "Trường này là bắt buộc.")
        self.assertEqual(response.data["service_id"][0], "Trường này là bắt buộc.")

    def test_service_usage_report_groups_and_totals(self):
        ServiceUsage.objects.create(
            student=self.student,
            service=self.service,
            used_at=datetime(2026, 11, 6, 9, tzinfo=timezone.utc),
            quantity=2,
            applied_price=Decimal("15000.00"),
        )
        response = self.client.get(
            "/api/reports/service-usage",
            {"date_from": "2026-11-01", "date_to": "2026-11-30"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["total_quantity"], 2)
        self.assertEqual(Decimal(response.data[0]["total_amount"]), Decimal("30000.00"))

    def test_revenue_report_includes_services_without_usage(self):
        response = self.client.get(
            "/api/reports/service-revenue",
            {"year": 2026, "month": 11},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Decimal(response.data[0]["total_revenue"]), Decimal("0.00"))

    def test_revenue_report_sums_usage_for_requested_month(self):
        ServiceUsage.objects.create(
            student=self.student,
            service=self.service,
            used_at=datetime(2026, 11, 6, 9, tzinfo=timezone.utc),
            quantity=2,
            applied_price=Decimal("15000.00"),
        )
        response = self.client.get(
            "/api/reports/service-revenue",
            {"year": 2026, "month": 11},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["total_quantity"], 2)
        self.assertEqual(
            Decimal(response.data[0]["total_revenue"]),
            Decimal("30000.00"),
        )


# Kiểm tra tạo, cập nhật và kiểm tra đơn giá dịch vụ.
class ServiceCatalogApiTests(APITestCase):
    def test_create_and_update_service(self):
        create_response = self.client.post(
            "/api/services",
            {"name": "Nước uống", "price": "5000.00", "unit": "chai"},
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)

        update_response = self.client.put(
            f"/api/services/{create_response.data['id']}",
            {"name": "Nước uống", "price": "6000.00", "unit": "chai"},
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(Decimal(update_response.data["price"]), Decimal("6000.00"))

    def test_service_price_cannot_be_negative(self):
        response = self.client.post(
            "/api/services",
            {"name": "Nước uống", "price": "-1.00", "unit": "chai"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("price", response.data)
