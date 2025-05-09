from django.contrib.auth.backends import BaseBackend
from django.db.models import Q
from .models import CustomUser


class CustomUserAuthenticationBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Custom authentication logic for authenticating users based on 
        email, memberID, or phone_number along with password.
        """
        if username is None or password is None:
            return None

        # Attempt to find the user by email, memberID, or phone_number
        user = CustomUser.objects.filter(
            Q(email=username) | Q(memberID=username) | Q(phone_number=username)
        ).first()

        if user and user.check_password(password):
            # Specify the backend attribute to avoid ValueError
            user.backend = f"{self.__module__}.{self.__class__.__name__}"
            return user
        return None

    def get_user(self, user_id):
        """
        Retrieves a user by their ID.
        """
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None


