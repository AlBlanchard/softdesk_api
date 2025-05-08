from rest_framework.permissions import BasePermission


class IsSelf(BasePermission):
    """
    Permission qui autorise uniquement l'interaction (lecture, modification) avec
    l'instance CustomUser correspondant à l'utilisateur authentifié.
    
    - has_object_permission : autorise si l'objet cible est l'utilisateur courant.
    """

    def has_object_permission(self, request, view, obj):
        """
        Vérifie que l'objet sur lequel porte l'opération est bien celui de l'utilisateur connecté.

        Args:
            request (Request) : requête HTTP contenant request.user.
            view (View) : instance de la vue en cours (non utilisé ici).
            obj (CustomUser) : instance du profil utilisateur ciblé.

        Returns:
            bool : True si obj est request.user, False sinon.
        """
        return obj == request.user
