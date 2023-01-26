from http import HTTPStatus

from django.db.models import Count, Q
from django.test import TestCase
from django.urls import reverse

from recipe.models import Category, Recipe, Ingredient


class RecipesListViewTestCase(TestCase):
    fixtures = ['category.json', 'recipe.json']

    def setUp(self):
        self.paginate_by = 9
        self.recipes = Recipe.objects.all()
        self.categories = Category.objects.all()

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'recipe/index.html')
        self.assertEqual(response.context_data['title'], 'Special Recipe | Recipes')
        self.assertEqual(list(response.context_data['categories']), list(self.categories))
        self.assertEqual(
            list(response.context_data['popular_recipes']),
            list(self.recipes.annotate(saves_count=Count('saves')).order_by('-saves_count')[:3])
        )

    def test_list_view(self):
        path = reverse('index')
        response = self.client.get(path)

        self._common_tests(response)
        self.assertEqual(list(response.context_data['recipes']), list(self.recipes.order_by('name')[:self.paginate_by]))
        self.assertEqual(response.context_data['selected_category'], None)

    def test_list_view_category(self):
        category = self.categories.first()

        path = reverse('recipe:category', kwargs={'category_slug': category.slug})
        response = self.client.get(path)

        self._common_tests(response)
        self.assertEqual(
            list(response.context_data['recipes']),
            list(self.recipes.filter(category__slug=category.slug).order_by('name'))[:self.paginate_by]
        )
        self.assertEqual(response.context_data['selected_category'], category.slug)

    def test_list_view_search(self):
        search = 'pizza'

        path = reverse('index') + f'?search={search}'
        response = self.client.get(path)

        self._common_tests(response)
        self.assertEqual(
            list(response.context_data['recipes']),
            list(
                self.recipes.filter(Q(name__icontains=search) | Q(description__icontains=search)).order_by('name')
            )[:self.paginate_by])
        self.assertEqual(response.context_data['selected_category'], None)


class DescriptionViewTestCase(TestCase):
    fixtures = ['category.json', 'recipe.json', 'ingredient.json']

    def setUp(self):
        self.recipes = Recipe.objects.all()

    def test_view(self):
        recipe = self.recipes.first()
        ingredients = Ingredient.objects.filter(recipe=recipe)

        path = reverse('recipe:description', kwargs={'recipe_slug': recipe.slug})
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'recipe/recipe_description.html')
        self.assertEqual(response.context_data['title'], f'Special Recipe | {recipe.name}')
        self.assertEqual(response.context_data['recipe'], recipe)
        self.assertEqual(list(response.context_data['ingredients']), list(ingredients))
