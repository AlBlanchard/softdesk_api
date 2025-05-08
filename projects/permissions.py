from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .models import Contributor, Project, Issue, Comment


class IsContributor(BasePermission):
    """
    Autorise uniquement les utilisateurs qui contribuent à un projet à accéder
    ou à créer des ressources liées à ce projet.

    - Pour les opérations POST, vérifie si l'utilisateur est contributeur du projet
      ciblé soit directement via 'project' ou 'issue' dans les données de requête,
      soit via les paramètres 'project_pk' ou 'issue_pk' de l'URL.
    - Pour les autres méthodes (GET, PUT, DELETE, etc.), délègue au contrôle
      par objet (has_object_permission).
    """

    def has_permission(self, request, view):
        # Autoriser la lecture générale (liste, etc.)
        if request.method != 'POST':
            return True

        # Pour une création, déterminer l'ID du projet
        project_id = request.data.get('project') or view.kwargs.get('project_pk')

        # Si pas de projet, essayer de récupérer depuis une issue
        if not project_id:
            issue_id = request.data.get('issue') or view.kwargs.get('issue_pk')
            if not issue_id:
                return False
            try:
                issue = Issue.objects.get(pk=issue_id)
                project_id = issue.project.id
            except Issue.DoesNotExist:
                return False

        # Vérifier que l'utilisateur est bien contributeur de ce projet
        return Contributor.objects.filter(
            user=request.user,
            project_id=project_id
        ).exists()

    def has_object_permission(self, request, view, obj):
        # Vérifie l'accès en lecture ou écriture selon l'objet cible
        if isinstance(obj, Project):
            return Contributor.objects.filter(user=request.user, project=obj).exists()
        if isinstance(obj, Issue):
            return Contributor.objects.filter(
                user=request.user,
                project=obj.project
            ).exists()
        if isinstance(obj, Comment):
            return Contributor.objects.filter(
                user=request.user,
                project=obj.issue.project
            ).exists()
        return False


class IsAuthor(BasePermission):
    """
    Autorise uniquement l'auteur d'un objet à le modifier ou le supprimer.
    La lecture reste possible pour tous selon leur permission.
    """

    def has_object_permission(self, request, view, obj):
        # Seul l'auteur originel peut modifier ou supprimer
        return getattr(obj, 'author', None) == request.user


class IsAuthorOrReadOnly(BasePermission):
    """
    Permet la lecture (SAFE_METHODS) à tous,
    mais autorise la modification seulement si l'utilisateur en est l'auteur.
    """

    def has_object_permission(self, request, view, obj):
        # Méthodes de lecture considérées comme safe
        if request.method in permissions.SAFE_METHODS:
            return True
        # Méthodes d'écriture réservées à l'auteur
        return getattr(obj, 'author', None) == request.user
