from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Q
from django.test import TestCase
from django.urls import reverse

from recipe.models import Category, Ingredient, Recipe


class RecipesListViewTestCase(TestCase):
    fixtures = ['category.json', 'recipe.json']

    def setUp(self):
        self.queryset = Recipe.objects.order_by('name')
        self.categories = Category.objects.order_by('name')[:settings.CATEGORIES_PAGINATE_BY]

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'recipe/index.html')
        self.assertEqual(list(response.context_data['categories']), list(self.categories))
        popular_recipes_cached = cache.get('popular_recipes')[:settings.COMMENTS_PAGINATE_BY]
        if popular_recipes_cached:
            self.assertEqual(list(response.context_data['popular_recipes']), list(popular_recipes_cached))
        else:
            self.assertEqual(
                list(response.context_data['popular_recipes']),
                list(self.queryset.annotate(bookmarks_count=Count('bookmarks')).order_by('-bookmarks_count')[:3])
            )

    def test_list_view(self):
        path = reverse('recipe:index')
        response = self.client.get(path)

        self._common_tests(response)
        self.assertEqual(
            list(response.context_data['object_list']),
            list(self.queryset[:settings.RECIPES_PAGINATE_BY])
        )
        self.assertEqual(response.context_data['selected_category_slug'], None)

    def test_list_view_category(self):
        category = self.categories.first()

        path = reverse('recipe:category', kwargs={'category_slug': category.slug})
        response = self.client.get(path)

        self._common_tests(response)
        self.assertEqual(
            list(response.context_data['object_list']),
            list(self.queryset.filter(category__slug=category.slug).order_by('name'))[:settings.RECIPES_PAGINATE_BY]
        )
        self.assertEqual(response.context_data['selected_category_slug'], category.slug)

    def test_list_view_search(self):
        search = 'pizza'
        data = {'search': search}

        path = reverse('recipe:index')
        response = self.client.get(path, data)

        self._common_tests(response)
        self.assertEqual(
            list(response.context_data['object_list']),
            list(
                self.queryset.filter(Q(name__icontains=search) | Q(description__icontains=search)).order_by('name')
            )[:settings.RECIPES_PAGINATE_BY],
        )
        self.assertEqual(response.context_data['selected_category_slug'], None)


class RecipeDetailViewTestCase(TestCase):
    fixtures = ['category.json', 'recipe.json', 'ingredient.json']

    def setUp(self):
        self.object = Recipe.objects.first()
        self.path = reverse('recipe:detail', kwargs={'recipe_slug': self.object.slug})
        # The address is specified in order to delete the cache created by the test.
        self.remote_addr = '127.0.0.1'

    def test_view(self):
        initial_views = self.object.views
        ingredients = Ingredient.objects.filter(recipe=self.object)

        response = self.client.get(self.path, REMOTE_ADDR=self.remote_addr)

        self.object.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'recipe/recipe_description.html')
        self.assertEqual(response.context_data['title'], f'Special Recipe | {self.object.name}')
        self.assertEqual(response.context_data['recipe'], self.object)
        self.assertEqual(list(response.context_data['ingredients']), list(ingredients))
        self.assertGreater(self.object.views, initial_views)

    def tearDown(self):
        key = f'{self.remote_addr}_{self.object.slug}'
        cache.delete(key)
