from django.db import models

from accounts.models import User
from recipe.managers import (CategoryManager, RecipeBookmarkManager,
                             RecipeManager)


class Category(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(unique=True)

    objects = CategoryManager()

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    image = models.ImageField(upload_to='recipe_images')
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=128)
    cooking_description = models.TextField()
    category = models.ForeignKey(to=Category, on_delete=models.PROTECT)
    slug = models.SlugField(unique=True)
    bookmarks = models.ManyToManyField(User, blank=True, through='RecipeBookmark')
    views = models.PositiveBigIntegerField(default=0)

    objects = RecipeManager()

    def __str__(self):
        return self.name

    def get_ingredients(self):
        return Ingredient.objects.filter(recipe=self)

    def get_comments(self):
        return Comment.objects.filter(recipe=self).prefetch_related('author')

    def bookmarks_count(self):
        return self.bookmarks.count()


class Ingredient(models.Model):
    name = models.CharField(max_length=256)
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class RecipeBookmark(models.Model):
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = RecipeBookmarkManager()

    def __str__(self):
        return f'{self.user.username} | {self.recipe.name}'


class Comment(models.Model):
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)
    author = models.ForeignKey(to=User, null=True, on_delete=models.SET_NULL)
    text = models.CharField(max_length=516)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
