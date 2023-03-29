from django.db import models

from accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'category'
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

    def get_ingredients(self):
        return Ingredient.objects.filter(recipe=self)

    def bookmarks_count(self):
        return self.bookmarks.count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'


class Ingredient(models.Model):
    name = models.CharField(max_length=48)
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class RecipeBookmark(models.Model):
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
