import os
import django
import random
import sys

# Ajoute la racine du projet au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "softdesk.settings")
django.setup()

from projects.models import Project, Contributor, Issue, Comment
from users.models import CustomUser


def generate_data():

    def create_author():
        user, created = CustomUser.objects.get_or_create(
            username="authortest",
            defaults={
                "age": 105,
                "can_be_contacted": True,
                "can_data_be_shared": True,
            },
        )

        if created:
            user.set_password("djangotest10")  # hash correctement le mot de passe
            user.save()
        return user

    def create_contributor():
        user, created = CustomUser.objects.get_or_create(
            username="contributortest",
            defaults={
                "age": 20,
                "can_be_contacted": True,
                "can_data_be_shared": True,
            },
        )

        if created:
            user.set_password("djangotest20")
            user.save()
        return user

    user = create_author()
    user_contributor = create_contributor()

    issue_titles = [
        "Bug critique",
        "Amélioration UI",
        "Erreur serveur",
        "Ajout fonctionnalité",
        "Refactor code",
    ]
    comment_texts = [
        "C'est une bonne idée.",
        "À corriger rapidement !",
        "Je propose une autre solution.",
        "Vu et validé.",
        "Peut-être à revoir.",
    ]

    for i in range(30):
        project = Project.objects.create(
            title=f"Projet Test {i+1}",
            description="Projet généré pour tester la pagination, issues et commentaires.",
            type=random.choice(["Back-End", "Front-End", "iOS", "Android"]),
            author=user,
        )
        Contributor.objects.create(user=user, project=project)
        contributor_or_not = random.choice([True, False])
        if contributor_or_not:
            Contributor.objects.create(user=user_contributor, project=project)

        for _ in range(random.randint(1, 5)):
            issue = Issue.objects.create(
                title=random.choice(issue_titles),
                description="Description automatique d'issue.",
                tag=random.choice(["Bug", "Feature", "Task"]),
                priority=random.choice(["Low", "Medium", "High"]),
                status=random.choice(["To Do", "In Progress", "Finished"]),
                project=project,
                author=user,
                assignee_user=user,
            )

            for _ in range(random.randint(1, 3)):
                Comment.objects.create(
                    description=random.choice(comment_texts), author=user, issue=issue
                )

    print("30 projets, avec issues et commentaires créés avec succès !")


if __name__ == "__main__":
    generate_data()
