from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser as User
from projects.models import Project, Contributor, Issue, Comment
from .constants import Priority, Tag, Status


class BaseAPITestCase(APITestCase):
    """
    Classe de base pour factoriser la création d'utilisateurs et l'authentification JWT.

    Méthodes :
        create_user(username) : crée et renvoie un utilisateur avec mot de passe par défaut.
        authenticate(user) : authentifie l'utilisateur donné via header Bearer.
    """

    def create_user(self, username):
        """
        Crée un utilisateur CustomUser avec un mot de passe 'pass' et age de 20.
        """
        return User.objects.create_user(username=username, password="pass", age=20)

    def authenticate(self, user):
        """
        Génére un token JWT pour l'utilisateur et ajoute l'en-tête Authorization.
        """
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")


class ProjectPermissionTests(BaseAPITestCase):
    """
    Tests des permissions pour les endpoints imbriqués de projets.

    Vérifie que seul l'auteur peut modifier, qu'un contributeur ne peut pas,
    et qu'un étranger n'accède pas (404) tandis qu'un contributeur peut lire.
    """

    def setUp(self):
        # Préparation des utilisateurs
        self.user_author = self.create_user("author")
        self.user_contributor = self.create_user("contributor")
        self.user_stranger = self.create_user("stranger")

        # Création du projet avec author comme créateur
        self.project = Project.objects.create(
            title="Mon Super Projet",
            description="Description du super projet",
            type="Back-End",
            author=self.user_author,
        )
        # Ajout des contributeurs
        Contributor.objects.create(user=self.user_author, project=self.project)
        Contributor.objects.create(user=self.user_contributor, project=self.project)

    def test_author_can_update_project(self):
        """
        L'auteur du projet peut effectuer un PATCH sur le projet imbriqué.
        """
        self.authenticate(self.user_author)
        url = reverse("projects:project-detail", args=[self.project.id])
        response = self.client.patch(url, {"title": "Nouveau Titre"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contributor_cannot_update_project(self):
        """
        Un contributeur non-auteur reçoit un 403 sur l'update.
        """
        self.authenticate(self.user_contributor)
        url = reverse("projects:project-detail", args=[self.project.id])
        response = self.client.patch(url, {"title": "Hacking Attempt"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stranger_cannot_access_project(self):
        """
        Un utilisateur sans lien avec le projet obtient un 404.
        """
        self.authenticate(self.user_stranger)
        url = reverse("projects:project-detail", args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_contributor_can_view_project(self):
        """
        Un contributeur peut lire le projet imbriqué.
        """
        self.authenticate(self.user_contributor)
        url = reverse("projects:project-detail", args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class IssuePermissionTests(BaseAPITestCase):
    """
    Tests des permissions pour les endpoints d'issues imbriqués.

    Vérifie la création, la lecture et la mise à jour par contributeur/auteur/étranger.
    """

    def setUp(self):
        # Création des utilisateurs et du projet associé
        self.user_author = self.create_user("author")
        self.user_contributor = self.create_user("contributor")
        self.user_stranger = self.create_user("stranger")

        self.project = Project.objects.create(
            title="Projet Test",
            description="Test",
            type="Back-End",
            author=self.user_author,
        )
        Contributor.objects.create(user=self.user_author, project=self.project)
        Contributor.objects.create(user=self.user_contributor, project=self.project)

    def test_contributor_can_create_issue(self):
        """
        Un contributeur peut POST sur /projects/{pk}/issues/.
        """
        self.authenticate(self.user_contributor)
        url = reverse("projects:project-issues-list", args=[self.project.id])
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
        Un étranger obtient un 403 en POST sur issues imbriquées.
        """
        self.authenticate(self.user_stranger)
        url = reverse("projects:project-issues-list", args=[self.project.id])
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
        Un contributeur peut GET sur /projects/{pk}/issues/{id}/.
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
        url = reverse("projects:project-issues-detail", args=[self.project.id, issue.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Bug visible")

    def test_contributor_cannot_update_issue(self):
        """
        Un contributeur non-auteur reçoit un 403 sur PATCH.
        """
        issue = Issue.objects.create(
            title="Modifiable seulement par l'auteur",
            description="Tentative de modification interdite",
            tag=Tag.TASK,
            priority=Priority.LOW,
            status=Status.TODO,
            project=self.project,
            author=self.user_author,
            assignee_user=self.user_contributor,
        )
        self.authenticate(self.user_contributor)
        url = reverse("projects:project-issues-detail", args=[self.project.id, issue.id])
        response = self.client.patch(url, {"title": "HACKED"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_update_issue(self):
        """
        L'auteur reçoit un 200 sur PATCH.
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
        url = reverse("projects:project-issues-detail", args=[self.project.id, issue.id])
        response = self.client.patch(url, {"title": "Titre modifié par l'auteur"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Titre modifié par l'auteur")

    def test_stranger_cannot_view_issue(self):
        """
        Un étranger obtient un 404 sur GET imbriqué.
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
        url = reverse("projects:project-issues-detail", args=[self.project.id, issue.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentPermissionTests(BaseAPITestCase):

    def setUp(self):
        self.user_author = self.create_user("author")
        self.user_contributor = self.create_user("contributor")
        self.user_stranger = self.create_user("stranger")

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
            status=Status.TODO,
            project=self.project,
            author=self.user_author,
            assignee_user=self.user_author,
        )

        Contributor.objects.create(user=self.user_author, project=self.project)
        Contributor.objects.create(user=self.user_contributor, project=self.project)

        self.comment = Comment.objects.create(
            description="Premier commentaire", author=self.user_author, issue=self.issue
        )

    def test_contributor_can_create_comment(self):
        self.authenticate(self.user_contributor)
        url = (
            f"/api/projects/projects/{self.project.id}/issues/{self.issue.id}/comments/"
        )
        response = self.client.post(
            url, {"description": "Nouveau commentaire"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_contributor_can_view_comment(self):
        self.authenticate(self.user_contributor)
        url = f"/api/projects/projects/{self.project.id}/issues/{self.issue.id}/comments/{self.comment.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contributor_cannot_update_comment(self):
        self.authenticate(self.user_contributor)
        url = f"/api/projects/projects/{self.project.id}/issues/{self.issue.id}/comments/{self.comment.id}/"
        response = self.client.patch(url, {"description": "hack"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stranger_cannot_create_comment(self):
        self.authenticate(self.user_stranger)
        url = (
            f"/api/projects/projects/{self.project.id}/issues/{self.issue.id}/comments/"
        )
        response = self.client.post(
            url, {"description": "stranger fail"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_update_comment(self):
        self.authenticate(self.user_author)
        url = f"/api/projects/projects/{self.project.id}/issues/{self.issue.id}/comments/{self.comment.id}/"
        response = self.client.patch(
            url, {"description": "modification"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # on recharge et vérifie bien la nouvelle valeur
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.description, "modification")
