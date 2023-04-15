import logging

from django.test import TestCase
from rest_framework.authtoken.models import Token

from accounts.models import User


class TestUser:
    username = 'TestUser'
    first_name = 'Test'
    last_name = 'User'
    email = 'testuser@mail.com'
    password = 'qnjCmk27yzKTCWWiwdYH'
    slug = 'test'
    new_password = 'L0x60&fq!^ni'
    weak_password = '123'

    @classmethod
    def create_user(cls, username=None, first_name=None, last_name=None, email=None, password=None):
        user = User.objects.create_user(
            username=username if username else cls.username,
            first_name=first_name if first_name else cls.first_name,
            last_name=last_name if last_name else cls.last_name,
            email=email if email else cls.email,
            password=password if password else cls.password,
        )
        return user

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
