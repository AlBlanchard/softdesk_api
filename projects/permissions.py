from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .models import Contributor, Project, Issue, Comment


class IsContributor(BasePermission):
    """
    Autorise uniquement les contributeurs d'un projet à interagir avec ses ressources.
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            # Création via project nested /projects/{project_pk}/issues/
            project_id = (
                request.data.get("project") or view.kwargs.get("project_pk") or None
            )

            # création d'un commentaire via issue nested /projects/{project_pk}/issues/{issue_pk}/comments/
            if not project_id:
                issue_id = request.data.get("issue") or view.kwargs.get("issue_pk")
                if not issue_id:
                    return False
                try:
                    issue = Issue.objects.get(pk=issue_id)
                    project_id = issue.project.id
                except Issue.DoesNotExist:
                    return False

            return Contributor.objects.filter(
                user=request.user, project_id=project_id
            ).exists()

        return True  # GET, etc délégué à has_object_permission

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            return Contributor.objects.filter(user=request.user, project=obj).exists()
        elif isinstance(obj, Issue):
            return Contributor.objects.filter(
                user=request.user, project=obj.project
            ).exists()
        elif isinstance(obj, Comment):
            return Contributor.objects.filter(
                user=request.user, project=obj.issue.project
            ).exists()
        return False

    def has_object_permission(self, request, view, obj):
        # Dans le cas d'un projet, vérifie si user est contributor
        if isinstance(obj, Project):
            return Contributor.objects.filter(user=request.user, project=obj).exists()
        # Dans le cas d'un autre obj, va chercher le projet lié pour vérifier si contributor
        elif isinstance(obj, Issue):
            return Contributor.objects.filter(
                user=request.user, project=obj.project
            ).exists()
        elif isinstance(obj, Comment):
            return Contributor.objects.filter(
                user=request.user, project=obj.issue.project
            ).exists()
        return False


class IsAuthor(permissions.BasePermission):
    """
    Autorise la modif ou suppression si le user est l'auteur de l'objet.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsAuthorOrReadOnly(BasePermission):
    """
    L'utilisateur peut modifier l'objet seulement s'il en est l'auteur.
    Sinon, il peut uniquement le lire.
    """

    def has_object_permission(self, request, view, obj):
        # Lecture autorisée
        if request.method in permissions.SAFE_METHODS:
            return True
        # Écriture seulement si auteur
        return obj.author == request.user
