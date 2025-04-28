from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "age",
        "can_be_contacted",
        "can_data_be_shared",
    )
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_active", "can_be_contacted", "can_data_be_shared")
    ordering = ("username",)
