from django.db import models
from accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=32)

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

    class Meta:
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=32)
    amount = models.CharField(max_length=32)
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)


class Saves(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'save'
        verbose_name_plural = 'saves'

    def __str__(self):
        return f'User: {self.user.username} | Recipe {self.recipe.name}'
