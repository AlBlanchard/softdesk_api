from rest_framework import serializers
from .models import Project, Contributor, Issue, Comment
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Project
        fields = ["id", "title", "description", "type", "author", "created_time"]
        read_only_fields = ["id", "author", "created_time"]


class ContributorSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    project = serializers.ReadOnlyField(source="project.id")

    class Meta:
        model = Contributor
        fields = ["id", "user", "project", "created_time"]
        read_only_fields = ["id", "user", "project", "created_time"]


class IssueSerializer(serializers.ModelSerializer):
    author_user = serializers.ReadOnlyField(source="author_user.username")
    assignee_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "tag",
            "priority",
            "status",
            "project",
            "author_user",
            "assignee_user",
            "created_time",
        ]
        read_only_fields = ["id", "author_user", "created_time"]


class CommentSerializer(serializers.ModelSerializer):
    author_user = serializers.ReadOnlyField(source="author_user.username")
    issue = serializers.ReadOnlyField(source="issue.id")

    class Meta:
        model = Comment
        fields = ["id", "description", "author_user", "issue", "created_time"]
        read_only_fields = ["id", "author_user", "issue", "created_time"]
