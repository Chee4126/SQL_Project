from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.students.models import Student
from apps.visitors.models import Visit, Visitor


class VisitorVisitApiTests(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="staff-visitors",
            password="secure-pass",
        )
        self.client.force_authenticate(user=user)
        self.visitor = Visitor.objects.create(name="Nguyen Van A")

    def test_guest_catalog_endpoints_are_removed(self):
        response = self.client.get("/api/visitors")

        self.assertEqual(response.status_code, 404)

    def test_visit_can_create_visitor_from_manually_entered_details(self):
        student = Student.objects.create(student_id="SV002", name="Tran Binh")

        response = self.client.post(
            "/api/visits",
            {
                "visitor_name_input": "Le Thi B",
                "visitor_identity_number": "0123456789",
                "visitor_birth_date": "1998-02-03",
                "student_id": student.pk,
                "arrived_at": "2026-11-06T09:00:00Z",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["visitor_name"], "Le Thi B")
        visitor = Visitor.objects.get(identity_number="0123456789")
        self.assertEqual(visitor.birth_date.isoformat(), "1998-02-03")
        self.assertEqual(response.data["visitor_id"], visitor.pk)

    def test_visit_reuses_existing_visitor_by_identity_number(self):
        student = Student.objects.create(student_id="SV003", name="Nguyen An")
        visitor = Visitor.objects.create(
            name="Pham Van C",
            identity_number="9988776655",
        )

        response = self.client.post(
            "/api/visits",
            {
                "visitor_name_input": visitor.name,
                "visitor_identity_number": visitor.identity_number,
                "student_id": student.pk,
                "arrived_at": "2026-11-06T09:00:00Z",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["visitor_id"], visitor.pk)
        self.assertEqual(Visitor.objects.filter(identity_number="9988776655").count(), 1)

    def test_returning_guest_without_identity_number_increments_visit_count(self):
        student = Student.objects.create(student_id="SV003A", name="Nguyen An")
        previous_visit = Visit.objects.create(
            visitor=self.visitor,
            student=student,
            arrived_at=datetime(2026, 11, 12, 9, tzinfo=timezone.utc),
            left_at=datetime(2026, 11, 12, 10, tzinfo=timezone.utc),
        )

        response = self.client.post(
            "/api/visits",
            {
                "visitor_name_input": self.visitor.name,
                "student_id": student.pk,
                "arrived_at": "2026-11-13T09:00:00Z",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["visitor_id"], previous_visit.visitor_id)
        report = self.client.get(
            "/api/reports/visits",
            {"period": "month", "date": "2026-11-13"},
        )
        self.assertEqual(report.status_code, 200, report.data)
        self.assertEqual(report.data["results"][0]["visit_count"], 2)

    def test_visit_rejects_identity_number_with_different_name(self):
        student = Student.objects.create(student_id="SV004", name="Tran Binh")
        Visitor.objects.create(name="Existing Name", identity_number="0011223344")

        response = self.client.post(
            "/api/visits",
            {
                "visitor_name_input": "Different Name",
                "visitor_identity_number": "0011223344",
                "student_id": student.pk,
                "arrived_at": "2026-11-06T09:00:00Z",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("visitor_name_input", response.data)

    def test_visit_rejects_manually_entered_guest_with_open_visit(self):
        student = Student.objects.create(student_id="SV005", name="Le Chi")
        visitor = Visitor.objects.create(
            name="Open Visit Guest",
            identity_number="5566778899",
        )
        Visit.objects.create(
            visitor=visitor,
            student=student,
            arrived_at=datetime(2026, 11, 6, 8, tzinfo=timezone.utc),
        )
        another_student = Student.objects.create(
            student_id="SV006",
            name="Nguyen Lan",
        )

        response = self.client.post(
            "/api/visits",
            {
                "visitor_name_input": visitor.name,
                "visitor_identity_number": visitor.identity_number,
                "student_id": another_student.pk,
                "arrived_at": "2026-11-06T09:00:00Z",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Visit.objects.count(), 1)

    def test_visit_still_accepts_existing_visitor_id(self):
        student = Student.objects.create(student_id="SV007", name="Pham Ha")

        response = self.client.post(
            "/api/visits",
            {
                "visitor_id": self.visitor.pk,
                "student_id": student.pk,
                "arrived_at": "2026-11-06T09:00:00Z",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["visitor_id"], self.visitor.pk)

    def test_departure_updates_visit_status_and_persists_departure_time(self):
        student = Student.objects.create(student_id="SV008", name="Vu Lan")
        visit = Visit.objects.create(
            visitor=self.visitor,
            student=student,
            arrived_at=datetime(2026, 11, 6, 8, tzinfo=timezone.utc),
        )

        response = self.client.patch(
            f"/api/visits/{visit.pk}/departure",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)
        self.assertIsNotNone(response.data["left_at"])
        visit.refresh_from_db()
        self.assertIsNotNone(visit.left_at)
        self.assertEqual(
            self.client.get("/api/visits").data[0]["left_at"],
            response.data["left_at"],
        )
