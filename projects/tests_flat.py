from urllib import response
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from projects.models import Project, Contributor, Issue, Comment
from rest_framework_simplejwt.tokens import RefreshToken
from .constants import Priority, Tag, Status

from users.models import CustomUser as User


class ProjectPermissionTests(APITestCase):
    """
    Tests des permissions pour les opérations sur les projets.
    Vérifie que seuls les auteurs ou contributeurs autorisés peuvent lire et modifier.
    """

    def setUp(self):
        # Création des utilisateurs de test
        self.user_author = User.objects.create_user(
            username="author", password="pass", age=20
        )
        self.user_contributor = User.objects.create_user(
            username="contributor", password="pass", age=20
        )
        self.user_stranger = User.objects.create_user(
            username="stranger", password="pass", age=20
        )

        # Création d'un projet avec 'author' comme créateur
        self.project = Project.objects.create(
            title="Mon Super Projet",
            description="Description du super projet",
            type="Back-End",
            author=self.user_author,
        )
        # Refresh pour récupérer les relations mises à jour
        self.project.refresh_from_db()

        # Ajout des contributeurs au projet
        Contributor.objects.create(user=self.user_author, project=self.project)
        Contributor.objects.create(user=self.user_contributor, project=self.project)

    def authenticate(self, user):
        """
        Helper pour authentifier un utilisateur via JWT dans les tests.
        """
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        # Ajout du header Authorization pour les requêtes
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_author_can_update_project(self):
        """
        L'auteur du projet peut modifier son titre.
        """
        self.authenticate(self.user_author)
        url = reverse("projects:project-detail", args=[int(self.project.id)])
        response = self.client.patch(url, {"title": "Nouveau Titre"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contributor_cannot_update_project(self):
        """
        Un contributeur non-auteur ne peut pas modifier le projet.
        """
        self.authenticate(self.user_contributor)
        url = reverse("projects:project-detail", args=[int(self.project.id)])
        response = self.client.patch(url, {"title": "Hacking Attempt"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stranger_cannot_access_project(self):
        """
        Un utilisateur n'ayant aucun lien avec le projet reçoit un 404.
        """
        self.authenticate(self.user_stranger)
        url = reverse("projects:project-detail", args=[int(self.project.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_contributor_can_view_project(self):
        """
        Un contributeur peut lire les détails du projet.
        """
        self.authenticate(self.user_contributor)
        url = reverse("projects:project-detail", args=[int(self.project.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class IssuePermissionTests(APITestCase):
    """
    Tests des permissions pour les opérations sur les issues.
    Vérifie que les contributeurs peuvent créer et lire des issues,
    et que seuls les auteurs peuvent les modifier.
    """

    def setUp(self):
        # Création des utilisateurs
        self.user_author = User.objects.create_user(
            username="author", password="pass", age=20
        )
        self.user_contributor = User.objects.create_user(
            username="contributor", password="pass", age=20
        )
        self.user_stranger = User.objects.create_user(
            username="stranger", password="pass", age=20
        )

        # Création d'un projet de test
        self.project = Project.objects.create(
            title="Projet Test",
            description="Test",
            type="Back-End",
            author=self.user_author,
        )
        # Ajout des contributeurs
        Contributor.objects.create(user=self.user_author, project=self.project)
        Contributor.objects.create(user=self.user_contributor, project=self.project)

        # Authentifier par défaut le contributeur
        self.authenticate(self.user_contributor)

    def authenticate(self, user):
        """
        Helper JWT pour authentifier un utilisateur.
        """
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_contributor_can_create_issue(self):
        """
        Un contributeur peut créer une nouvelle issue.
        """
        url = reverse("projects:issue-list")
        data = {
            "title": "Bug à corriger",
            "description": "Il y a un bug",
            "tag": Tag.BUG,
            "priority": Priority.HIGH,
            "status": Status.TODO,
            "project": self.project.id,
            "assignee_user": self.user_author.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Issue.objects.count(), 1)

    def test_stranger_cannot_create_issue(self):
        """
        Un utilisateur non-contributeur ne peut pas créer d'issue.
        """
        self.authenticate(self.user_stranger)
        url = reverse("projects:issue-list")
        data = {
            "title": "Tentative interdite",
            "description": "Un étranger tente de créer une issue.",
            "tag": Tag.BUG,
            "priority": Priority.HIGH,
            "status": Status.TODO,
            "project": self.project.id,
            "assignee_user": self.user_author.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Issue.objects.count(), 0)

    def test_contributor_can_view_issue(self):
        """
        Un contributeur peut lire une issue existante.
        """
        issue = Issue.objects.create(
            title="Bug visible",
            description="Un bug qu'on peut lire",
            tag=Tag.BUG,
            priority=Priority.MEDIUM,
            status=Status.TODO,
            project=self.project,
            author=self.user_author,
            assignee_user=self.user_contributor,
        )
        self.authenticate(self.user_contributor)
        url = reverse("projects:issue-detail", args=[issue.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Bug visible")

    def test_contributor_cannot_update_issue(self):
        """
        Un contributeur non-auteur ne peut pas modifier l'issue.
        """
        issue = Issue.objects.create(
            title="Modifiable seulement par l’auteur",
            description="Tentative de modification interdite",
            tag=Tag.TASK,
            priority=Priority.LOW,
            status=Status.TODO,
            project=self.project,
            author=self.user_author,
            assignee_user=self.user_contributor,
        )
        self.authenticate(self.user_contributor)
        url = reverse("projects:issue-detail", args=[issue.id])
        response = self.client.patch(url, {"title": "HACKED"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_update_issue(self):
        """
        L'auteur de l'issue peut la modifier.
        """
        issue = Issue.objects.create(
            title="Issue modifiable",
            description="Auteur uniquement",
            tag=Tag.TASK,
            priority=Priority.HIGH,
            status=Status.TODO,
            project=self.project,
            author=self.user_author,
            assignee_user=self.user_contributor,
        )
        self.authenticate(self.user_author)
        url = reverse("projects:issue-detail", args=[issue.id])
        response = self.client.patch(
            url, {"title": "Titre modifié par l'auteur"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Titre modifié par l'auteur")

    def test_stranger_cannot_view_issue(self):
        """
        Un utilisateur non-contributeur reçoit un 403 sur la lecture d'une issue.
        """
        issue = Issue.objects.create(
            title="Bug privé",
            description="Visibilité restreinte",
            tag=Tag.BUG,
            priority=Priority.LOW,
            status=Status.TODO,
            project=self.project,
            author=self.user_author,
            assignee_user=self.user_contributor,
        )
        self.authenticate(self.user_stranger)
        url = reverse("projects:issue-detail", args=[issue.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentPermissionTests(APITestCase):
    """
    Tests des permissions pour les opérations sur les commentaires.
    Vérifie la création, la lecture et la modification selon le statut utilisateur.
    """

    def setUp(self):
        # Création des utilisateurs
        self.user_author = User.objects.create_user(
            username="author", password="pass", age=20
        )
        self.user_contributor = User.objects.create_user(
            username="contributor", password="pass", age=20
        )
        self.user_stranger = User.objects.create_user(
            username="stranger", password="pass", age=20
        )

        # Création d'un projet et d'une issue
        self.project = Project.objects.create(
            title="Projet Test",
            description="Description test",
            type="Back-End",
            author=self.user_author,
        )
        self.issue = Issue.objects.create(
            title="Bug visible",
            description="Un bug",
            tag=Tag.BUG,
            priority=Priority.HIGH,
            project=self.project,
            author=self.user_author,
            assignee_user=self.user_author,
        )
        # Ajout des contributeurs
        Contributor.objects.create(user=self.user_author, project=self.project)
        Contributor.objects.create(user=self.user_contributor, project=self.project)

        # Création initiale d'un commentaire
        self.comment = Comment.objects.create(
            description="Premier commentaire", author=self.user_author, issue=self.issue
        )

    def authenticate(self, user):
        """
        Helper JWT pour authentifier un utilisateur.
        """
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_contributor_can_create_comment(self):
        """
        Un contributeur peut ajouter un commentaire.
        """
        self.authenticate(self.user_contributor)
        url = reverse(
            "projects:comment-list"
        )  # Route vers la création de commentaires
        data = {"description": "Nouveau commentaire", "issue": self.issue.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_contributor_can_view_comment(self):
        """
        Un contributeur peut lire un commentaire existant.
        """
        self.authenticate(self.user_contributor)
        url = reverse("projects:comment-detail", args=[self.comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contributor_cannot_update_comment(self):
        """
        Un contributeur non-auteur ne peut pas modifier un commentaire.
        """
        self.authenticate(self.user_contributor)
        url = reverse("projects:comment-detail", args=[str(self.comment.id)])
        data = {"description": "Tentative de modification interdite"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stranger_cannot_create_comment(self):
        """
        Un utilisateur non-contributeur ne peut pas créer de commentaire.
        """
        self.authenticate(self.user_stranger)
        url = reverse("projects:comment-list")
        data = {
            "description": "Je ne devrais pas pouvoir poster ce commentaire.",
            "issue": self.issue.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_update_comment(self):
        """
        L'auteur du commentaire peut le modifier.
        """
        self.authenticate(self.user_author)
        url = reverse("projects:comment-detail", args=[self.comment.id])
        updated_data = {"description": "Nouveau contenu du commentaire"}
        response = self.client.patch(url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Vérifie la persistance de la modification
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.description, "Nouveau contenu du commentaire")
