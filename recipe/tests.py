from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Q
from django.test import TestCase
from django.urls import reverse

from recipe.models import Category, Ingredient, Recipe, User


class RecipesListViewTestCase(TestCase):
    fixtures = ['category.json', 'recipe.json']

    def setUp(self) -> None:
        self.paginate_by = settings.RECIPES_PAGINATE_BY
        self.recipes = Recipe.objects.all()
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
        data = {'search': search}

        path = reverse('index')
        response = self.client.get(path, data)

        self._common_tests(response)
        self.assertEqual(
            list(response.context_data['recipes']),
            list(
                self.recipes.filter(Q(name__icontains=search) | Q(description__icontains=search)).order_by('name')
            )[:self.paginate_by])
        self.assertEqual(response.context_data['selected_category'], None)


class DescriptionViewTestCase(TestCase):
    fixtures = ['category.json', 'recipe.json', 'ingredient.json']

    def setUp(self) -> None:
        self.recipes = Recipe.objects.all()

    def test_view(self):
        recipe = self.recipes.first()
        ingredients = Ingredient.objects.filter(recipe=recipe)

        self.assertEqual(recipe.views, 0)

        path = reverse('recipe:description', kwargs={'recipe_slug': recipe.slug})
        response = self.client.get(path)

        recipe.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'recipe/recipe_description.html')
        self.assertEqual(response.context_data['title'], f'Special Recipe | {recipe.name}')
        self.assertEqual(response.context_data['recipe'], recipe)
        self.assertEqual(list(response.context_data['ingredients']), list(ingredients))
        self.assertEqual(recipe.views, 1)


class AddToSavedViewTestCase(TestCase):
    fixtures = ['category.json', 'recipe.json']

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='TestUser',
            email='testuser@mail.com',
            password='qnjCmk27yzKTCWWiwdYH'
        )
        self.client.login(username='TestUser', email='testuser@mail.com', password='qnjCmk27yzKTCWWiwdYH')
        self.recipe = Recipe.objects.first()
        self.path = reverse('recipe:add-to-saved', args={self.recipe.id})

    def test_view(self):
        self.assertFalse(self.recipe.saves.filter(id=self.user.id))

        response = self.client.get(self.path, HTTP_REFERER=reverse('index'))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(self.recipe.saves.filter(id=self.user.id))


class RemoveFromSavedViewTestCase(TestCase):
    fixtures = ['category.json', 'recipe.json']

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='TestUser',
            email='testuser@mail.com',
            password='qnjCmk27yzKTCWWiwdYH'
        )
        self.client.login(username='TestUser', email='testuser@mail.com', password='qnjCmk27yzKTCWWiwdYH')
        self.recipe = Recipe.objects.first()
        self.recipe.saves.add(self.user)
        self.path = reverse('recipe:remove-from-saved', args={self.recipe.id})

    def test_view(self):
        self.assertTrue(self.recipe.saves.filter(id=self.user.id))

        response = self.client.get(self.path, HTTP_REFERER=reverse('index'))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('index'))
        self.assertFalse(self.recipe.saves.filter(id=self.user.id))
