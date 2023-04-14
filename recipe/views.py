from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin, FormView
from django.views.generic.list import ListView

from common.views import TitleMixin
from recipe.forms import CommentForm, SearchForm
from recipe.models import Category, Comment, Recipe, RecipeBookmark


class RecipesListView(TitleMixin, ListView):
    model = Recipe
    template_name = 'recipe/index.html'
    ordering = ('name',)
    title = 'Special Recipe | Recipes'
    paginate_by = settings.RECIPES_PAGINATE_BY

    def get_queryset(self):
        queryset = self.model.objects.get_cached_queryset()

        selected_category_slug = self.kwargs.get('category_slug')
        search = self.request.GET.get('search')

        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        elif selected_category_slug:
            queryset = queryset.filter(category__slug=selected_category_slug)

        return queryset.prefetch_related('bookmarks').order_by(*self.ordering)

    def get_paginator_url(self):
        selected_category_slug = self.kwargs.get('category_slug')
        search = self.request.GET.get('search')

        if selected_category_slug:
            paginator_url = reverse('recipe:category', args=(selected_category_slug,)) + '?page='
        elif search:
            paginator_url = f'?search={search}&page='
        else:
            paginator_url = reverse('recipe:index') + '?page='
        return paginator_url

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        categories = Category.objects.get_cached_queryset().order_by('name')
        popular_recipes = self.model.objects.get_cached_popular_recipes()

        context['categories'] = categories[:settings.CATEGORIES_PAGINATE_BY]
        context['popular_recipes'] = popular_recipes[:3]

        context['has_more_categories'] = categories.count() > settings.CATEGORIES_PAGINATE_BY
        context['selected_category_slug'] = self.kwargs.get('category_slug')
        context['paginator_url'] = self.get_paginator_url()
        context['user_bookmarks'] = self.model.objects.get_user_bookmarked_recipes(self.request.user)
        context['form'] = SearchForm(initial={'search': self.request.GET.get('search')})

        return context


class RecipeDetailView(FormMixin, DetailView):
    model = Recipe
    slug_url_kwarg = 'recipe_slug'
    template_name = 'recipe/recipe_description.html'
    form_class = CommentForm

    def _has_viewed(self, request):
        remote_addr = request.META.get('REMOTE_ADDR')
        recipe_slug = self.kwargs.get(self.slug_url_kwarg)

        key = f'{remote_addr}_{recipe_slug}'
        has_viewed = cache.get(key)

        if not has_viewed:
            cache.set(key, True, 60)
        return has_viewed

    def _increment_views(self):
        self.object.views += 1
        self.object.save()

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not self._has_viewed(request):
            self._increment_views()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        comments = self.object.get_comments().order_by('-created_date')
        comments_count = comments.count()

        context['comments'] = comments[:settings.COMMENTS_PAGINATE_BY]
        context['comments_count'] = comments_count
        context['has_more_comments'] = comments_count > settings.COMMENTS_PAGINATE_BY

        context['title'] = f'Special Recipe | {self.object.name}'
        context['ingredients'] = self.object.get_ingredients()
        return context


class BookmarksListView(LoginRequiredMixin, TitleMixin, ListView):
    model = RecipeBookmark
    template_name = 'recipe/recipe_bookmarks.html'
    ordering = ('-created_date',)
    title = 'Special Recipe | Bookmarks'

    def get_queryset(self):
        queryset = self.model.objects.get_user_bookmarks(self.request.user)
        return queryset.order_by(*self.ordering)[:settings.RECIPES_PAGINATE_BY]


class AddCommentCreateView(LoginRequiredMixin, FormView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        text = form.cleaned_data.get('text')
        recipe_id = self.kwargs.get('recipe_id')

        recipe = get_object_or_404(Recipe, id=recipe_id)

        Comment.objects.create(text=text, author=self.request.user, recipe=recipe)
        return super().form_valid(form)

    def get_success_url(self):
        referer = self.request.META.get('HTTP_REFERER')
        if referer:
            return referer
        return reverse('recipe:index')


@login_required()
def add_to_bookmarks(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.bookmarks.add(request.user, through_defaults=None)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return HttpResponseRedirect(reverse('recipe:index'))


@login_required()
def remove_from_bookmarks(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.bookmarks.remove(request.user)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return HttpResponseRedirect(reverse('recipe:index'))
