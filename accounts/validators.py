from django.core.exceptions import ValidationError

from accounts.models import User


def case_insensitive_existence_check(username):
    if User.objects.filter(username__iexact=username).exists():
        raise ValidationError('A user with that username already exists.')
