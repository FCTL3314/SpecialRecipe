import logging
from dataclasses import dataclass

from django.test import TestCase
from rest_framework.authtoken.models import Token

from accounts.models import User


@dataclass(frozen=True)
class TestUser:
    username: str = 'TestUser'
    first_name: str = 'Test'
    last_name: str = 'User'
    email: str = 'testuser@mail.com'
    password: str = 'qnjCmk27yzKTCWWiwdYH'
    slug: str = 'test'

    new_password: str = 'L0x60&fq!^ni'

    invalid_password: str = '123'
    invalid_username: str = 'abc'

    def create_user(self, **kwargs):
        defaults = {
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'password': self.password,
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    @staticmethod
    def get_user_token(user):
        token, created = Token.objects.get_or_create(user=user)
        return token


class DisableLoggingMixin(TestCase):
    def setUp(self):
        self._reduce_log_level()
        super().setUp()

    def tearDown(self):
        self._restore_log_level()
        super().tearDown()

    def _reduce_log_level(self):
        """Reduce the log level to avoid messages like 'bad_request'."""
        logger = logging.getLogger('django.request')
        self.previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

    def _restore_log_level(self):
        """Restore the normal log level."""
        logger = logging.getLogger('django.request')
        logger.setLevel(self.previous_level)
