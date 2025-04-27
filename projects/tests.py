from urllib import response
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from projects.models import Project, Contributor, Issue, Comment
from rest_framework_simplejwt.tokens import RefreshToken
from .constants import ProjectType, Priority, Tag, Status


class ProjectPermissionTests(APITestCase):

    def setUp(self):
        self.user_author = User.objects.create_user(username="author", password="pass")
        self.user_contributor = User.objects.create_user(
            username="contributor", password="pass"
        )
        self.user_stranger = User.objects.create_user(
            username="stranger", password="pass"
        )

        self.project = Project.objects.create(
            title="Mon Super Projet",
            description="Description du super projet",
            type="Back-End",
            author=self.user_author,
        )

        self.project.refresh_from_db()  # Refresh pour que le test ait la dernière version de l'objet

        Contributor.objects.create(user=self.user_author, project=self.project)
        Contributor.objects.create(user=self.user_contributor, project=self.project)

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_author_can_update_project(self):
        self.authenticate(self.user_author)
        url = reverse("api:project-detail", args=[int(self.project.id)])
        response = self.client.patch(url, {"title": "Nouveau Titre"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contributor_cannot_update_project(self):
        self.authenticate(self.user_contributor)
        url = reverse("api:project-detail", args=[int(self.project.id)])
        response = self.client.patch(url, {"title": "Hacking Attempt"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stranger_cannot_access_project(self):
        self.authenticate(self.user_stranger)
        url = reverse("api:project-detail", args=[int(self.project.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_contributor_can_view_project(self):
        self.authenticate(self.user_contributor)
        url = reverse("api:project-detail", args=[int(self.project.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class IssuePermissionTests(APITestCase):

    def setUp(self):
        self.user_author = User.objects.create_user(username="author", password="pass")
        self.user_contributor = User.objects.create_user(
            username="contributor", password="pass"
        )
        self.user_stranger = User.objects.create_user(
            username="stranger", password="pass"
        )

        self.project = Project.objects.create(
            title="Projet Test",
            description="Test",
            type="Back-End",
            author=self.user_author,
        )
        Contributor.objects.create(user=self.user_author, project=self.project)
        Contributor.objects.create(user=self.user_contributor, project=self.project)

        self.authenticate(self.user_contributor)

    def authenticate(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_contributor_can_create_issue(self):
        url = reverse("api:issue-list")
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
        self.authenticate(self.user_stranger)

        url = reverse("api:issue-list")
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
        url = reverse("api:issue-detail", args=[issue.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Bug visible")

    def test_contributor_cannot_update_issue(self):
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

        self.authenticate(self.user_contributor)  # Pas l'auteur
        url = reverse("api:issue-detail", args=[issue.id])

        response = self.client.patch(url, {"title": "HACKED"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_update_issue(self):
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
        url = reverse("api:issue-detail", args=[issue.id])

        response = self.client.patch(
            url, {"title": "Titre modifié par l'auteur"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Titre modifié par l'auteur")

    def test_stranger_cannot_view_issue(self):
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
        url = reverse("api:issue-detail", args=[issue.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class CommentPermissionTests(APITestCase):

    def setUp(self):
        self.user_author = User.objects.create_user(username="author", password="pass")
        self.user_contributor = User.objects.create_user(username="contributor", password="pass")
        self.user_stranger = User.objects.create_user(username="stranger", password="pass")

        self.project = Project.objects.create(
            title="Projet Test",
            description="Description test",
            type="Back-End",
            author=self.user_author
        )

        self.issue = Issue.objects.create(
            title="Bug visible",
            description="Un bug",
            tag="Bug",
            priority="High",
            project=self.project,
            author=self.user_author,
            assignee_user=self.user_author
        )

        Contributor.objects.create(user=self.user_author, project=self.project)
        Contributor.objects.create(user=self.user_contributor, project=self.project)

        self.comment = Comment.objects.create(
            description="Premier commentaire",
            author=self.user_author,
            issue=self.issue
        )

    def authenticate(self, user):
        """Authentification helper pour simuler l'utilisateur connecté."""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_contributor_can_create_comment(self):
        self.authenticate(self.user_contributor)
        url = reverse("api:comment-list")  # Utilise le nom du router pour les commentaires

        data = {
            "description": "Nouveau commentaire",
            "issue": self.issue.id
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_contributor_can_view_comment(self):
        self.authenticate(self.user_contributor)
        url = reverse("api:comment-detail", args=[self.comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contributor_cannot_update_comment(self):
        """
        Vérifie qu'un contributeur ne peut pas modifier un commentaire qu'il n'a pas créé.
        """
        self.authenticate(self.user_contributor)
        url = reverse("api:comment-detail", args=[str(self.comment.id)])
        data = {"description": "Tentative de modification interdite"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stranger_cannot_create_comment(self):
        self.authenticate(self.user_stranger)
        url = reverse("api:comment-list")
        data = {
            "description": "Je ne devrais pas pouvoir poster ce commentaire.",
            "issue": self.issue.id,  
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_update_comment(self):
        self.authenticate(self.user_author)
        url = reverse("api:comment-detail", args=[self.comment.id])
        updated_data = {
            "description": "Nouveau contenu du commentaire"
        }
        response = self.client.patch(url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Recharge l'objet en DB et vérifie que la modification est effective
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.description, "Nouveau contenu du commentaire")



