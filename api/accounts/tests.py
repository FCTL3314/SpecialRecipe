import logging
from datetime import timedelta
from uuid import uuid4

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.staticfiles.finders import find
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import now
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import EmailVerification, User

user_data = {
    'username': 'TestUser',
    'first_name': 'Test',
    'last_name': 'User',
    'email': 'testuser@mail.com',
    'password': 'qnjCmk27yzKTCWWiwdYH',
    'slug': 'test',
}


class UserTestCase(APITestCase):

    def _reduce_log_level(self):
        """Reduce the log level to avoid messages like 'bad_request'."""
        logger = logging.getLogger('django.request')
        self.previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

    def _restore_log_level(self):
        """Restore the normal log level."""
        logger = logging.getLogger('django.request')
        logger.setLevel(self.previous_level)

    def _create_user_and_token(self, username=user_data['username'], first_name=user_data['first_name'],
                               last_name=user_data['last_name'], email=user_data['email'],
                               password=user_data['password']):
        """Create a new user and auth token."""
        self.user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )
        self.token, self.created = Token.objects.get_or_create(user=self.user)

    def setUp(self) -> None:
        self._reduce_log_level()

        self._create_user_and_token()

        self.data = {
            'username': 'NewTestUser',
            'first_name': 'NewTest',
            'last_name': 'NewUser',
            'email': 'Newtestuser@mail.com',
        }
        self.list_path = reverse('api:accounts:users-list')
        self.me_path = reverse('api:accounts:users-me')
        self.login_path = reverse('api:accounts:login')
        self.logout_path = reverse('api:accounts:logout')

    def tearDown(self) -> None:
        self._restore_log_level()

    def test_user_me(self):
        response = self.client.get(self.me_path, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.username, user_data['username'])
        self.assertEqual(self.user.first_name, user_data['first_name'])
        self.assertEqual(self.user.last_name, user_data['last_name'])
        self.assertEqual(self.user.email, user_data['email'])

    def test_user_create(self):
        user_create_data = self.data.copy()
        del user_create_data['first_name']
        del user_create_data['last_name']
        user_create_data['password'] = user_data['password']

        self.assertFalse(User.objects.filter(username=user_create_data['username']).exists())

        response = self.client.post(self.list_path, user_create_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username=user_create_data['username']).exists())

    def test_user_update(self):
        self.assertFalse(self.user.image)

        with open(find('img/default_user_image.png'), 'rb') as image:
            self.data['image'] = image
            response = self.client.patch(self.me_path, self.data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.image)
        self.assertEqual(self.data['username'], self.user.username)
        self.assertEqual(self.data['first_name'], self.user.first_name)
        self.assertEqual(self.data['last_name'], self.user.last_name)
        self.assertEqual(self.data['email'], self.user.email)

    def test_user_login_success(self):
        data = {
            'username': user_data['username'],
            'password': user_data['password'],
        }

        response = self.client.post(self.login_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_login_bad_request(self):
        data = {
            'username': user_data['username'],
            'password': 'wrong_password',
        }

        response = self.client.post(self.login_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_logout(self):
        response = self.client.post(self.logout_path, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(user=self.user).exists())


class PasswordResetTestCase(APITestCase):

    def _create_user_and_token(self, username=user_data['username'], first_name=user_data['first_name'],
                               last_name=user_data['last_name'], email=user_data['email'],
                               password=user_data['password']):
        """Create a new user and auth token."""
        self.user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )
        self.token, self.created = Token.objects.get_or_create(user=self.user)

    def setUp(self) -> None:
        self._create_user_and_token()

        self.data = {'email': user_data['email']}
        self.password_reset_path = reverse('api:accounts:users-reset-password')
        self.password_reset_confirm_path = reverse('api:accounts:users-reset-password-confirm')

    def test_password_reset(self):
        response = self.client.post(self.password_reset_path, self.data)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_password_reset_confirm(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.id))
        token = PasswordResetTokenGenerator().make_token(self.user)
        reset_data = {
            'uid': uid,
            'token': token,
            'new_password': 'L0x60&fq!^ni',
        }

        response = self.client.post(self.password_reset_confirm_path, reset_data, )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PasswordChangeTestCase(APITestCase):

    def _reduce_log_level(self):
        """Reduce the log level to avoid messages like 'bad_request'."""
        logger = logging.getLogger('django.request')
        self.previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

    def _restore_log_level(self):
        """Restore the normal log level."""
        logger = logging.getLogger('django.request')
        logger.setLevel(self.previous_level)

    def _create_user_and_token(self, username=user_data['username'], first_name=user_data['first_name'],
                               last_name=user_data['last_name'], email=user_data['email'],
                               password=user_data['password']):
        """Create a new user and auth token."""
        self.user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )
        self.token, self.created = Token.objects.get_or_create(user=self.user)

    def setUp(self) -> None:
        self._reduce_log_level()

        self._create_user_and_token()

        self.data = {'current_password': user_data['password'], 'new_password': 'L0x60&fq!^ni'}
        self.token, self.created = Token.objects.get_or_create(user=self.user)
        self.path = reverse('api:accounts:users-set-password')

    def tearDown(self) -> None:
        self._restore_log_level()

    def test_password_change_success(self):
        response = self.client.post(self.path, self.data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_password_change_bad_request(self):
        wrong_data = self.data.copy()
        wrong_data['new_password'] = 'G*&njN'

        response = self.client.post(self.path, wrong_data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SendEmailVerificationTestCase(APITestCase):

    def _create_user_and_token(self, username=user_data['username'], first_name=user_data['first_name'],
                               last_name=user_data['last_name'], email=user_data['email'],
                               password=user_data['password']):
        """Create a new user and auth token."""
        self.user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )
        self.token, self.created = Token.objects.get_or_create(user=self.user)

    def setUp(self) -> None:
        self._create_user_and_token()

        self.data = {'email': user_data['email']}
        self.token, self.created = Token.objects.get_or_create(user=self.user)
        self.path = reverse('api:accounts:send-verification-email')

    def test_send_email_verification(self):
        response = self.client.post(self.path, self.data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EmailVerificationTest(APITestCase):

    def _create_user_and_token(self, username=user_data['username'], first_name=user_data['first_name'],
                               last_name=user_data['last_name'], email=user_data['email'],
                               password=user_data['password']):
        """Create a new user and auth token."""
        self.user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )
        self.token, self.created = Token.objects.get_or_create(user=self.user)

    def setUp(self) -> None:
        self._create_user_and_token()

        expiration = now() + timedelta(hours=48)
        self.email_verification = EmailVerification.objects.create(code=uuid4(), user=self.user, expiration=expiration)

        self.data = {'email': user_data['email'], 'code': self.email_verification.code}
        self.token, self.created = Token.objects.get_or_create(user=self.user)
        self.path = reverse('api:accounts:email-verification')

    def test_email_verification(self):
        response = self.client.patch(self.path, self.data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
