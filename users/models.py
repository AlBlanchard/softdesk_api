from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class CustomUser(AbstractUser):
    """
    Modèle utilisateur étendu basé sur AbstractUser.

    Attributs :
        age (int|None) : âge de l'utilisateur (>=1), optionnel.
        can_be_contacted (bool) : indique si l'utilisateur accepte d'être contacté.
        can_data_be_shared (bool) : indique si l'utilisateur accepte le partage de ses données.
    """
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
        help_text="Âge de l'utilisateur (doit être ≥ 1)",
    )
    can_be_contacted = models.BooleanField(
        default=False,
        help_text="Si vrai, l'utilisateur accepte d'être contacté.",
    )
    can_data_be_shared = models.BooleanField(
        default=False,
        help_text="Si vrai, l'utilisateur autorise le partage de ses données.",
    )

    def __str__(self):
        """
        Retourne une représentation textuelle de l'utilisateur.

        Utilise le nom d'utilisateur pour l'affichage.
        """
        return self.username