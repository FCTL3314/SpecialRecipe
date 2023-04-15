from django.db import models

from recipe.managers import CategoryManager, IngredientManager, RecipeManager


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
    bookmarks = models.ManyToManyField('accounts.User', blank=True, through='interactions.RecipeBookmark')
    views = models.PositiveBigIntegerField(default=0)

    objects = RecipeManager()

    def __str__(self):
        return self.name

    def bookmarks_count(self):
        return self.bookmarks.count()


class Ingredient(models.Model):
    name = models.CharField(max_length=256)
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)

    objects = IngredientManager()

    def __str__(self):
        return self.name
