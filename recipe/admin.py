from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from recipe.models import Category, Ingredient, Recipe


class RecipeInlineAdmin(admin.TabularInline):
    model = Recipe
    fields = ('name', 'description')
    ordering = ('name',)


class IngredientInlineAdmin(admin.TabularInline):
    model = Ingredient
    ordering = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = (RecipeInlineAdmin,)


@admin.register(Recipe)
class RecipeAdmin(SummernoteModelAdmin):
    readonly_fields = ('views',)
    summernote_fields = ('cooking_description',)
    search_fields = ('name',)
    ordering = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = (IngredientInlineAdmin,)
