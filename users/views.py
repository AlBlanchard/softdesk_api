from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError, PermissionDenied

from django.contrib.auth.password_validation import validate_password

from .models import CustomUser
from .serializers import CustomUserSerializer


class RegisterView(APIView):
    """
    Vue API pour l'enregistrement d'un nouvel utilisateur.

    Permissions :
        AllowAny - accessible sans authentification.

    Méthode POST :
        - Vérifie la présence de username, password et age.
        - Contrôle que l'âge est ≥ 15 ans.
        - Valide la robustesse du mot de passe avec validate_password().
        - Vérifie l'unicité du username.
        - Crée l'utilisateur si toutes les validations passent.
        - Retourne un message de succès ou d'erreur avec le statut approprié.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Traite la requête d'inscription.

        Args:
            request (Request): contient les champs username, password, age,
                               can_be_contacted, can_data_be_shared.

        Returns:
            Response: JSON avec message de succès ou détails de l'erreur.
        """
        username = request.data.get("username")
        password = request.data.get("password")
        age = request.data.get("age")
        can_be_contacted = request.data.get("can_be_contacted", False)
        can_data_be_shared = request.data.get("can_data_be_shared", False)

        # Vérification des champs requis
        if not username or not password or age is None:
            return Response(
                {"error": "Username, password et age sont requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validation de l'âge minimal
        if int(age) < 15:
            return Response(
                {"error": "Vous devez avoir au moins 15 ans pour vous inscrire."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validation du mot de passe selon les règles Django
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        # Vérification de l'unicité du nom d'utilisateur
        if CustomUser.objects.filter(username=username).exists():
            return Response(
                {"error": "Ce nom d'utilisateur existe déjà."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Création de l'utilisateur avec create_user() qui hash le mot de passe
        CustomUser.objects.create_user(
            username=username,
            password=password,
            age=age,
            can_be_contacted=can_be_contacted,
            can_data_be_shared=can_data_be_shared,
        )
        return Response(
            {"message": "Utilisateur créé avec succès."},
            status=status.HTTP_201_CREATED,
        )


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les utilisateurs par leurs propres profils.

    Permissions :
        IsAuthenticated - seules les requêtes authentifiées sont autorisées.

    - get_queryset : renvoie uniquement l'utilisateur connecté.
    - perform_destroy : n'autorise la suppression que sur son propre compte,
      sinon déclenche PermissionDenied.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Limite le queryset à l'utilisateur connecté.

        Returns:
            QuerySet[CustomUser]: l'objet user courant.
        """
        return CustomUser.objects.filter(id=self.request.user.id)

    def perform_destroy(self, instance):
        """
        Supprime le compte utilisateur si c'est le sien,
        sinon lève une exception PermissionDenied.

        Args:
            instance (CustomUser): instance à supprimer.
        """
        if instance != self.request.user:
            raise PermissionDenied(
                "Vous ne pouvez supprimer que votre propre compte."
            )
        instance.delete()
