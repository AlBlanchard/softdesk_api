from rest_framework import viewsets
from rest_framework import permissions as drf_permissions
from .permissions import IsAuthor, IsContributor, IsAuthorOrReadOnly
from .models import Project, Contributor, Issue, Comment
from .serializers import (
    ProjectSerializer,
    ContributorSerializer,
    IssueSerializer,
    CommentSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les opérations CRUD sur les projets.

    - list/retrieve : l'utilisateur doit être contributeur du projet.
    - create : tout utilisateur authentifié peut créer un projet.
    - update/partial_update/destroy : seul l'auteur du projet peut modifier ou supprimer.
    """
    serializer_class = ProjectSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Retourne les projets accessibles à l'utilisateur.

        - En génération de schéma Swagger, renvoie un queryset vide pour éviter les erreurs.
        - Sinon, filtre les projets où l'utilisateur est contributeur.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Project.objects.none()

        user = self.request.user
        return Project.objects.filter(contributors__user=user).distinct()

    def get_permissions(self):
        """
        Définit dynamiquement les permissions selon l'action :
        - update, partial_update, destroy : IsAuthor
        - retrieve, list                : IsContributor
        - autres (create)              : IsAuthenticated
        """
        if self.action in ["update", "partial_update", "destroy"]:
            return [drf_permissions.IsAuthenticated(), IsAuthor()]
        elif self.action in ["retrieve", "list"]:
            return [drf_permissions.IsAuthenticated(), IsContributor()]
        return [drf_permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Lors de la création, l'utilisateur devient l'auteur du projet
        et est automatiquement ajouté comme contributeur.
        """
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)


class ContributorViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les contributeurs d'un projet.

    - Sans paramètre project_pk : renvoie tous les contributeurs (flat routes).
    - Avec project_pk         : renvoie les contributeurs de ce projet uniquement.
    """
    serializer_class = ContributorSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Retourne le queryset de Contributor selon le contexte :
        - Swagger : vide
        - project_pk fourni : contributeurs de ce projet
        - sinon : tous les contributeurs
        """
        if getattr(self, 'swagger_fake_view', False):
            return Contributor.objects.none()

        project_id = self.kwargs.get("project_pk")
        if project_id is None:
            return Contributor.objects.all()
        return Contributor.objects.filter(project__id=project_id)


class IssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les issues.

    - list/retrieve (flat)          : l'utilisateur doit contribuer à l'un de ses projets.
    - list/retrieve (nested)        : limité au projet parent.
    - create (flat/nested)          : l'utilisateur doit être contributeur.
    - update/partial_update/destroy : seul l'auteur de l'issue peut modifier.
    """
    serializer_class = IssueSerializer

    def get_queryset(self):
        """
        Retourne les issues accessibles :
        - Swagger : queryset vide
        - nested (project_pk) : issues du projet où l'utilisateur contribue
        - flat list            : issues de tous les projets de l'utilisateur
        """
        if getattr(self, 'swagger_fake_view', False):
            return Issue.objects.none()

        qs = Issue.objects.all().distinct()
        project_pk = self.kwargs.get("project_pk")
        if project_pk:
            qs = qs.filter(
                project__id=project_pk,
                project__contributors__user=self.request.user
            )
        elif self.action == "list":
            qs = qs.filter(project__contributors__user=self.request.user)
        return qs

    def get_permissions(self):
        """
        Permissions selon l'action :
        - create, list, retrieve : IsContributor
        - update, partial_update, destroy : IsAuthor
        """
        if self.action in ["create", "list", "retrieve"]:
            return [drf_permissions.IsAuthenticated(), IsContributor()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [drf_permissions.IsAuthenticated(), IsAuthor()]
        return [drf_permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """
        À la création, détermine le projet :
        - nested : via project_pk
        - flat   : via le champ project du serializer
        """
        project_pk = self.kwargs.get("project_pk")
        if project_pk:
            project = Project.objects.get(pk=project_pk)
        else:
            project = serializer.validated_data.get("project")
        serializer.save(author=self.request.user, project=project)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les commentaires d'une issue.

    - list/retrieve (flat)     : commentaires des issues des projets contrib.
    - list/retrieve (nested)   : commentaires d'une issue précise.
    - create (flat/nested)     : IsContributor
    - update/partial_update/destroy : IsAuthor
    """
    serializer_class = CommentSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Retourne les commentaires visibles :
        - Swagger : queryset vide
        - nested (issue_pk) : commentaires de cette issue si contributeur
        - flat list         : tous les commentaires pour les projets contrib.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Comment.objects.none()

        qs = Comment.objects.all().distinct()
        issue_pk = self.kwargs.get("issue_pk")
        if issue_pk:
            qs = qs.filter(
                issue__id=issue_pk,
                issue__project__contributors__user=self.request.user
            )
        elif self.action == "list":
            qs = qs.filter(issue__project__contributors__user=self.request.user)
        return qs

    def perform_create(self, serializer):
        """
        Lors de la création :
        - nested : récupère l'issue via issue_pk
        - flat   : issue fourni dans le payload
        """
        issue_id = self.kwargs.get("issue_pk")
        if issue_id:
            issue = Issue.objects.get(pk=issue_id)
        else:
            issue = serializer.validated_data.get("issue")
        serializer.save(author=self.request.user, issue=issue)

    def get_permissions(self):
        """
        Permissions selon l'action :
        - create, list, retrieve : IsContributor
        - update, partial_update, destroy : IsAuthor
        """
        if self.action in ["create", "list", "retrieve"]:
            return [drf_permissions.IsAuthenticated(), IsContributor()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [drf_permissions.IsAuthenticated(), IsAuthor()]
        return [drf_permissions.IsAuthenticated()]
