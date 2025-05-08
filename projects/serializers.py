from rest_framework import serializers
from .models import Project, Contributor, Issue, Comment
from django.contrib.auth import get_user_model

# Récupère le modèle utilisateur configuré pour ce projet
User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Project.

    - Gère la conversion entre l'objet Project et sa représentation JSON.
    - Le champ 'author' est en lecture seule et renvoie le nom d'utilisateur.
    """
    # Affiche le nom d'utilisateur de l'auteur au lieu de son ID
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Project
        fields = [
            "id",         # Identifiant unique du projet
            "title",      # Titre du projet
            "description",# Description détaillée
            "type",       # Type ou catégorie du projet
            "author",     # Auteur (en lecture seule)
            "created_time"# Date de création (en lecture seule)
        ]
        read_only_fields = ["id", "author", "created_time"]


class ContributorSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Contributor.

    - Affiche le nom d'utilisateur et l'ID du projet associés.
    """
    # Nom d'utilisateur du contributeur en lecture seule
    user = serializers.ReadOnlyField(source="user.username")
    # ID du projet en lecture seule
    project = serializers.ReadOnlyField(source="project.id")

    class Meta:
        model = Contributor
        fields = [
            "id",          # Identifiant unique
            "user",        # Contributeur (en lecture seule)
            "project",     # Projet associé (en lecture seule)
            "created_time" # Date d'ajout (en lecture seule)
        ]
        read_only_fields = ["id", "user", "project", "created_time"]


class IssueSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Issue.

    - Permet de lire et de créer/modifier des issues.
    - Champ 'author' en lecture seule.
    - Champ 'project' pour définir l'ID du projet parent.
    - Champ 'assignee_user' optionnel pour l'utilisateur assigné.
    """
    # Nom d'utilisateur de l'auteur en lecture seule
    author = serializers.ReadOnlyField(source="author.username")
    # Clé primaire du projet parent (écriture autorisée)
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all()
    )
    # Clé primaire de l'utilisateur assigné (optionnel)
    assignee_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Issue
        fields = [
            "id",            # Identifiant unique de l'issue
            "title",         # Titre de l'issue
            "description",   # Description détaillée
            "tag",           # Étiquette de catégorie
            "priority",      # Priorité
            "status",        # Statut actuel
            "project",       # Projet parent
            "author",        # Auteur (en lecture seule)
            "assignee_user", # Utilisateur assigné (optionnel)
            "created_time"   # Date de création (en lecture seule)
        ]
        read_only_fields = ["id", "author", "created_time"]


class CommentSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Comment.

    - Convertit entre Comment et JSON.
    - Champ 'author' en lecture seule.
    - Champ 'issue' optionnel pour définir l'ID de l'issue parente.
    """
    # Nom d'utilisateur de l'auteur en lecture seule
    author = serializers.ReadOnlyField(source="author.username")
    # Clé primaire de l'issue parente (optionnel en contextes imbriqués)
    issue = serializers.PrimaryKeyRelatedField(
        queryset=Issue.objects.all(),
        required=False
    )

    class Meta:
        model = Comment
        fields = [
            "id",           # Identifiant unique du commentaire (UUID)
            "description",  # Contenu du commentaire
            "author",       # Auteur (en lecture seule)
            "issue",        # Issue parente (optionnel)
            "created_time"  # Date de création (en lecture seule)
        ]
        read_only_fields = ["id", "author", "created_time"]
