import os
import sys
import django

# Ajouter la racine du projet au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "softdesk.settings")
django.setup()

# A garder après la configuration de Django, sinon ça marche pas
from projects.models import Project
from users.models import CustomUser


def clean_fake_data():
    print("Suppression des projets, issues et commentaires...")

    Project.objects.filter(title__startswith="Projet Test").delete()
    print("Toutes les données tests supprimées.")

    CustomUser.objects.filter(username="authortest").delete()
    CustomUser.objects.filter(username="contributortest").delete()


if __name__ == "__main__":
    clean_fake_data()
