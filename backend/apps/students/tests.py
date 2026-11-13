from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.rooms.models import Room, RoomAssignment
from apps.students.models import Student


class StudentApiTests(APITestCase):
    def test_authenticated_staff_can_create_student_without_optional_fields(self):
        response = self.client.post(
            "/api/auth/register",
            {
                "email": "staff@example.com",
                "full_name": "Staff",
                "phone_number": "0901234567",
                "password": "secure-pass",
                "password_confirm": "secure-pass",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {response.data['token']}",
        )

        response = self.client.post(
            "/api/students",
            {"student_id": "SV001", "name": "Nguyen An"},
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertIsNone(response.data["identity_number"])
        self.assertIsNone(response.data["birth_date"])

    def test_student_delete_is_blocked_by_room_assignment_history(self):
        user = get_user_model().objects.create_user(
            username="staff-delete-student",
            password="secure-pass",
        )
        self.client.force_authenticate(user=user)
        student = Student.objects.create(student_id="SV002", name="Tran Binh")
        room = Room.objects.create(
            room_id="P101",
            name="Phòng 101",
            monthly_price="1800000.00",
            max_occupants=4,
        )
        RoomAssignment.objects.create(
            student=student,
            room=room,
            start_date="2026-01-01",
        )

        response = self.client.delete(f"/api/students/{student.pk}")

        self.assertEqual(response.status_code, 400)
        self.assertTrue(Student.objects.filter(pk=student.pk).exists())
        self.assertIn("lịch sử phân phòng", response.data["detail"])

    def test_student_without_history_can_be_deleted(self):
        user = get_user_model().objects.create_user(
            username="staff-delete-student",
            password="secure-pass",
        )
        self.client.force_authenticate(user=user)
        student = Student.objects.create(student_id="SV003", name="Le Chi")

        response = self.client.delete(f"/api/students/{student.pk}")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Student.objects.filter(pk=student.pk).exists())
