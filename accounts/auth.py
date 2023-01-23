from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrUsernameAuth(ModelBackend):
    """
    User authentication by email or username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(Q(email__iexact=username) | Q(username__iexact=username))
        except user_model.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
