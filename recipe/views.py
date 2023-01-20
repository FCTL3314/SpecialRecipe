from django.shortcuts import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count

from recipe.models import Category, Recipe, Ingredient
from recipe.forms import SearchForm


class RecipesListView(ListView):
    model = Recipe
    context_object_name = 'recipes'
    template_name = 'recipe/recipe.html'

    paginate_by = 3

    def get_queryset(self):
        recipes = super().get_queryset()
        category_id = self.kwargs.get('category_id')
        search = self.request.GET.get('search')
        if search:
            return recipes.filter(Q(name__icontains=search) | Q(description__icontains=search)).annotate(
                saves_count=Count('saves')).order_by('-saves_count')
        elif category_id:
            return recipes.filter(category_id=category_id).annotate(saves_count=Count('saves')).order_by('-saves_count')
        else:
            return recipes.annotate(saves_count=Count('saves')).order_by('-saves_count')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Special Recipe - Recipes'
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.kwargs.get('category_id')
        context['form'] = SearchForm(initial={'search': self.request.GET.get('search')})
        context['popular_recipes'] = Recipe.objects.annotate(saves_count=Count('saves')).order_by('-saves_count')[:3]
        if self.request.user.is_authenticated:
            context['user_saves'] = self.object_list.filter(saves=self.request.user)
        return context


class DescriptionView(TemplateView):
    template_name = 'recipe/recipe_description.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        recipe = Recipe.objects.all().get(slug=self.kwargs.get('slug'))
        ingredients = Ingredient.objects.filter(recipe=recipe)
        context['recipe'] = recipe
        context['ingredients'] = ingredients
        context['title'] = f'Special Recipe - {recipe.name}'
        return context


class SavesListView(ListView):
    model = Recipe
    context_object_name = 'saved_recipes'
    template_name = 'accounts/saved_recipes.html'

    paginate_by = 3

    def get_queryset(self):
        recipes = super().get_queryset()
        return recipes.filter(saves=self.request.user).annotate(saves_count=Count('saves')).order_by('-saves_count')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['title'] = f'Special Recipe - {self.request.user.username}\'s saves'
        return context


@login_required()
def add_to_saved(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    recipe.saves.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required()
def remove_from_saved(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    save = recipe.saves.get(id=request.user.id)
    recipe.saves.remove(save)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
