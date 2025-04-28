from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, CustomUserViewSet

router = DefaultRouter()
router.register(r"users", CustomUserViewSet, basename="user")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("", include(router.urls)),
]
