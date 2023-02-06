from datetime import timedelta
from http import HTTPStatus
from uuid import uuid4

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.staticfiles.finders import find
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import now
from humanize import naturaldelta

from accounts.models import EmailVerification, User


class UserRegistrationViewTestCase(TestCase):

    def setUp(self):
        self.data = {
            'username': 'TestUser',
            'email': 'testuser@mail.com',
            'password1': 'qnjCmk27yzKTCWWiwdYH',
            'password2': 'qnjCmk27yzKTCWWiwdYH',
        }
        self.path = reverse('accounts:registration')

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

        user = User.objects.get(username=username)

        self.assertTrue(user.slug, user.username.lower())

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
        self.data = {
            'username': 'TestUser',
            'password': 'qnjCmk27yzKTCWWiwdYH',
        }
        User.objects.create_user(
            username=self.data['username'],
            email='testuser@mail.com',
            password=self.data['password']
        )
        self.path = reverse('accounts:login')

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
        username = 'TestUser'
        email = 'testuser@mail.com'
        password = 'qnjCmk27yzKTCWWiwdYH'
        self.user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        self.client.login(username=username, email=email, password=password)
        self.path = reverse('accounts:send-verification-email', args={self.user.email})

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Sending a verification email')
        self.assertTemplateUsed(response, 'accounts/email/email_verification_done.html')

    def test_view_success(self):
        self.assertFalse(EmailVerification.objects.filter(user=self.user))
        self.assertFalse(mail.outbox)

        response = self.client.get(self.path)

        self._common_tests(response)
        self.assertContains(response, f'You\'re almost there! You will receive an email within a couple of minutes. '
                                      f'Just click on the link in that email to complete your verification if you '
                                      f'don\'t see it, you may need to check your spam folder.', html=True)

        email_verification = EmailVerification.objects.filter(user=self.user)

        self.assertTrue(email_verification)
        self.assertEqual(email_verification.first().expiration.date(), (now() + timedelta(hours=48)).date())
        self.assertTrue(mail.outbox)

    def test_view_previous_email_not_expired(self):
        expiration = now() + timedelta(hours=48)
        verification = EmailVerification.objects.create(code=uuid4(), user=self.user, expiration=expiration)

        self.assertTrue(EmailVerification.objects.first())

        response = self.client.get(self.path)

        self._common_tests(response)

        seconds_left = naturaldelta(verification.created + timedelta(minutes=1) - now())
        self.assertContains(response, f'Please wait {seconds_left} to resend the confirmation email.')
        self.assertFalse(mail.outbox)

    def test_view_user_already_verified(self):
        self.user.is_verified = True
        self.user.save()

        response = self.client.get(self.path)

        self._common_tests(response)
        self.assertContains(response, f'You have already verified your email.')
        self.assertFalse(mail.outbox)


class EmailVerificationViewTestCase(TestCase):

    def setUp(self):
        username = 'TestUser'
        email = 'testuser@mail.com'
        password = 'qnjCmk27yzKTCWWiwdYH'
        self.user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        self.client.login(username=username, email=email, password=password)
        expiration = now() + timedelta(hours=48)
        self.email_verification = EmailVerification.objects.create(code=uuid4(), user=self.user, expiration=expiration)
        self.path = reverse(
            'accounts:email-verification',
            kwargs={'email': self.user.email, 'code': self.email_verification.code}
        )

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Email verification')
        self.assertTemplateUsed(response, 'accounts/email/email_verification_complete.html')

    def test_view_success(self):
        self.assertFalse(self.user.is_verified)

        response = self.client.get(self.path)

        self._common_tests(response)
        self.assertContains(response, 'Your email address has been successfully verified.')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

    def test_view_user_already_verified(self):
        self.user.is_verified = True
        self.user.save()

        response = self.client.get(self.path)

        self._common_tests(response)
        self.assertContains(response, f'Your email has already been verified.')

    def test_view_link_has_expired(self):
        self.email_verification.expiration -= timedelta(hours=72)
        self.email_verification.save()

        response = self.client.get(self.path)

        self._common_tests(response)
        self.assertContains(response, f'The verification link has expired.')


class UserProfileViewTestCase(TestCase):

    def setUp(self):
        username = 'TestUser'
        email = 'testuser@mail.com'
        self.password = 'qnjCmk27yzKTCWWiwdYH'
        self.data = {
            'username': 'TestUserUpdated',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuserupdated@mail.com',
        }
        self.user = User.objects.create_user(
            username=username,
            email=email,
            password=self.password,
        )
        self.client.login(username=username, email=email, password=self.password)
        self.path = reverse('accounts:profile', args={self.user.slug})

    def _common_tests(self, response, user):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], f'Special Recipe | {user.username}\'s profile')
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_view_get(self):
        response = self.client.get(self.path)

        self._common_tests(response, self.user)

    def test_view_post_success(self):
        self.assertEqual(self.user.username, 'TestUser')
        self.assertEqual(self.user.first_name, '')
        self.assertEqual(self.user.last_name, '')
        self.assertEqual(self.user.email, 'testuser@mail.com')
        self.assertFalse(self.user.image)

        with open(find('icon/default_user_image.png'), 'rb') as image:
            self.data['image'] = image
            response = self.client.post(self.path, self.data, follow=True)

        self.user.refresh_from_db()
        self._common_tests(response, self.user)
        self.assertEqual(self.user.username, 'TestUserUpdated')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'testuserupdated@mail.com')
        self.assertTrue(self.user.image)
        self.assertContains(response, 'Profile updated successfully!')

    def test_view_post_username_taken(self):
        username = 'User'
        email = 'user@mail.com'

        username_taken_data = self.data.copy()
        username_taken_data['username'] = username
        username_taken_data['email'] = email

        self.assertFalse(User.objects.filter(username=username, email=email))

        User.objects.create_user(username=username, email=email, password=self.password)

        response = self.client.post(self.path, username_taken_data, follow=True)

        self.user.refresh_from_db()
        self._common_tests(response, self.user)
        self.assertTrue(User.objects.filter(username=username, email=email))
        self.assertContains(response, 'A user with that username already exists.')


class PwdResetViewTestCase(TestCase):

    def setUp(self):
        username = 'TestUser'
        email = 'testuser@mail.com'
        password = 'qnjCmk27yzKTCWWiwdYH'
        self.data = {'email': email}
        self.user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        self.path = reverse('accounts:reset_password')

    def test_view_get(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Special Recipe | Password reset')
        self.assertTemplateUsed(response, 'accounts/password/reset_password.html')

    def test_view_post(self):
        self.assertFalse(mail.outbox)

        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('accounts:password_reset_done'))
        self.assertTrue(mail.outbox)


class PwdResetDoneViewTestCase(TestCase):
    def setUp(self):
        self.path = reverse('accounts:password_reset_done')
        self.follow_path = reverse('accounts:reset_password')

    def test_view_get(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Special Recipe | Password reset')
        self.assertTemplateUsed(response, 'accounts/password/password_reset_done.html')


class PwdResetConfirmViewTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='TestUser',
            email='testuser@mail.com',
            password='qnjCmk27yzKTCWWiwdYH',
        )
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.id))
        token = PasswordResetTokenGenerator().make_token(self.user)
        self.valid_path = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        self.invalid_path = reverse('accounts:password_reset_confirm', kwargs={'uidb64': 'invalid', 'token': 'invalid'})

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Special Recipe | Password reset')
        self.assertTemplateUsed(response, 'accounts/password/password_reset_confirm.html')

    def test_view_get_valid_url(self):
        response = self.client.get(self.valid_path, follow=True)

        self._common_tests(response)

    def test_view_get_invalid_url(self):
        response = self.client.get(self.invalid_path)

        self._common_tests(response)
        self.assertContains(response, 'The password reset link was invalid, possibly because it has already been used. '
                                      'Please request a new password reset.', html=True)


class PwdResetCompleteViewTestCase(TestCase):

    def setUp(self):
        self.path = reverse('accounts:password_reset_complete')

    def test_view_get(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Special Recipe | Password reset')
        self.assertTemplateUsed(response, 'accounts/password/password_reset_complete.html')


class PwdChangeViewTestCase(TestCase):

    def setUp(self):
        username = 'TestUser'
        email = 'testuser@mail.com'
        password = 'qnjCmk27yzKTCWWiwdYH'
        new_password = 'I2l^91VxMD!y'
        self.data = {
            'old_password': password,
            'new_password1': new_password,
            'new_password2': new_password,
        }
        self.user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        self.client.login(username=username, email=email, password=password)
        self.path = reverse('accounts:password_change')

    def test_view_get(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Special Recipe | Password change')
        self.assertTemplateUsed(response, 'accounts/password/password_change.html')

    def test_view_post(self):
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('accounts:password_change_done'))


class PwdChangeDoneViewTestCase(TestCase):

    def setUp(self):
        username = 'TestUser'
        email = 'testuser@mail.com'
        password = 'qnjCmk27yzKTCWWiwdYH'
        self.user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        self.client.login(username=username, email=email, password=password)
        self.path = reverse('accounts:password_change_done')

    def test_view_get(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Special Recipe | Password change')
        self.assertTemplateUsed(response, 'accounts/password/password_change_done.html')
