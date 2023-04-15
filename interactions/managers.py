from django.db import models


class RecipeBookmarkManager(models.Manager):

    def get_user_bookmarks(self, user):
        return self.filter(user=user).prefetch_related('recipe__bookmarks', 'recipe')
