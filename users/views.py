from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError, PermissionDenied

from django.contrib.auth.password_validation import validate_password

from .models import CustomUser
from .serializers import CustomUserSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        age = request.data.get("age")
        can_be_contacted = request.data.get("can_be_contacted", False)
        can_data_be_shared = request.data.get("can_data_be_shared", False)

        if not username or not password or age is None:
            return Response(
                {"error": "Username, password, and age are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if int(age) < 15:
            return Response(
                {"error": "You must be at least 15 years old to register."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(password)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            age=age,
            can_be_contacted=can_be_contacted,
            can_data_be_shared=can_data_be_shared,
        )
        return Response(
            {"message": "User created successfully."},
            status=status.HTTP_201_CREATED,
        )


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)

    def perform_destroy(self, instance):
        if instance != self.request.user:
            raise PermissionDenied("Vous ne pouvez supprimer que votre propre compte.")
        instance.delete()
