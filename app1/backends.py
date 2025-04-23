from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """
    Autentica usando la dirección de correo electrónico.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Intenta encontrar un usuario con el email o username proporcionado
            user = UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except UserModel.DoesNotExist:
            # Ejecuta el hash de contraseña de todos modos para evitar ataques de temporización
            UserModel().set_password(password)
            return None
        except UserModel.MultipleObjectsReturned:
            # Si hay múltiples usuarios con el mismo email (no debería pasar si email es unique)
            # Intenta encontrar por username exacto
            try:
                user = UserModel.objects.get(username__iexact=username)
            except UserModel.DoesNotExist:
                return None # No se encontró usuario único

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None