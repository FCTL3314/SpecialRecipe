from django.urls import path

from recipe.views import (BookmarksListView, RecipeDetailView, RecipesListView,
                          add_comment, add_to_bookmarks, remove_from_bookmarks)

app_name = 'recipe'

urlpatterns = [
    path('', RecipesListView.as_view(), name='index'),
    path('description/<slug:recipe_slug>/', RecipeDetailView.as_view(), name='description'),
    path('category/<slug:category_slug>/', RecipesListView.as_view(), name='category'),
    path('bookmarks/add/<int:recipe_id>/', add_to_bookmarks, name='add-to-bookmarks'),
    path('bookmarks/remove/<int:recipe_id>/', remove_from_bookmarks, name='remove-from-bookmarks'),
    path('bookmarks/', BookmarksListView.as_view(), name='bookmarks'),
    path('comment/add/<int:recipe_id>/', add_comment, name='comment-add'),
]
