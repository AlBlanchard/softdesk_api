from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle CustomUser.

    - Permet la conversion entre l'objet CustomUser et sa représentation JSON.
    - Gère la création sécurisée du mot de passe.
    - Valide que l'âge de l'utilisateur est >= 15 ans.
    """

    class Meta:
        model = CustomUser
        # Champs exposés via l'API
        fields = [
            "id",                 # Identifiant unique (lecture seule)
            "username",           # Nom d'utilisateur
            "password",           # Mot de passe (écriture seule)
            "email",              # Adresse e-mail
            "first_name",         # Prénom
            "last_name",          # Nom
            "age",                # Âge (doit être >= 15)
            "can_be_contacted",   # Autorisation de contact
            "can_data_be_shared", # Autorisation de partage des données
        ]
        # Configuration spéciale pour certains champs
        extra_kwargs = {
            # Le mot de passe ne peut être lu via l'API
            "password": {"write_only": True},
        }

    def validate_age(self, value):
        """
        Vérifie que l'âge, s'il est fourni, est d'au moins 15 ans.

        Args:
            value (int|None): âge soumis par le client.

        Raises:
            ValidationError: si age < 15.

        Returns:
            int|None: valeur validée.
        """
        if value is not None and value < 15:
            raise serializers.ValidationError(
                "L'utilisateur doit avoir au moins 15 ans pour s'inscrire."
            )
        return value

    def create(self, validated_data):
        """
        Crée une instance CustomUser en hashant le mot de passe.

        - Extrait le mot de passe du validated_data.
        - Utilise set_password() pour le hasher.
        - Sauvegarde l'utilisateur en base.

        Args:
            validated_data (dict): données validées par le sérialiseur.

        Returns:
            CustomUser: nouvel utilisateur créé.
        """
        password = validated_data.pop("password")
        # Instancie l'utilisateur sans mot de passe en clair
        user = CustomUser(**validated_data)
        # Hash du mot de passe
        user.set_password(password)
        user.save()
        return user