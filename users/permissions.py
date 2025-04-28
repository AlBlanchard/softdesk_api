from rest_framework.permissions import BasePermission


class IsSelf(BasePermission):
    """
    Autorise uniquement l'utilisateur connecté à voir ou modifier son propre profil.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user
