from django.db import models


class RecipeBookmarkManager(models.Manager):

    def get_user_bookmarks(self, user_id):
        return self.filter(user_id=user_id).prefetch_related('recipe__bookmarks', 'recipe')


class RecipeCommentManager(models.Manager):

    def get_recipe_comments(self, recipe_id):
        return self.filter(recipe_id=recipe_id).prefetch_related('author')
