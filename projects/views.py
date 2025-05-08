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
    ViewSet pour gérer les projets.
    """

    serializer_class = ProjectSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Retourne la liste des projets de l'utilisateur connecté.
        """
        # drf-yasg schema generation => on retourne un queryset neutre (sinon erreur)
        if getattr(self, 'swagger_fake_view', False):
            return Project.objects.none()
        
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
    ViewSet pour gérer les contributeurs d'un projet.
    """

    serializer_class = ContributorSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        # si drf-yasg fait son boulot, on évite tout filtrage
        if getattr(self, 'swagger_fake_view', False):
            return Contributor.objects.none()

        project_id = self.kwargs.get("project_pk")
        # attention à get() plutôt que [] pour éviter KeyError
        if project_id is None:
            return Contributor.objects.all()
        return Contributor.objects.filter(project__id=project_id)


# views.py

class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer

    def get_queryset(self):
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
        if self.action in ["create", "list", "retrieve"]:
            return [drf_permissions.IsAuthenticated(), IsContributor()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [drf_permissions.IsAuthenticated(), IsAuthor()]
        return [drf_permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        project_pk = self.kwargs.get("project_pk")
        if project_pk:
            project = Project.objects.get(pk=project_pk)
        else:
            project = serializer.validated_data.get("project")
        serializer.save(author=self.request.user, project=project)

    def perform_create(self, serializer):
        project_pk = self.kwargs.get("project_pk")
        if project_pk:
            project = Project.objects.get(pk=project_pk)
        else:
            project = serializer.validated_data.get("project")
        serializer.save(author=self.request.user, project=project)



class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
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
        issue_id = self.kwargs.get("issue_pk")
        if issue_id:
            issue = Issue.objects.get(pk=issue_id)
        else:
            issue = serializer.validated_data.get("issue")
        serializer.save(author=self.request.user, issue=issue)

    def get_permissions(self):
        if self.action in ["create", "list", "retrieve"]:
            return [drf_permissions.IsAuthenticated(), IsContributor()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [drf_permissions.IsAuthenticated(), IsAuthor()]
        return [drf_permissions.IsAuthenticated()]