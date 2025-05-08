from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken


class CustomUserPermissionTests(APITestCase):
    """
    Tests des permissions et validations pour les opérations sur le modèle CustomUser via l'API.

    Vérifie que chaque utilisateur :
    - Peut récupérer, modifier et supprimer son propre profil.
    - Ne peut pas accéder aux profils des autres (404).
    - Peut mettre à jour ses préférences de consentement.
    - Ne peut pas définir un âge inférieur à 15 ans.
    """

    def setUp(self):
        """
        Prépare deux utilisateurs pour les tests.
        """
        self.user1 = CustomUser.objects.create_user(
            username="user1", password="password123", age=20
        )
        self.user2 = CustomUser.objects.create_user(
            username="user2", password="password123", age=30
        )

    def authenticate(self, user):
        """
        Authentifie un utilisateur en générant un token JWT et en l'ajoutant à l'en-tête Authorization.

        Args:
            user (CustomUser): utilisateur à authentifier.
        """
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_user_can_retrieve_own_profile(self):
        """
        Un utilisateur authentifié peut accéder à son propre profil (status 200).
        """
        self.authenticate(self.user1)
        url = reverse("users:user-detail", args=[self.user1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_update_own_profile(self):
        """
        Un utilisateur peut modifier son âge (status 200) et la valeur est persistée.
        """
        self.authenticate(self.user1)
        url = reverse("users:user-detail", args=[self.user1.id])
        response = self.client.patch(url, {"age": 25}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.age, 25)

    def test_user_can_delete_own_account(self):
        """
        Un utilisateur peut supprimer son propre compte (status 204).
        """
        self.authenticate(self.user1)
        url = reverse("users:user-detail", args=[self.user1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cannot_access_another_user_profile(self):
        """
        Un utilisateur ne peut pas récupérer le profil d'un autre (status 404).
        """
        self.authenticate(self.user1)
        url = reverse("users:user-detail", args=[self.user2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_update_another_user_profile(self):
        """
        Un utilisateur ne peut pas mettre à jour le profil d'un autre (status 404).
        """
        self.authenticate(self.user1)
        url = reverse("users:user-detail", args=[self.user2.id])
        response = self.client.patch(url, {"age": 35}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_delete_another_user_account(self):
        """
        Un utilisateur ne peut pas supprimer un compte autre que le sien (status 404).
        """
        self.authenticate(self.user1)
        url = reverse("users:user-detail", args=[self.user2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_consent_choices(self):
        """
        Un utilisateur peut modifier ses choix de consentement (status 200) et les modifications sont persistées.
        """
        self.authenticate(self.user1)
        url = reverse("users:user-detail", args=[self.user1.id])
        data = {
            "can_be_contacted": True,
            "can_data_be_shared": False,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.can_be_contacted)
        self.assertFalse(self.user1.can_data_be_shared)

    def test_user_cannot_set_age_under_15(self):
        """
        La validation d'âge empêche de fixer un âge inférieur à 15 (status 400) et l'âge n'est pas modifié.
        """
        self.authenticate(self.user1)
        url = reverse("users:user-detail", args=[self.user1.id])
        response = self.client.patch(url, {"age": 14}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user1.refresh_from_db()
        self.assertNotEqual(self.user1.age, 14)