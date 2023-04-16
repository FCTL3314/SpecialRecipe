from django.db import models


class RecipeBookmarkManager(models.Manager):

    def user_bookmarks(self, user_id):
        return self.filter(user_id=user_id).prefetch_related('recipe__bookmarks', 'recipe')
