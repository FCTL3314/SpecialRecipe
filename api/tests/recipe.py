from django.contrib.staticfiles.finders import find
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import User
from recipe.models import Category, Ingredient, Recipe


class CategoryTestCase(APITestCase):
    fixtures = ['category.json']

    def setUp(self) -> None:
        self.object = Category.objects.first()
        self.initial_count = Category.objects.count()
        self.user = User.objects.create_user(
            username='TestUser',
            email='testuser@mail.com',
            password='qnjCmk27yzKTCWWiwdYH',
        )
        self.token, self.created = Token.objects.get_or_create(user=self.user)
        self.data = {'name': 'Test', 'slug': 'test'}
        self.list_path = reverse('api:categories-list')
        self.detail_path = reverse('api:categories-detail', kwargs={'pk': self.object.id})

    def _make_user_staff(self):
        self.user.is_staff = True
        self.user.save()

    def test_category_retrieve(self):
        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('name'), self.object.name)

    def test_category_list(self):
        response = self.client.get(self.list_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('results'))

    def test_category_create_success(self):
        self._make_user_staff()

        response = self.client.post(self.list_path, self.data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(Category.objects.count(), self.initial_count)

    def test_category_create_forbidden(self):
        response = self.client.post(self.list_path, self.data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Category.objects.count(), self.initial_count)

    def test_category_create_unauthorized(self):
        response = self.client.post(self.list_path, self.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Category.objects.count(), self.initial_count)

    def test_category_patch(self):
        response = self.client.patch(self.detail_path, self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('name'), self.data['name'])

    def test_category_delete(self):
        self._make_user_staff()

        response = self.client.delete(self.detail_path, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.object.id).exists())


class RecipeTestCase(APITestCase):
    fixtures = ['recipe.json', 'category.json', 'ingredient.json']

    def setUp(self) -> None:
        self.object = Recipe.objects.first()
        self.initial_count = Recipe.objects.count()
        self.user = User.objects.create_user(
            username='TestUser',
            email='testuser@mail.com',
            password='qnjCmk27yzKTCWWiwdYH',
        )
        self.token, self.created = Token.objects.get_or_create(user=self.user)
        self.data = {
            'name': 'Test',
            'description': 'Test',
            'cooking_description': 'Test',
            'category_id': Category.objects.first().id,
            'slug': 'test'
        }
        self.list_path = reverse('api:recipes-list')
        self.detail_path = reverse('api:recipes-detail', kwargs={'pk': self.object.id})

    def _make_user_staff(self):
        self.user.is_staff = True
        self.user.save()

    def test_recipe_retrieve(self):
        response = self.client.get(self.detail_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('name'), self.object.name)
        self.assertEqual(
            len(response.data.get('ingredients')),
            Ingredient.objects.filter(recipe_id=self.object.id).count()
        )

    def test_recipe_list(self):
        response = self.client.get(self.list_path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('results'))

    def test_recipe_create_success(self):
        self._make_user_staff()

        with open(find('icon/default_user_image.png'), 'rb') as image:
            self.data['image'] = image
            response = self.client.post(self.list_path, self.data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(Recipe.objects.count(), self.initial_count)

    def test_recipe_create_forbidden(self):
        response = self.client.post(self.list_path, self.data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Recipe.objects.count(), self.initial_count)

    def test_recipe_create_unauthorized(self):
        response = self.client.post(self.list_path, self.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Recipe.objects.count(), self.initial_count)

    def test_recipe_patch(self):
        response = self.client.patch(self.detail_path, self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('name'), self.data['name'])

    def test_recipe_delete(self):
        self._make_user_staff()

        response = self.client.delete(self.detail_path, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=self.object.id).exists())


class IngredientTestCase(APITestCase):
    fixtures = ['category.json', 'recipe.json', 'ingredient.json']

    def setUp(self) -> None:
        self.object = Ingredient.objects.first()
        self.initial_count = Ingredient.objects.count()
        self.user = User.objects.create_user(
            username='TestUser',
            email='testuser@mail.com',
            password='qnjCmk27yzKTCWWiwdYH',
        )
        self.token, self.created = Token.objects.get_or_create(user=self.user)
        self.data = {
            'name': 'Test',
            'recipe_id': Recipe.objects.first().id,
            'slug': 'test'
        }
        self.list_path = reverse('api:ingredients-list')
        self.detail_path = reverse('api:ingredients-detail', kwargs={'pk': self.object.id})

    def _make_user_staff(self):
        self.user.is_staff = True
        self.user.save()

    def test_ingredient_create_success(self):
        self._make_user_staff()

        response = self.client.post(self.list_path, self.data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(Ingredient.objects.count(), self.initial_count)

    def test_ingredient_create_forbidden(self):
        response = self.client.post(self.list_path, self.data, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Ingredient.objects.count(), self.initial_count)

    def test_ingredient_create_unauthorized(self):
        response = self.client.post(self.list_path, self.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Ingredient.objects.count(), self.initial_count)

    def test_ingredient_patch(self):
        response = self.client.patch(self.detail_path, self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('name'), self.data['name'])

    def test_ingredient_delete(self):
        self._make_user_staff()

        response = self.client.delete(self.detail_path, HTTP_AUTHORIZATION=f'Token {self.token}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=self.object.id).exists())
