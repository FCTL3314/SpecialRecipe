from datetime import timedelta
from uuid import uuid4
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from accounts.models import EmailVerification, User


class UserRegistrationViewTestCase(TestCase):

    def setUp(self):
        self.path = reverse('accounts:registration')
        self.data = {
            'username': 'TestUser',
            'email': 'testuser@mail.com',
            'password1': 'qnjCmk27yzKTCWWiwdYH',
            'password2': 'qnjCmk27yzKTCWWiwdYH',
        }

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Special Recipe | Registration')
        self.assertTemplateUsed(response, 'accounts/registration.html')

    def test_user_registration_get(self):
        response = self.client.get(self.path)

        self._common_tests(response)

    def test_user_registration_post_success(self):
        username = self.data['username']

        self.assertFalse(User.objects.filter(username=username).exists())

        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertTrue(User.objects.filter(username=username).exists())

    def test_user_registration_post_short_username(self):
        username = 'abc'
        short_username_data = self.data.copy()
        short_username_data['username'] = username

        response = self.client.post(self.path, short_username_data)

        self._common_tests(response)
        self.assertContains(response, 'Ensure this value has at least 4 characters (it has 3).')
        self.assertFalse(User.objects.filter(username=username))

    def test_user_registration_post_username_taken(self):
        username = self.data['username']
        User.objects.create(username=username)

        response = self.client.post(self.path, self.data)

        self._common_tests(response)
        self.assertContains(response, 'A user with that username already exists.')

    def test_user_registration_post_email_taken(self):
        email = self.data['email']
        User.objects.create(email=email)

        response = self.client.post(self.path, self.data)

        self._common_tests(response)
        self.assertContains(response, 'User with this Email already exists.')

    def test_user_registration_post_weak_password(self):
        password = '123456'
        weak_password_data = self.data.copy()
        weak_password_data['password1'] = password
        weak_password_data['password2'] = password

        response = self.client.post(self.path, weak_password_data)

        self._common_tests(response)
        self.assertContains(response, 'This password is too short. It must contain at least 8 characters.')
        self.assertContains(response, 'This password is too common.')
        self.assertContains(response, 'This password is entirely numeric.')


class UserLoginViewTestCase(TestCase):

    def setUp(self):
        self.path = reverse('accounts:login')
        self.data = {
            'username': 'TestUser',
            'password': 'qnjCmk27yzKTCWWiwdYH',
        }
        User.objects.create_user(
            username=self.data['username'],
            email='testuser@mail.com',
            password=self.data['password']
        )

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Special Recipe | Login')
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_user_login_get(self):
        response = self.client.get(self.path)

        self._common_tests(response)

    def test_user_login_post_with_username(self):
        username = self.data['username']

        self.assertTrue(User.objects.filter(username=username).exists())

        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('index'))

    def test_user_login_post_via_email(self):
        email = 'testuser@mail.com'
        email_data = self.data.copy()
        email_data['username'] = email

        self.assertTrue(User.objects.filter(email=email).exists())

        response = self.client.post(self.path, email_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('index'))

    def test_user_login_post_with_remember_be(self):
        username = self.data['username']

        data_with_remember_me = self.data.copy()
        data_with_remember_me['remember_me'] = 'on'

        self.assertTrue(User.objects.filter(username=username).exists())

        response = self.client.post(self.path, data_with_remember_me)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.cookies['sessionid']['max-age'], 1209600)
        self.assertRedirects(response, reverse('index'))

    def test_user_login_post_without_remember_me(self):
        username = self.data['username']

        self.assertTrue(User.objects.filter(username=username).exists())

        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.cookies['sessionid']['max-age'], 1800)
        self.assertRedirects(response, reverse('index'))

    def test_user_login_post_invalid_username(self):
        username = 'InvalidUsername'
        invalid_username_data = self.data.copy()
        invalid_username_data['username'] = username

        self.assertFalse(User.objects.filter(username=username).exists())

        response = self.client.post(self.path, invalid_username_data)

        self._common_tests(response)
        self.assertContains(response, 'Invalid username/email or password.')

    def test_user_login_post_invalid_password(self):
        password = 'InvalidPassword'
        invalid_password_data = self.data.copy()
        invalid_password_data['password'] = password

        self.assertTrue(User.objects.filter(username=invalid_password_data['username']).exists())

        response = self.client.post(self.path, invalid_password_data)

        self._common_tests(response)
        self.assertContains(response, 'Invalid username/email or password.')


class SendVerificationEmailViewTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='TestUser',
            email='testuser@mail.com',
            password='qnjCmk27yzKTCWWiwdYH',
        )
        self.client.login(username='TestUser', email='testuser@mail.com', password='qnjCmk27yzKTCWWiwdYH')
        self.path = reverse('accounts:send-verification-email', args={self.user.email})

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Sending a verification email')
        self.assertTemplateUsed(response, 'accounts/email_verification/sending_information.html')

    def test_view_success(self):
        self.assertFalse(EmailVerification.objects.filter(user=self.user))

        response = self.client.get(self.path)

        self._common_tests(response)
        self.assertContains(response, f'We send an email to {self.user.email}.')

        email_verification = EmailVerification.objects.filter(user=self.user)

        self.assertTrue(email_verification)
        self.assertEqual(email_verification.first().expiration.date(), (now() + timedelta(hours=48)).date())

    def test_view_previous_email_not_expired(self):
        expiration = now() + timedelta(hours=48)
        EmailVerification.objects.create(code=uuid4(), user=self.user, expiration=expiration)

        self.assertTrue(EmailVerification.objects.first())

        response = self.client.get(self.path)

        self._common_tests(response)
        self.assertContains(response, f'The last sent email has not expired yet, use it to verify your email address.')

    def test_view_user_already_verified(self):
        self.user.is_verified = True
        self.user.save()

        response = self.client.get(self.path)

        self._common_tests(response)
        self.assertContains(response, f'You have already verified your email.')
