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
from common.tests import DisableLoggingMixin, TestUser

test_user = TestUser()


class UserTestCase(DisableLoggingMixin, APITestCase):

    def setUp(self):
        super().setUp()

        self.user = test_user.create_user()
        self.token = test_user.get_user_token(self.user)

        self.data = {
            'username': 'New' + test_user.username,
            'first_name': 'New' + test_user.first_name,
            'last_name': 'New' + test_user.last_name,
            'email': 'New' + test_user.email,
        }
        self.list_path = reverse('api:accounts:users-list')
        self.me_path = reverse('api:accounts:users-me')
        self.login_path = reverse('api:accounts:login')
        self.logout_path = reverse('api:accounts:logout')

    def test_user_me(self):
        response = self.client.get(self.me_path, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.username, test_user.username)
        self.assertEqual(self.user.first_name, test_user.first_name)
        self.assertEqual(self.user.last_name, test_user.last_name)
        self.assertEqual(self.user.email, test_user.email)

    def test_user_create(self):
        user_create_data = self.data.copy()
        del user_create_data['first_name']
        del user_create_data['last_name']
        user_create_data['password'] = test_user.password

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
            'username': test_user.username,
            'password': test_user.password,
        }

        response = self.client.post(self.login_path, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_login_bad_request(self):
        data = {
            'username': test_user.username,
            'password': 'wrong_password',
        }

        response = self.client.post(self.login_path, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_logout(self):
        response = self.client.post(self.logout_path, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(user=self.user).exists())


class PasswordResetTestCase(APITestCase):

    def setUp(self):
        self.user = test_user.create_user()
        self.token = test_user.get_user_token(self.user)

        self.data = {'email': test_user.email}
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
            'new_password': test_user.new_password,
        }

        response = self.client.post(self.password_reset_confirm_path, reset_data, )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PasswordChangeTestCase(DisableLoggingMixin, APITestCase):

    def setUp(self):
        super().setUp()

        self.user = test_user.create_user()
        self.token = test_user.get_user_token(self.user)

        self.data = {'current_password': test_user.password, 'new_password': test_user.new_password}
        self.token, self.created = Token.objects.get_or_create(user=self.user)
        self.path = reverse('api:accounts:users-set-password')

    def test_password_change_success(self):
        response = self.client.post(self.path, self.data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_password_change_bad_request(self):
        wrong_data = self.data.copy()
        wrong_data['new_password'] = test_user.invalid_password

        response = self.client.post(self.path, wrong_data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SendEmailVerificationTestCase(APITestCase):

    def setUp(self):
        self.user = test_user.create_user()
        self.token = test_user.get_user_token(self.user)

        self.data = {'email': test_user.email}
        self.token, self.created = Token.objects.get_or_create(user=self.user)
        self.path = reverse('api:accounts:send-verification-email')

    def test_send_email_verification(self):
        response = self.client.post(self.path, self.data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EmailVerificationTest(APITestCase):

    def setUp(self):
        self.user = test_user.create_user()
        self.token = test_user.get_user_token(self.user)

        expiration = now() + timedelta(hours=48)
        self.email_verification = EmailVerification.objects.create(code=uuid4(), user=self.user, expiration=expiration)

        self.data = {'email': test_user.email, 'code': self.email_verification.code}
        self.token, self.created = Token.objects.get_or_create(user=self.user)
        self.path = reverse('api:accounts:email-verification')

    def test_email_verification(self):
        response = self.client.patch(self.path, self.data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
