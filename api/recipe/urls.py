from django.urls import include, path
from rest_framework import routers

from api.recipe.views import (CategoryModelViewSet, CommentGenericViewSet,
                              IngredientGenericViewSet,
                              RecipeBookmarkGenericViewSet, RecipeModelViewSet)

app_name = 'recipe'

router = routers.DefaultRouter()

router.register(r'recipes', RecipeModelViewSet, basename='recipes')
router.register(r'categories', CategoryModelViewSet, basename='categories')
router.register(r'ingredients', IngredientGenericViewSet, basename='ingredients')
router.register(r'comments', CommentGenericViewSet, basename='comments')
router.register(r'bookmarks', RecipeBookmarkGenericViewSet, basename='bookmarks')

urlpatterns = [
    path('', include(router.urls)),
]
