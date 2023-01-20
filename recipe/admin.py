from django.contrib import admin
from recipe.models import Category, Recipe, Ingredient


class RecipeInlineAdmin(admin.TabularInline):
    model = Recipe
    fields = ('name', 'description')
    ordering = ('name',)


class IngredientInlineAdmin(admin.TabularInline):
    model = Ingredient
    fields = ('name',)
    ordering = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    inlines = (RecipeInlineAdmin,)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = (IngredientInlineAdmin,)
