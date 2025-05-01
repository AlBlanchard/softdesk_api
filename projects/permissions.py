from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .models import Contributor, Project, Issue, Comment


class IsContributor(BasePermission):
    """
    Autorise uniquement les contributeurs d'un projet à interagir avec ses ressources.
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            if "project" in request.data:
                # Création d'une Issue : vérifie via le projet
                project_id = request.data.get("project")
                if not project_id:
                    return False
                return Contributor.objects.filter(
                    user=request.user, project_id=project_id
                ).exists()
            elif "issue" in request.data:
                # Création d'un Comment : vérifie via l'issue liée
                issue_id = request.data.get("issue")
                if not issue_id:
                    return False
                try:
                    issue = Issue.objects.get(pk=issue_id)
                except Issue.DoesNotExist:
                    return False
                return Contributor.objects.filter(
                    user=request.user, project=issue.project
                ).exists()
            else:
                # Aucun project ni issue trouvé = interdit
                return False
        return True  # autres méthodes, laisse has_object_permission gérer

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
