from rest_framework import viewsets
from rest_framework import permissions as drf_permissions
from .permissions import IsAuthor, IsContributor, IsAuthorOrReadOnly, IsIssueAuthor
from .models import Project, Contributor, Issue, Comment
from .serializers import (
    ProjectSerializer,
    ContributorSerializer,
    IssueSerializer,
    CommentSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les projets.
    """

    serializer_class = ProjectSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Retourne la liste des projets de l'utilisateur connecté.
        """
        user = self.request.user
        return Project.objects.filter(contributors__user=user).distinct()

    def get_permissions(self):
        """
        Retourne les permissions en fonction de l'action.
        """
        if self.action in ["update", "partial_update", "destroy"]:
            return [drf_permissions.IsAuthenticated(), IsAuthor()]
        elif self.action in ["retrieve", "list"]:
            return [drf_permissions.IsAuthenticated(), IsContributor()]
        return [drf_permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        # Ajoute l'auteur comme contributeur du projet
        Contributor.objects.create(user=self.request.user, project=project)


class ContributorViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les contributeurs.
    """

    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [drf_permissions.IsAuthenticated]


class IssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les issues.
    """

    serializer_class = IssueSerializer
    permission_classes = [
        drf_permissions.IsAuthenticated,
        IsContributor,
        IsAuthorOrReadOnly,
    ]

    def get_queryset(self):
        return Issue.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in ["create", "list", "retrieve"]:
            return [drf_permissions.IsAuthenticated(), IsContributor()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [drf_permissions.IsAuthenticated(), IsIssueAuthor()]
        return [drf_permissions.IsAuthenticated()]


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les commentaires.
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.all()

    def perform_create(self, serializer):
        issue_id = self.request.data.get("issue")
        issue = Issue.objects.get(id=issue_id)
        serializer.save(author=self.request.user, issue=issue)

    def get_permissions(self):
        if self.action in ["create", "list", "retrieve"]:
            return [drf_permissions.IsAuthenticated(), IsContributor()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [drf_permissions.IsAuthenticated(), IsAuthor()]

        return [drf_permissions.IsAuthenticated()]