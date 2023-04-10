from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Count, F, Q
from django.http import HttpResponseBadRequest
from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView

from common.views import CacheMixin, TitleMixin
from recipe.forms import CommentForm, SearchForm
from recipe.models import Category, Comment, Recipe, RecipeBookmark


class RecipesListView(CacheMixin, TitleMixin, ListView):
    queryset = Recipe.objects.all()
    template_name = 'recipe/index.html'
    ordering = ('name',)
    title = 'Special Recipe | Recipes'

    paginate_by = settings.RECIPES_PAGINATE_BY

    def get_queryset(self):
        initial_queryset = self.get_cached_data_or_set_new('recipes', lambda: self.queryset, 60 * 60)
        selected_category_slug = self.kwargs.get('category_slug')
        search = self.request.GET.get('search')
        if search:
            queryset = initial_queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        elif selected_category_slug:
            queryset = initial_queryset.filter(category__slug=selected_category_slug)
        else:
            queryset = initial_queryset
        return queryset.prefetch_related('bookmarks').order_by(*self.ordering)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        selected_category_slug = self.kwargs.get('category_slug')
        search = self.request.GET.get('search')

        if selected_category_slug:
            context['paginator_url'] = reverse('recipe:category', args=(selected_category_slug,)) + '?page='
        elif search:
            context['paginator_url'] = f'?search={search}&page='
        else:
            context['paginator_url'] = reverse('recipe:index') + '?page='

        context['categories'] = self.get_cached_data_or_set_new(
            'categories',
            lambda: Category.objects.all(),
            60 * 60,
        ).order_by('name')[:settings.CATEGORIES_PAGINATE_BY]
        context['has_more_categories'] = Category.objects.count() > settings.CATEGORIES_PAGINATE_BY
        context['popular_recipes'] = self.get_cached_data_or_set_new(
            'popular_recipes',
            lambda: Recipe.objects.annotate(bookmarks_count=Count('bookmarks')).order_by('-bookmarks_count'),
            3600 * 24,
        )[:3]

        context['selected_category_slug'] = self.kwargs.get('category_slug')
        context['form'] = SearchForm(initial={'search': self.request.GET.get('search')})

        if self.request.user.is_authenticated:
            context['user_bookmarks'] = self.object_list.filter(bookmarks=self.request.user)
        return context


class RecipeDetailView(FormMixin, DetailView):
    model = Recipe
    slug_url_kwarg = 'recipe_slug'
    template_name = 'recipe/recipe_description.html'
    form_class = CommentForm

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        ip = request.META.get('REMOTE_ADDR')
        recipe_slug = kwargs.get(self.slug_url_kwarg)
        view = (ip, recipe_slug)
        has_viewed = cache.get(view)
        if not has_viewed:
            cache.set(view, True, 60)
            self.object.views = F('views') + 1
            self.object.save(update_fields=['views'])
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = f'Special Recipe | {self.object.name}'
        context['ingredients'] = self.object.get_ingredients()
        comments = self.object.get_comments()
        context['comments'] = comments[:settings.COMMENTS_PAGINATE_BY]
        context['comments_count'] = comments.count()
        context['has_more_comments'] = comments.count() > settings.COMMENTS_PAGINATE_BY
        return context


class BookmarksListView(LoginRequiredMixin, TitleMixin, ListView):
    model = RecipeBookmark
    template_name = 'recipe/recipe_bookmarks.html'
    ordering = ('-created_date',)
    title = 'Special Recipe | Bookmarks'

    def get_queryset(self):
        queryset = self.model.objects.filter(user=self.request.user).prefetch_related('recipe')
        return queryset.order_by(*self.ordering)[:settings.RECIPES_PAGINATE_BY]


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


@login_required()
def add_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    text = request.POST.get('comment')
    if not text:
        return HttpResponseBadRequest('Comment text is missing.')
    Comment.objects.create(text=text, author=request.user, recipe=recipe)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return HttpResponseRedirect(reverse('recipe:index'))
