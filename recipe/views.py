from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from recipe.forms import SearchForm
from recipe.models import Category, Ingredient, Recipe


class RecipesListView(ListView):
    model = Recipe
    context_object_name = 'recipes'
    template_name = 'recipe/index.html'
    ordering = ('name',)

    paginate_by = settings.RECIPES_PAGINATE_BY

    def get_queryset(self):
        recipes_cache = cache.get('recipes')
        if recipes_cache:
            recipes = recipes_cache
        else:
            recipes = super().get_queryset()
            cache.set('recipes', recipes, 60 * 60)
        category_slug = self.kwargs.get('category_slug')
        search = self.request.GET.get('search')
        if search:
            return recipes.filter(
                Q(name__icontains=search) | Q(description__icontains=search)).prefetch_related('saves')
        elif category_slug:
            return recipes.filter(category__slug=category_slug).prefetch_related('saves')
        else:
            return recipes.prefetch_related('saves')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Special Recipe | Recipes'

        categories_cache = cache.get('categories')
        if categories_cache:
            context['categories'] = categories_cache
        else:
            context['categories'] = Category.objects.all()
            cache.set('categories', context['categories'], 60 * 60)

        popular_recipes_cache = cache.get('popular_recipes')
        if popular_recipes_cache:
            context['popular_recipes'] = popular_recipes_cache
        else:
            context['popular_recipes'] = Recipe.objects.annotate(
                saves_count=Count('saves')
            ).order_by('-saves_count')[:3]
            cache.set('popular_recipes', context['popular_recipes'], 3600 * 24)

        context['selected_category'] = self.kwargs.get('category_slug')
        context['form'] = SearchForm(initial={'search': self.request.GET.get('search')})
        if self.request.user.is_authenticated:
            context['user_saves'] = self.object_list.filter(saves=self.request.user)
        return context


class DescriptionView(TemplateView):
    template_name = 'recipe/recipe_description.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        recipe = get_object_or_404(Recipe, slug=self.kwargs.get('recipe_slug'))
        ingredients = Ingredient.objects.filter(recipe=recipe)
        context['recipe'] = recipe
        context['ingredients'] = ingredients
        context['title'] = f'Special Recipe | {recipe.name}'
        return context


class SavesListView(ListView):
    model = Recipe
    context_object_name = 'saved_recipes'
    template_name = 'accounts/saved_recipes.html'
    ordering = ('name',)

    def get_queryset(self):
        recipes = super().get_queryset()
        return recipes.filter(saves=self.request.user).prefetch_related('saves')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['title'] = f'Special Recipe | {self.request.user.username}\'s saves'
        return context


@login_required()
def add_to_saved(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.saves.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required()
def remove_from_saved(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    save = recipe.saves.get(id=request.user.id)
    recipe.saves.remove(save)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
