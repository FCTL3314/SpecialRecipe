from datetime import timedelta
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.staticfiles.finders import find
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import now

from accounts.forms import EmailChangeForm
from accounts.models import EmailVerification, User
from common.tests import TestUser

test_user = TestUser()


class UserRegistrationViewTestCase(TestCase):

    def setUp(self):
        self.data = {
            'username': test_user.username,
            'email': test_user.email,
            'password1': test_user.password,
            'password2': test_user.password,
        }
        self.path = reverse('accounts:registration')

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
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

        user = User.objects.get(username=username)

        self.assertTrue(user.slug, user.username.lower())

    def test_user_registration_post_short_username(self):
        username = test_user.invalid_username

        data = self.data.copy()
        data['username'] = username

        response = self.client.post(self.path, data)

        self._common_tests(response)
        self.assertFormError(response, 'form', 'username', 'Ensure this value has at least 4 characters (it has 3).')
        self.assertFalse(User.objects.filter(username=username))

    def test_user_registration_post_username_taken(self):
        test_user.create_user()

        response = self.client.post(self.path, self.data)

        self._common_tests(response)
        self.assertFormError(response, 'form', 'username', 'A user with that username already exists.')

    def test_user_registration_post_email_taken(self):
        test_user.create_user()

        response = self.client.post(self.path, self.data)

        self._common_tests(response)
        self.assertFormError(response, 'form', 'email', 'User with this Email already exists.')

    def test_user_registration_post_weak_password(self):
        password = test_user.invalid_password

        data = self.data.copy()
        data['password1'] = password
        data['password2'] = password

        response = self.client.post(self.path, data)

        self._common_tests(response)
        errors = [
            'This password is too short. It must contain at least 8 characters.',
            'This password is too common.',
            'This password is entirely numeric.',
        ]
        self.assertFormError(response, 'form', 'password2', errors)


class UserLoginViewTestCase(TestCase):

    def setUp(self):
        self.data = {
            'username': test_user.username,
            'password': test_user.password,
        }
        self.user = test_user.create_user()
        self.path = reverse('accounts:login')

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_user_login_get(self):
        response = self.client.get(self.path)

        self._common_tests(response)

    def test_user_login_post_with_username(self):
        username = self.data['username']

        self.assertTrue(User.objects.filter(username=username).exists())

        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('accounts:profile', args=(self.user.slug,)))

    def test_user_login_post_via_email(self):
        data = self.data.copy()
        email = test_user.email
        data['username'] = email

        self.assertTrue(User.objects.filter(email=email).exists())

        response = self.client.post(self.path, data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('accounts:profile', args=(self.user.slug,)))

    def test_user_login_post_with_remember_be(self):
        username = self.data['username']

        data_with_remember_me = self.data.copy()
        data_with_remember_me['remember_me'] = 'on'

        self.assertTrue(User.objects.filter(username=username).exists())

        response = self.client.post(self.path, data_with_remember_me)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.cookies['sessionid']['max-age'], 1209600)
        self.assertRedirects(response, reverse('accounts:profile', args=(self.user.slug,)))

    def test_user_login_post_without_remember_me(self):
        username = self.data['username']

        self.assertTrue(User.objects.filter(username=username).exists())

        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.cookies['sessionid']['max-age'], 1800)
        self.assertRedirects(response, reverse('accounts:profile', args=(self.user.slug,)))

    def test_user_login_post_invalid_username(self):
        username = 'InvalidUsername'

        data = self.data.copy()
        data['username'] = username

        self.assertFalse(User.objects.filter(username=username).exists())

        response = self.client.post(self.path, data)

        self._common_tests(response)
        self.assertContains(response, 'The entered data is incorrect, please try again.')

    def test_user_login_post_invalid_password(self):
        password = 'InvalidPassword'

        data = self.data.copy()
        data['password'] = password

        self.assertTrue(User.objects.filter(username=data['username']).exists())

        response = self.client.post(self.path, data)

        self._common_tests(response)
        self.assertContains(response, 'The entered data is incorrect, please try again.')


class SendVerificationEmailViewTestCase(TestCase):

    def setUp(self):
        self.user = test_user.create_user()
        self.client.force_login(user=self.user)
        self.sending_interval = settings.EMAIL_SEND_INTERVAL_SECONDS
        self.expiration_hours = settings.EMAIL_EXPIRATION_HOURS
        self.path = reverse('accounts:send-verification-email', args=(self.user.email,))

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'accounts/email/email_verification_done.html')

    def test_view_success(self):
        self.assertFalse(EmailVerification.objects.filter(user=self.user))

        response = self.client.get(self.path)

        self._common_tests(response)
        self.assertContains(response, 'You\'re almost there! You will receive an email within a couple of minutes. '
                                      'Just click on the link in that email to complete your verification if you '
                                      'don\'t see it, you may need to check your spam folder.', html=True)

        email_verification = EmailVerification.objects.valid_user_verifications(self.user).order_by('-created')

        self.assertTrue(email_verification)
        self.assertEqual(
            email_verification.first().expiration.date(),
            (now() + timedelta(hours=self.expiration_hours)).date(),
        )

    def test_view_previous_email_not_expired(self):
        self.user.create_email_verification()

        self.assertTrue(EmailVerification.objects.first())

        response = self.client.get(self.path)

        self._common_tests(response)

        seconds_since_last_email = self.user.seconds_since_last_email_verification()
        seconds_left = self.sending_interval - seconds_since_last_email

        self.assertContains(response, f'Please wait {seconds_left} to resend the confirmation email.')
        self.assertFalse(mail.outbox)

    def test_view_user_already_verified(self):
        self.user.verify()

        response = self.client.get(self.path)

        self._common_tests(response)
        self.assertContains(response, 'You have already verified your email.')
        self.assertFalse(mail.outbox)


class EmailVerificationViewTestCase(TestCase):

    def setUp(self):
        self.user = test_user.create_user()
        self.client.force_login(user=self.user)
        self.email_verification = self.user.create_email_verification()
        self.path = reverse(
            'accounts:email-verification',
            kwargs={'email': self.user.email, 'code': self.email_verification.code}
        )

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'accounts/email/email_verification_complete.html')

    def test_view_success(self):
        self.assertFalse(self.user.is_verified)

        response = self.client.get(self.path)

        self._common_tests(response)
        self.assertContains(response, 'Your email address has been successfully verified.')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

    def test_view_user_already_verified(self):
        self.user.verify()

        response = self.client.get(self.path)

        self._common_tests(response)
        self.assertContains(response, 'Your email has already been verified.')

    def test_view_link_has_expired(self):
        self.email_verification.expiration -= timedelta(hours=settings.EMAIL_EXPIRATION_HOURS * 2)
        self.email_verification.save()

        response = self.client.get(self.path)

        self._common_tests(response)
        self.assertContains(response, 'The verification link has expired.')


class UserProfileViewTestCase(TestCase):

    def setUp(self):
        self.data = {
            'username': test_user.username + 'New',
            'first_name': test_user.first_name + 'New',
            'last_name': test_user.last_name + 'New',
            'email': test_user.email + 'New',
        }
        self.user = test_user.create_user()
        self.client.force_login(user=self.user)
        self.path = reverse('accounts:profile', args=(self.user.slug,))

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'accounts/profile/profile.html')

    def test_view_get(self):
        response = self.client.get(self.path)

        self._common_tests(response)

    def test_view_post_success(self):
        self.assertEqual(self.user.username, test_user.username)
        self.assertEqual(self.user.first_name, test_user.first_name)
        self.assertEqual(self.user.last_name, test_user.last_name)
        self.assertFalse(self.user.image)

        with open(find('img/default_user_image.png'), 'rb') as image:
            self.data['image'] = image
            response = self.client.post(self.path, self.data, follow=True)

        self.user.refresh_from_db()
        self._common_tests(response)
        self.assertEqual(self.user.username, self.data['username'])
        self.assertEqual(self.user.first_name, self.data['first_name'])
        self.assertEqual(self.user.last_name, self.data['last_name'])
        self.assertTrue(self.user.image)
        self.assertContains(response, 'Profile updated successfully!')

    def test_view_post_without_changing_username(self):
        data = self.data.copy()
        data['username'] = test_user.username

        self.assertEqual(self.user.username, test_user.username)

        response = self.client.post(self.path, data, follow=True)

        self.user.refresh_from_db()
        self._common_tests(response)
        self.assertEqual(self.user.username, test_user.username)
        self.assertContains(response, 'Profile updated successfully!')

    def test_view_post_username_taken(self):
        username = 'User'
        email = 'user@mail.com'

        data = self.data.copy()
        data['username'] = username
        data['email'] = email

        self.assertFalse(User.objects.filter(username=username, email=email))

        test_user.create_user(username=username, email=email)

        response = self.client.post(self.path, data, follow=True)

        self.user.refresh_from_db()
        self._common_tests(response)
        self.assertTrue(User.objects.filter(username=username, email=email))
        self.assertFormError(response, 'form', 'username', 'A user with that username already exists.')


class UserProfilePasswordViewTestCase(TestCase):

    def setUp(self):
        new_password = test_user.new_password
        self.data = {
            'old_password': test_user.password,
            'new_password1': new_password,
            'new_password2': new_password,
        }
        self.user = test_user.create_user()
        self.client.force_login(user=self.user)
        self.path = reverse('accounts:profile-password', args=(self.user.slug,))

    def test_view_get(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'accounts/profile/profile.html')

    def test_view_post(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.path)


class PwdResetViewTestCase(TestCase):

    def setUp(self):
        self.data = {'email': test_user.email}
        self.user = test_user.create_user()
        self.path = reverse('accounts:reset_password')

    def test_view_get(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'accounts/password/reset_password.html')

    def test_view_post(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.path)


class PwdResetConfirmViewTestCase(TestCase):

    def setUp(self):
        self.user = test_user.create_user()
        uid = urlsafe_base64_encode(force_bytes(self.user.id))
        token = PasswordResetTokenGenerator().make_token(self.user)
        self.valid_path = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        self.invalid_path = reverse('accounts:password_reset_confirm', kwargs={'uidb64': 'invalid', 'token': 'invalid'})

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'accounts/password/password_reset_confirm.html')

    def test_view_get_valid_url(self):
        response = self.client.get(self.valid_path, follow=True)

        self._common_tests(response)

    def test_view_get_invalid_url(self):
        response = self.client.get(self.invalid_path)

        self._common_tests(response)
        self.assertContains(response, 'The password reset link was invalid, possibly because it has already been used. '
                                      'Please request a new password reset.', html=True)


class UserProfileEmailViewTest(TestCase):

    def setUp(self):
        self.user = test_user.create_user()
        self.client.force_login(self.user)
        self.url = reverse('accounts:profile-email', args=(self.user.id,))

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'accounts/profile/profile.html')

    def test_profile_email_page_contains_form(self):
        response = self.client.get(self.url)

        self._common_tests(response)
        form = response.context.get('form')
        self.assertIsInstance(form, EmailChangeForm)

    def test_profile_email_form_changes_email_address(self):
        new_email = test_user.email + 'New'

        response = self.client.post(
            self.url,
            {'new_email': new_email, 'old_password': test_user.password},
            follow=True,
        )

        self._common_tests(response)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, new_email)

    def test_profile_email_form_returns_error_for_invalid_password(self):
        response = self.client.post(self.url, {'new_email': test_user.email, 'old_password': 123})

        self._common_tests(response)
        self.assertContains(response, 'Your old password was entered incorrectly. Please enter it again.')

    def test_profile_email_form_returns_error_for_existing_email(self):
        username = 'New' + test_user.username
        email = 'New' + test_user.email

        test_user.create_user(username=username, email=email)
        response = self.client.post(self.url, {
            'new_email': email,
            'old_password': test_user.password,
        })

        self._common_tests(response)
        self.assertContains(response, 'This email address is already in use.')
