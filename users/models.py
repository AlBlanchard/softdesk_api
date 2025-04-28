from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class CustomUser(AbstractUser):
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
        help_text="Âge de l'utilisateur",
    )
    can_be_contacted = models.BooleanField(
        default=False, help_text="L'utilisateur accepte d'être contacté."
    )
    can_data_be_shared = models.BooleanField(
        default=False,
        help_text="L'utilisateur accepte que ses données soient partagées.",
    )

    def __str__(self):
        return self.username
