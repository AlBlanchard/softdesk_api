from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
            "age",
            "can_be_contacted",
            "can_data_be_shared",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_age(self, value):
        if value is not None and value < 15:
            raise serializers.ValidationError(
                "L'utilisateur doit avoir au moins 15 ans pour s'inscrire."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
