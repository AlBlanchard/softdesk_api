from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import (
    ProjectViewSet,
    ContributorViewSet,
    IssueViewSet,
    CommentViewSet,
)

# --------------------------------------------------------------------
# Routeurs plats : exposent les endpoints CRUD indépendants
# --------------------------------------------------------------------
router = DefaultRouter()
# Projet : /projects/ et /projects/{id}/
router.register(r"projects", ProjectViewSet, basename="project")
# Contributeur : /contributors/ et /contributors/{id}/
router.register(r"contributors", ContributorViewSet, basename="contributor")
# Issue : /issues/ et /issues/{id}/
router.register(r"issues", IssueViewSet, basename="issue")
# Commentaire : /comments/ et /comments/{id}/
router.register(r"comments", CommentViewSet, basename="comment")

# --------------------------------------------------------------------
# Routeurs imbriqués sous /projects/{project_pk}/...
# --------------------------------------------------------------------
projects_router = NestedDefaultRouter(router, r"projects", lookup="project")
# Contributeurs d'un projet : /projects/{project_pk}/contributors/
projects_router.register(
    r"contributors", ContributorViewSet, basename="project-contributors"
)
# Issues d'un projet     : /projects/{project_pk}/issues/
projects_router.register(r"issues", IssueViewSet, basename="project-issues")

# --------------------------------------------------------------------
# Routeurs imbriqués sous /projects/{project_pk}/issues/{issue_pk}/...
# --------------------------------------------------------------------
issues_router = NestedDefaultRouter(projects_router, r"issues", lookup="issue")
# Commentaires d'une issue : /projects/{project_pk}/issues/{issue_pk}/comments/
issues_router.register(r"comments", CommentViewSet, basename="issue-comments")

# --------------------------------------------------------------------
# Inclusion des routeurs dans les URL patterns
# - Les deux sets (plats et imbriqués) coexistent
# --------------------------------------------------------------------
urlpatterns = [
    # Endpoints CRUD classiques
    path("", include(router.urls)),
    # Endpoints imbriqués projet->subresources
    path("", include(projects_router.urls)),
    # Endpoints imbriqués projet->issue->comments
    path("", include(issues_router.urls)),
]
