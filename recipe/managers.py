from django.db import models
from django.db.models import Count

from common.cache import get_cached_data_or_set_new


class CategoryManager(models.Manager):
    categories_cache_time = 60 * 60

    def cached_queryset(self):
        return get_cached_data_or_set_new('categories', self.all, self.categories_cache_time)


class RecipeManager(models.Manager):
    recipes_cache_time = 60 * 60
    popular_recipes_cache_time = 3600 * 24

    def cached_queryset(self):
        return get_cached_data_or_set_new('recipes', self.all, self.recipes_cache_time)

    def cached_popular_recipes(self):
        return get_cached_data_or_set_new(
            'popular_recipes',
            lambda: self.annotate(bookmarks_count=Count('bookmarks')).order_by('-bookmarks_count'),
            self.popular_recipes_cache_time,
        )

    def user_bookmarked_recipes(self, user):
        return self.filter(bookmarks=user) if user.is_authenticated else None
