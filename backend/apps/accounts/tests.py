from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class RegistrationApiTests(APITestCase):
    def test_registration_always_creates_staff_and_returns_login_token(self):
        response = self.client.post(
            "/api/auth/register",
            {
                "email": "new-user@example.com",
                "full_name": "New User",
                "phone_number": "+84901234567",
                "password": "secure-pass",
                "password_confirm": "secure-pass",
                "role": "ADMIN",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"]["role"], "STAFF")
        self.assertEqual(response.data["user"]["username"], "new-user")
        self.assertEqual(response.data["user"]["email"], "new-user@example.com")
        self.assertEqual(response.data["user"]["phone_number"], "+84901234567")
        self.assertTrue(response.data["token"])
        user = User.objects.get(email="new-user@example.com")
        self.assertTrue(user.check_password("secure-pass"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        login = self.client.post(
            "/api/auth/login",
            {"email": "NEW-USER@example.com", "password": "secure-pass"},
            format="json",
        )
        self.assertEqual(login.status_code, 200)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {response.data['token']}",
        )
        current_user = self.client.get("/api/auth/me")
        self.assertEqual(current_user.status_code, 200)
        self.assertEqual(current_user.data["email"], "new-user@example.com")

    def test_login_accepts_email_case_insensitively(self):
        user = User.objects.create_user(
            username="staff-account",
            email="staff@example.com",
            password="secure-pass",
            is_staff=True,
            is_superuser=True,
        )

        response = self.client.post(
            "/api/auth/login",
            {"email": "STAFF@example.com", "password": "secure-pass"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["id"], user.id)
        self.assertEqual(response.data["user"]["role"], "STAFF")

    def test_staff_can_create_account_with_email_and_phone(self):
        staff = User.objects.create_user(
            username="staff",
            email="staffer@example.com",
            password="secure-pass",
        )
        self.client.force_authenticate(user=staff)
        self.assertEqual(self.client.get("/api/accounts").status_code, 200)

        response = self.client.post(
            "/api/accounts",
            {
                "email": "staff@example.com",
                "full_name": "Staff User",
                "phone_number": "0901234567",
                "password": "secure-pass",
                "role": "ADMIN",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["email"], "staff@example.com")
        self.assertEqual(response.data["phone_number"], "0901234567")
        self.assertEqual(response.data["role"], "STAFF")
        created_user = User.objects.get(email="staff@example.com")
        self.assertFalse(created_user.is_staff)
        self.assertFalse(created_user.is_superuser)

    def test_account_list_requires_authentication_and_legacy_admin_api_is_removed(self):
        response = self.client.get("/api/accounts")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(self.client.get("/api/admin/users").status_code, 404)
        self.assertEqual(self.client.patch("/api/admin/users/1/role").status_code, 404)

    def test_account_cannot_delete_current_user(self):
        user = User.objects.create_user(
            username="staff-delete-self",
            password="secure-pass",
        )
        self.client.force_authenticate(user=user)

        response = self.client.delete(f"/api/accounts/{user.pk}")

        self.assertEqual(response.status_code, 400)
        self.assertTrue(User.objects.filter(pk=user.pk).exists())

    def test_account_can_delete_another_user(self):
        current_user = User.objects.create_user(
            username="staff-delete-other",
            password="secure-pass",
        )
        other_user = User.objects.create_user(
            username="other-account",
            password="secure-pass",
        )
        self.client.force_authenticate(user=current_user)

        response = self.client.delete(f"/api/accounts/{other_user.pk}")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(User.objects.filter(pk=other_user.pk).exists())

    def test_user_can_update_profile_without_changing_role(self):
        user = User.objects.create_user(
            username="profile-user",
            email="old@example.com",
            password="secure-pass",
            first_name="Old Name",
        )
        self.client.force_authenticate(user=user)

        response = self.client.patch(
            "/api/auth/me",
            {
                "full_name": "Updated Name",
                "email": "new@example.com",
                "phone_number": "0901234567",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["full_name"], "Updated Name")
        self.assertEqual(response.data["email"], "new@example.com")
        self.assertEqual(response.data["phone_number"], "0901234567")
        user.refresh_from_db()
        self.assertEqual(user.username, "profile-user")
        self.assertFalse(user.is_superuser)

    def test_profile_update_rejects_duplicate_email(self):
        user = User.objects.create_user(
            username="profile-user",
            email="old@example.com",
            password="secure-pass",
        )
        User.objects.create_user(
            username="other-user",
            email="used@example.com",
            password="secure-pass",
        )
        self.client.force_authenticate(user=user)

        response = self.client.patch(
            "/api/auth/me",
            {
                "full_name": "User",
                "email": "USED@example.com",
                "phone_number": "0901234567",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_profile_password_change_requires_current_password(self):
        user = User.objects.create_user(
            username="profile-user",
            email="user@example.com",
            password="secure-pass",
        )
        self.client.force_authenticate(user=user)
        payload = {
            "full_name": "User",
            "email": "user@example.com",
            "phone_number": "0901234567",
            "current_password": "wrong-pass",
            "new_password": "new-secure-pass",
            "password_confirm": "new-secure-pass",
        }

        response = self.client.patch("/api/auth/me", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("current_password", response.data)
        user.refresh_from_db()
        self.assertTrue(user.check_password("secure-pass"))

    def test_profile_password_change_updates_password(self):
        user = User.objects.create_user(
            username="profile-user",
            email="user@example.com",
            password="secure-pass",
        )
        from rest_framework.authtoken.models import Token

        old_token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {old_token.key}")
        response = self.client.patch(
            "/api/auth/me",
            {
                "full_name": "User",
                "email": "user@example.com",
                "phone_number": "0901234567",
                "current_password": "secure-pass",
                "new_password": "new-secure-pass",
                "password_confirm": "new-secure-pass",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertFalse(Token.objects.filter(key=old_token.key).exists())
        self.assertTrue(Token.objects.filter(key=response.data["token"], user=user).exists())
        user.refresh_from_db()
        self.assertTrue(user.check_password("new-secure-pass"))

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(
            "/api/auth/register",
            {
                "email": "new-user@example.com",
                "full_name": "New User",
                "phone_number": "0901234567",
                "password": "secure-pass",
                "password_confirm": "different-pass",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("password_confirm", response.data)
        self.assertFalse(User.objects.filter(email="new-user@example.com").exists())

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="secure-pass",
        )

        response = self.client.post(
            "/api/auth/register",
            {
                "email": "EXISTING@example.com",
                "full_name": "New User",
                "phone_number": "0901234567",
                "password": "secure-pass",
                "password_confirm": "secure-pass",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)
