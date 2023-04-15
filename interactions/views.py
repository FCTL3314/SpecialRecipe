from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, ListView

from common.urls import get_referer_or_default
from common.views import TitleMixin
from interactions.forms import RecipeCommentForm
from interactions.models import RecipeBookmark, RecipeComment
from recipe.models import Recipe


class BookmarksListView(LoginRequiredMixin, TitleMixin, ListView):
    model = RecipeBookmark
    template_name = 'recipe/recipe_bookmarks.html'
    ordering = ('-created_date',)
    title = 'Special Recipe | Bookmarks'

    def get_queryset(self):
        queryset = self.model.objects.get_user_bookmarks(self.request.user)
        return queryset.order_by(*self.ordering)[:settings.RECIPES_PAGINATE_BY]


class AddCommentCreateView(LoginRequiredMixin, FormView):
    model = RecipeComment
    form_class = RecipeCommentForm

    def form_valid(self, form):
        text = form.cleaned_data.get('text')
        recipe_id = self.kwargs.get('recipe_id')

        recipe = get_object_or_404(Recipe, id=recipe_id)

        RecipeComment.objects.create(text=text, author=self.request.user, recipe=recipe)
        return super().form_valid(form)

    def get_success_url(self):
        return get_referer_or_default(self.request)
