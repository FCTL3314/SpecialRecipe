from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework import routers

from api.views.accounts import (EmailVerificationUpdateAPIView,
                                SendVerificationEmailCreateAPIView)
from api.views.recipe import (AddToBookmarksCreateView, CategoryModelViewSet,
                              IngredientGenericViewSet, RecipeModelViewSet,
                              RemoveFromBookmarksDestroyView)
from utils.urls import is_url_allowed

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'recipes', RecipeModelViewSet, basename='recipes')
router.register(r'categories', CategoryModelViewSet, basename='categories')
router.register(r'ingredients', IngredientGenericViewSet, basename='ingredients')
djoser_user_router = routers.DefaultRouter()
djoser_user_router.register(r'users', UserViewSet, basename='users')

allowed_djoser_user_urls = [
    'users/',
    'users/me/',
    'users/set_password/',
    'users/reset_password/',
    'users/reset_password_confirm/',
]

filtered_djoser_user_router_urls = list(
    filter(lambda url: is_url_allowed(url, allowed_djoser_user_urls), djoser_user_router.urls)
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(filtered_djoser_user_router_urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('verification/send/', SendVerificationEmailCreateAPIView.as_view(), name='send-verification-email'),
    path('verify/', EmailVerificationUpdateAPIView.as_view(), name='email-verification'),
    path('saves/add/', AddToBookmarksCreateView.as_view(), name='add-to-bookmarks'),
    path('saves/remove/', RemoveFromBookmarksDestroyView.as_view(), name='remove-from-bookmarks'),
]
