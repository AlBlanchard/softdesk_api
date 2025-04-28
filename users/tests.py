from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken


class CustomUserPermissionTests(APITestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            username="user1", password="password123", age=20
        )
        self.user2 = CustomUser.objects.create_user(
            username="user2", password="password123", age=30
        )

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_user_can_retrieve_own_profile(self):
        self.authenticate(self.user1)
        url = reverse("users:user-detail", args=[self.user1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_update_own_profile(self):
        self.authenticate(self.user1)
        url = reverse("users:user-detail", args=[self.user1.id])
        response = self.client.patch(url, {"age": 25}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.age, 25)

    def test_user_can_delete_own_account(self):
        self.authenticate(self.user1)
        url = reverse("users:user-detail", args=[self.user1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cannot_access_another_user_profile(self):
        self.authenticate(self.user1)
        url = reverse("users:user-detail", args=[self.user2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_update_another_user_profile(self):
        self.authenticate(self.user1)
        url = reverse("users:user-detail", args=[self.user2.id])
        response = self.client.patch(url, {"age": 35}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_delete_another_user_account(self):
        self.authenticate(self.user1)
        url = reverse("users:user-detail", args=[self.user2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
