from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from common.tests import TestUser
from interactions.models import RecipeBookmark
from recipe.models import Recipe

test_user = TestUser()


class BookmarksListViewTestCase(TestCase):
    fixtures = ['category.json', 'recipe.json']

    def _add_recipes_to_user_bookmarks(self, recipes):
        for recipe in recipes:
            recipe.bookmarks.add(self.user, through_defaults=None)

    def setUp(self):
        self.user = test_user.create_user()
        self.client.force_login(self.user)
        self.path = reverse('interactions:bookmarks')

    def test_view_get(self):
        self._add_recipes_to_user_bookmarks(Recipe.objects.all()[:3])

        response = self.client.get(self.path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertCountEqual(
            response.context_data['object_list'],
            RecipeBookmark.objects.get_user_bookmarks(self.user)
        )
