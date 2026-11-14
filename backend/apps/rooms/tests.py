from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.invoices.models import Invoice
from apps.rooms.models import Room, RoomAssignment
from apps.students.models import Student


class RoomApiTests(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="staff",
            password="secure-pass",
        )
        self.client.force_authenticate(user=user)

    def create_room(self, room_id="P101", capacity=4):
        return Room.objects.create(
            room_id=room_id,
            name=f"Phòng {room_id}",
            monthly_price=Decimal("1800000.00"),
            max_occupants=capacity,
        )

    def test_room_creation_accepts_supported_price_capacity_pair(self):
        response = self.client.post(
            "/api/rooms",
            {
                "room_id": "P101",
                "name": "Phòng 101",
                "monthly_price": "1800000.00",
                "max_occupants": 4,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["max_occupants"], 4)
        self.assertEqual(response.data["monthly_price"], "1800000.00")
        self.assertNotIn("room_type_name", response.data)

    def test_room_creation_accepts_eight_person_price_option(self):
        response = self.client.post(
            "/api/rooms",
            {
                "room_id": "P102",
                "name": "Phòng 102",
                "monthly_price": "250000.00",
                "max_occupants": 8,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)

    def test_room_creation_rejects_mismatched_price_and_capacity(self):
        response = self.client.post(
            "/api/rooms",
            {
                "room_id": "P103",
                "name": "Phòng 103",
                "monthly_price": "1800000.00",
                "max_occupants": 8,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("monthly_price", response.data)

    def test_room_type_api_is_removed(self):
        self.assertEqual(self.client.get("/api/room-types").status_code, 404)

    def test_room_assignment_creates_invoice_for_its_month(self):
        room = self.create_room()
        student = Student.objects.create(student_id="SV011", name="Le Mai")

        zero_length_assignment = self.client.post(
            "/api/room-assignments",
            {
                "student_id": student.pk,
                "room_id": room.pk,
                "start_date": "2026-11-06",
                "end_date": "2026-11-06",
            },
            format="json",
        )
        response = self.client.post(
            "/api/room-assignments",
            {
                "student_id": student.pk,
                "room_id": room.pk,
                "start_date": "2026-11-06",
            },
            format="json",
        )

        self.assertEqual(zero_length_assignment.status_code, 201)
        self.assertEqual(response.status_code, 201, response.data)
        invoice = Invoice.objects.get(student=student, month=11, year=2026)
        self.assertEqual(invoice.room_amount, Decimal("1800000.00"))
        self.assertEqual(invoice.total_amount, Decimal("1800000.00"))
        self.assertEqual(invoice.status, Invoice.PaymentStatus.UNPAID)

    def test_room_delete_is_blocked_by_assignment_history(self):
        room = self.create_room()
        student = Student.objects.create(student_id="SV010", name="Nguyen An")
        RoomAssignment.objects.create(
            student=student,
            room=room,
            start_date=date.today(),
        )

        response = self.client.delete(f"/api/rooms/{room.pk}")

        self.assertEqual(response.status_code, 400)
        self.assertTrue(Room.objects.filter(pk=room.pk).exists())
        self.assertIn("lịch sử phân phòng", response.data["detail"])

    def test_room_without_assignment_history_can_be_deleted(self):
        room = self.create_room()

        response = self.client.delete(f"/api/rooms/{room.pk}")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Room.objects.filter(pk=room.pk).exists())

    def test_room_list_reports_occupancy_and_filters_full_rooms(self):
        room = self.create_room()
        students = [
            Student.objects.create(student_id=f"SV00{i}", name=f"Student {i}")
            for i in range(1, 5)
        ]
        for student in students:
            self.client.post(
                "/api/room-assignments",
                {
                    "student_id": student.pk,
                    "room_id": room.pk,
                    "start_date": date.today().isoformat(),
                },
                format="json",
            )

        rooms = self.client.get("/api/rooms", {"date": date.today().isoformat()})
        available = self.client.get(
            "/api/rooms",
            {"date": date.today().isoformat(), "available": "true"},
        )

        self.assertEqual(rooms.status_code, 200)
        self.assertEqual(rooms.data[0]["current_occupants"], 4)
        self.assertEqual(rooms.data[0]["max_occupants"], 4)
        self.assertEqual(available.data, [])

    def test_leaving_room_reduces_occupancy_on_departure_date(self):
        room = self.create_room()
        student = Student.objects.create(student_id="SV020", name="Nguyen An")
        assignment_response = self.client.post(
            "/api/room-assignments",
            {
                "student_id": student.pk,
                "room_id": room.pk,
                "start_date": date.today().isoformat(),
            },
            format="json",
        )
        self.assertEqual(assignment_response.status_code, 201)

        leave_response = self.client.patch(
            f"/api/room-assignments/{assignment_response.data['id']}/end",
            {},
            format="json",
        )
        room_response = self.client.get(
            "/api/rooms",
            {"date": date.today().isoformat()},
        )

        self.assertEqual(leave_response.status_code, 200)
        self.assertEqual(room_response.status_code, 200)
        self.assertEqual(room_response.data[0]["current_occupants"], 0)

    def test_room_assignment_uses_capacity_saved_on_room(self):
        room = self.create_room(capacity=4)
        Student.objects.create(student_id="SV001", name="Nguyen An")
        Student.objects.create(student_id="SV002", name="Tran Binh")

        first = self.client.post(
            "/api/room-assignments",
            {
                "student_id": "SV001",
                "room_id": room.pk,
                "start_date": date.today().isoformat(),
            },
            format="json",
        )
        second = self.client.post(
            "/api/room-assignments",
            {
                "student_id": "SV002",
                "room_id": room.pk,
                "start_date": date.today().isoformat(),
            },
            format="json",
        )

        self.assertEqual(first.status_code, 201, first.data)
        self.assertEqual(second.status_code, 201, second.data)
        third_student = Student.objects.create(student_id="SV003", name="Le Chi")
        third = self.client.post(
            "/api/room-assignments",
            {
                "student_id": third_student.pk,
                "room_id": room.pk,
                "start_date": date.today().isoformat(),
            },
            format="json",
        )
        fourth_student = Student.objects.create(student_id="SV004", name="Pham Ha")
        fourth = self.client.post(
            "/api/room-assignments",
            {
                "student_id": fourth_student.pk,
                "room_id": room.pk,
                "start_date": date.today().isoformat(),
            },
            format="json",
        )
        fifth_student = Student.objects.create(student_id="SV005", name="Vu Lan")
        fifth = self.client.post(
            "/api/room-assignments",
            {
                "student_id": fifth_student.pk,
                "room_id": room.pk,
                "start_date": date.today().isoformat(),
            },
            format="json",
        )
        self.assertEqual(third.status_code, 201, third.data)
        self.assertEqual(fourth.status_code, 201, fourth.data)
        self.assertEqual(fifth.status_code, 400)
        self.assertIn("room_id", fifth.data)
