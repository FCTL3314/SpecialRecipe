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
    saves = models.ManyToManyField(User, null=True, blank=True)

    class Meta:
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'

    def total_saves(self):
        return self.saves.count()

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=48)
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)
