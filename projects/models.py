import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    # Enum du type de projet -> A SORTIR(constants.py)
    class ProjectType(models.TextChoices):
        BACK_END = "Back-End", "Back-End"
        FRONT_END = "Front-End", "Front-End"
        IOS = "iOS", "iOS"
        ANDROID = "Android", "Android"

    title = models.CharField(max_length=128)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=ProjectType.choices)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Contributor(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="contributions"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="contributors"
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Un même user ne peut contribuer qu'une fois au même projet
        unique_together = (
            "user",
            "project",
        )

    def __str__(self):
        return f"{self.user.username} -> {self.project.title}"


class Issue(models.Model):
    class Priority(models.TextChoices):
        LOW = "Low", "Low"
        MEDIUM = "Medium", "Medium"
        HIGH = "High", "High"

    class Tag(models.TextChoices):
        BUG = "Bug", "Bug"
        FEATURE = "Feature", "Feature"
        TASK = "Task", "Task"

    class Status(models.TextChoices):
        TODO = "To Do", "To Do"
        IN_PROGRESS = "In Progress", "In Progress"
        FINISHED = "Finished", "Finished"

    title = models.CharField(max_length=128)
    description = models.TextField()
    tag = models.CharField(max_length=10, choices=Tag.choices)
    priority = models.CharField(max_length=10, choices=Priority.choices)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.TODO
    )

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="issues"
    )
    author_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="issues_created"
    )
    assignee_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issues_assigned",
    )

    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.project.title})"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    author_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire par {self.author_user.username} sur {self.issue.title}"
