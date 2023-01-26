from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class UserRegistrationViewTestCase(TestCase):

    def setUp(self):
        self.path = reverse('accounts:registration')
        self.data = {
            'username': 'testuser',
            'email': 'testuser@mail.com',
            'password1': 'testuserpassword',
            'password2': 'testuserpassword',
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
