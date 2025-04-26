from django.db import models

class ProjectType(models.TextChoices):
    BACK_END = "Back-End", "Back-End"
    FRONT_END = "Front-End", "Front-End"
    IOS = "iOS", "iOS"
    ANDROID = "Android", "Android"

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