from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .models import Contributor, Project, Issue, Comment


class IsContributor(BasePermission):
    """
    Autorise uniquement les contributeurs d'un projet à interagir avec ses ressources.
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            project_id = request.data.get("project")
            if not project_id:
                return False  # aucune info sur le projet = rejet
            return Contributor.objects.filter(
                user=request.user, project_id=project_id
            ).exists()
        return True  # autres méthodes, laisse has_object_permission gérer

    def has_object_permission(self, request, view, obj):
        # Dans le cas d'un projet, vérifie si user est contributor
        if isinstance(obj, Project):
            return Contributor.objects.filter(user=request.user, project=obj).exists()
        # Dans le cas d'un autre obj, va chercher le projet lié pour vérifier si contributor
        elif isinstance(obj, Issue) or isinstance(obj, Comment):
            return Contributor.objects.filter(
                user=request.user, project=obj.project
            ).exists()
        return False


class IsAuthor(permissions.BasePermission):
    """
    Autorise la modif ou suppression si le user est l'auteur du projet.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsAuthorOrReadOnly(BasePermission):
    """
    L'utilisateur peut modifier l'objet seulement s'il en est l'auteur.
    Sinon, il ne peut que le lire.
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            project = obj
        elif hasattr(obj, "project"):
            project = obj.project
        else:
            return False

        return Contributor.objects.filter(user=request.user, project=project).exists()


class IsIssueAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author_user == request.user
