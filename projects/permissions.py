from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .models import Contributor, Project, Issue, Comment


from rest_framework.permissions import BasePermission
from rest_framework.exceptions import ValidationError
from .models import Contributor, Issue

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import ValidationError
from .models import Contributor, Issue, Project, Comment


class IsContributor(BasePermission):
    """
    Autorise uniquement les utilisateurs qui contribuent à un projet à accéder
    ou à créer des ressources liées à ce projet.

    - Pour une POST sur les commentaires :
      * Route imbriquée       -> utilise 'issue_pk' de l'URL
      * Route plate (/comments/) -> exige 'issue' dans le JSON
    - Pour une POST sur issues/contributors :
      * Route imbriquée (/projects/{project_pk}/...) -> utilise 'project_pk'
      * Route plate (/issues/, /contributors/)         -> exige 'project' dans le JSON
    - Si ni clé URL ni champ requis présent : lève ValidationError (400).
    - En cas d'absence de contributor : renvoie False => 403 Forbidden.
    - Pour les autres méthodes (GET, PUT, DELETE), délègue à has_object_permission.
    """

    def has_permission(self, request, view):
        # Autorise tout sauf POST
        if request.method != 'POST':
            return True

        # Distingue les ressources par basename (défini par le router)
        base = getattr(view, 'basename', '')

        # Création de commentaire
        if base in ('comment', 'issue-comments'):
            # Nested : /projects/.../issues/{issue_pk}/comments/
            issue_pk = view.kwargs.get('issue_pk')
            if issue_pk:
                try:
                    issue = Issue.objects.get(pk=issue_pk)
                except Issue.DoesNotExist:
                    raise ValidationError({'issue': 'Issue introuvable pour création de commentaire.'})
                project_id = issue.project.id
            else:
                # Flat : /comments/ -> require 'issue'
                issue_id = request.data.get('issue')
                if not issue_id:
                    raise ValidationError({'issue': 'Le champ issue est requis.'})
                try:
                    issue = Issue.objects.get(pk=issue_id)
                except Issue.DoesNotExist:
                    raise ValidationError({'issue': 'Issue introuvable.'})
                project_id = issue.project.id

        else:
            # Création pour issues ou contributeurs
            project_pk = view.kwargs.get('project_pk')
            if project_pk:
                project_id = project_pk
            else:
                # Flat routes (/issues/, /contributors/)
                project_id = request.data.get('project')
                if not project_id:
                    raise ValidationError({'project': 'Le champ project est requis.'})

        # Vérifie contribution
        if not Contributor.objects.filter(user=request.user, project_id=project_id).exists():
            return False

        return True

    def has_object_permission(self, request, view, obj):
        # Vérification GET, PUT, DELETE sur instances
        if isinstance(obj, Project):
            return Contributor.objects.filter(user=request.user, project=obj).exists()
        if isinstance(obj, Issue):
            return Contributor.objects.filter(user=request.user, project=obj.project).exists()
        if isinstance(obj, Comment):
            return Contributor.objects.filter(user=request.user, project=obj.issue.project).exists()
        return False


class IsAuthor(BasePermission):
    """
    Autorise la modification ou suppression si request.user est l'auteur de l'objet.
    """

    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'author', None) == request.user


class IsAuthorOrReadOnly(BasePermission):
    """
    Autorise la lecture pour tous, et l'écriture uniquement pour l'auteur.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return getattr(obj, 'author', None) == request.user



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
