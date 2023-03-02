from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Q
from django.test import TestCase
from django.urls import reverse

from recipe.models import Category, Ingredient, Recipe, User

user_data = {
    'username': 'TestUser',
    'first_name': 'Test',
    'last_name': 'User',
    'email': 'testuser@mail.com',
    'password': 'qnjCmk27yzKTCWWiwdYH',
    'slug': 'test',
}


class RecipesListViewTestCase(TestCase):
    fixtures = ['category.json', 'recipe.json']

    def setUp(self) -> None:
        self.paginate_by = settings.RECIPES_PAGINATE_BY
        self.queryset = Recipe.objects.all()
        self.categories = Category.objects.all()

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'recipe/index.html')
        self.assertEqual(response.context_data['title'], 'Special Recipe | Recipes')
        self.assertEqual(list(response.context_data['categories']), list(self.categories))
        popular_recipes_cached = cache.get('popular_recipes')
        if popular_recipes_cached:
            self.assertEqual(list(response.context_data['popular_recipes']), list(popular_recipes_cached))
        else:
            self.assertEqual(
                list(response.context_data['popular_recipes']),
                list(self.queryset.annotate(saves_count=Count('saves')).order_by('-saves_count')[:3])
            )

    def test_list_view(self):
        path = reverse('index')
        response = self.client.get(path)

        self._common_tests(response)
        self.assertEqual(
            list(response.context_data['recipes']),
            list(self.queryset.order_by('name')[:self.paginate_by])
        )
        self.assertEqual(response.context_data['selected_category'], None)

    def test_list_view_category(self):
        category = self.categories.first()

        path = reverse('recipe:category', kwargs={'category_slug': category.slug})
        response = self.client.get(path)

        self._common_tests(response)
        self.assertEqual(
            list(response.context_data['recipes']),
            list(self.queryset.filter(category__slug=category.slug).order_by('name'))[:self.paginate_by]
        )
        self.assertEqual(response.context_data['selected_category'], category.slug)

    def test_list_view_search(self):
        search = 'pizza'
        data = {'search': search}

        path = reverse('index')
        response = self.client.get(path, data)

        self._common_tests(response)
        self.assertEqual(
            list(response.context_data['recipes']),
            list(
                self.queryset.filter(Q(name__icontains=search) | Q(description__icontains=search)).order_by('name')
            )[:self.paginate_by])
        self.assertEqual(response.context_data['selected_category'], None)


class DescriptionViewTestCase(TestCase):
    fixtures = ['category.json', 'recipe.json', 'ingredient.json']

    def setUp(self) -> None:
        self.object = Recipe.objects.first()
        self.path = reverse('recipe:description', kwargs={'recipe_slug': self.object.slug})
        # The address is specified in order to delete the cache created by the test.
        self.remote_addr = '127.0.0.1'

    def test_view(self):
        initial_view = self.object.views
        ingredients = Ingredient.objects.filter(recipe=self.object)

        response = self.client.get(self.path, REMOTE_ADDR=self.remote_addr)

        self.object.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'recipe/recipe_description.html')
        self.assertEqual(response.context_data['title'], f'Special Recipe | {self.object.name}')
        self.assertEqual(response.context_data['recipe'], self.object)
        self.assertEqual(list(response.context_data['ingredients']), list(ingredients))
        self.assertGreater(self.object.views, initial_view)
        cache.delete((self.remote_addr, self.object.slug))


class AddToSavedViewTestCase(TestCase):
    fixtures = ['category.json', 'recipe.json']

    def _create_user(self, username=user_data['username'], first_name=user_data['first_name'],
                     last_name=user_data['last_name'], email=user_data['email'], password=user_data['password']):
        self.user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )

    def setUp(self) -> None:
        self._create_user()
        self.client.login(**user_data)
        self.object = Recipe.objects.first()
        self.path = reverse('recipe:add-to-saved', args={self.object.id})

    def test_view(self):
        self.assertFalse(self.object.saves.filter(id=self.user.id))

        response = self.client.get(self.path, HTTP_REFERER=reverse('index'))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(self.object.saves.filter(id=self.user.id))


class RemoveFromSavedViewTestCase(TestCase):
    fixtures = ['category.json', 'recipe.json']

    def _create_user(self, username=user_data['username'], first_name=user_data['first_name'],
                     last_name=user_data['last_name'], email=user_data['email'], password=user_data['password']):
        self.user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )

    def setUp(self) -> None:
        self._create_user()
        self.client.login(**user_data)
        self.object = Recipe.objects.first()
        self.object.saves.add(self.user)
        self.path = reverse('recipe:remove-from-saved', args={self.object.id})

    def test_view(self):
        self.assertTrue(self.object.saves.filter(id=self.user.id))

        response = self.client.get(self.path, HTTP_REFERER=reverse('index'))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('index'))
        self.assertFalse(self.object.saves.filter(id=self.user.id))
