import uuid
from django.db import models
from django.contrib.auth import get_user_model
from .constants import ProjectType, Priority, Tag, Status

# Récupère le modèle utilisateur configuré pour ce projet
User = get_user_model()


class Project(models.Model):
    """
    Représente un projet.

    Attributs :
        title (str) : titre du projet.
        description (str) : description détaillée du projet.
        type (str) : catégorie du projet, parmi ProjectType.
        author (User) : utilisateur ayant créé le projet.
        created_time (datetime) : horodatage de création du projet.
    """
    title = models.CharField(
        max_length=128,
        help_text="Titre du projet"
    )
    description = models.TextField(
        help_text="Description détaillée du projet"
    )
    type = models.CharField(
        max_length=20,
        choices=ProjectType.choices,
        help_text="Type ou catégorie du projet"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects",
        help_text="Utilisateur créateur du projet"
    )
    created_time = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure de création du projet"
    )

    def __str__(self):
        """
        Retourne la représentation textuelle du projet.
        """
        return self.title


class Contributor(models.Model):
    """
    Associe un utilisateur à un projet en tant que contributeur.

    Attributs :
        user (User) : contributeur.
        project (Project) : projet auquel l'utilisateur contribue.
        created_time (datetime) : horodatage de l'ajout du contributeur.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contributions",
        help_text="Utilisateur contributeur"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="contributors",
        help_text="Projet associé au contributeur"
    )
    created_time = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure d'ajout du contributeur"
    )

    class Meta:
        # Un utilisateur ne peut être contributeur qu'une seule fois par projet
        unique_together = (
            "user",
            "project",
        )

    def __str__(self):
        """
        Retourne une chaîne décrivant la relation contributeur-projet.
        """
        return f"{self.user.username} -> {self.project.title}"


class Issue(models.Model):
    """
    Modélise une issue (ticket) liée à un projet.

    Attributs :
        title (str) : titre de l'issue.
        description (str) : description du problème ou de la tâche.
        tag (str) : étiquette de l'issue, parmi Tag.
        priority (str) : niveau de priorité, parmi Priority.
        status (str) : état actuel, parmi Status.
        project (Project) : projet parent de l'issue.
        author (User) : utilisateur ayant créé l'issue.
        assignee_user (User|None) : utilisateur assigné (facultatif).
        created_time (datetime) : horodatage de création de l'issue.
    """
    title = models.CharField(
        max_length=128,
        help_text="Titre de l'issue"
    )
    description = models.TextField(
        help_text="Description détaillée de l'issue"
    )
    tag = models.CharField(
        max_length=10,
        choices=Tag.choices,
        help_text="Étiquette de l'issue"
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        help_text="Niveau de priorité"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        help_text="Statut actuel de l'issue"
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="issues",
        help_text="Projet auquel l'issue appartient"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="issues_created",
        help_text="Utilisateur ayant créé l'issue"
    )
    assignee_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issues_assigned",
        help_text="Utilisateur assigné pour traiter l'issue (optionnel)"
    )

    created_time = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure de création de l'issue"
    )

    def __str__(self):
        """
        Retourne le titre de l'issue suivi du nom du projet.
        """
        return f"{self.title} ({self.project.title})"


class Comment(models.Model):
    """
    Représente un commentaire attaché à une issue.

    Attributs :
        id (UUID) : identifiant unique du commentaire.
        description (str) : contenu du commentaire.
        author (User) : utilisateur ayant écrit le commentaire.
        issue (Issue) : issue associée au commentaire.
        created_time (datetime) : horodatage de création du commentaire.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identifiant unique du commentaire"
    )
    description = models.TextField(
        help_text="Texte du commentaire"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="Utilisateur auteur du commentaire"
    )
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="Issue à laquelle le commentaire est lié"
    )
    created_time = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure de création du commentaire"
    )

    def __str__(self):
        """
        Retourne une représentation concise du commentaire.
        """
        return f"Commentaire de {self.author.username} sur {self.issue.title}"
