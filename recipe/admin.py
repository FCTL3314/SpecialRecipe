from django.contrib import admin
from recipe.models import Category, Recipe, Ingredient, Saves


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'recipe')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Saves)
class SavesAdmin(admin.ModelAdmin):
    list_display = ('recipe_id', 'user_id')
