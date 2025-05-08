from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import (
    ProjectViewSet,
    ContributorViewSet,
    IssueViewSet,
    CommentViewSet,
)

# flat routes
router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"contributors", ContributorViewSet, basename="contributor")
router.register(r"issues", IssueViewSet, basename="issue")
router.register(r"comments", CommentViewSet, basename="comment")

# nested /projects/{project_pk}
projects_router = NestedDefaultRouter(router, r"projects", lookup="project")
projects_router.register(
    r"contributors", ContributorViewSet, basename="project-contributors"
)
projects_router.register(r"issues", IssueViewSet, basename="project-issues")

# nested /projects/{project_pk}/issues/{issue_pk}
issues_router = NestedDefaultRouter(projects_router, r"issues", lookup="issue")
issues_router.register(r"comments", CommentViewSet, basename="issue-comments")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(projects_router.urls)),
    path("", include(issues_router.urls)),
]