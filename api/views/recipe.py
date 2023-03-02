from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   UpdateModelMixin)
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from api.pagination import (CategoryPageNumberPagination,
                            RecipePageNumberPagination)
from api.serializers.recipe import (CategorySerializer, IngredientSerializer,
                                    RecipeSerializer)
from recipe.models import Category, Ingredient, Recipe


class CategoryModelViewSet(ModelViewSet):
    queryset = Category.objects.order_by('name')
    serializer_class = CategorySerializer
    pagination_class = CategoryPageNumberPagination

    def get_permissions(self):
        if self.action in ('create', 'update', 'destroy'):
            self.permission_classes = (IsAdminUser,)
        return super().get_permissions()


class RecipeModelViewSet(ModelViewSet):
    queryset = Recipe.objects.order_by('name')
    serializer_class = RecipeSerializer
    pagination_class = RecipePageNumberPagination

    def get_permissions(self):
        if self.action in ('create', 'update', 'destroy'):
            self.permission_classes = (IsAdminUser,)
        return super().get_permissions()


class IngredientGenericViewSet(CreateModelMixin, UpdateModelMixin, GenericViewSet, DestroyModelMixin):
    queryset = Ingredient.objects.order_by('name')
    serializer_class = IngredientSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'destroy'):
            self.permission_classes = (IsAdminUser,)
        return super().get_permissions()
