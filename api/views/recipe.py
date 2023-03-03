from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   UpdateModelMixin)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from accounts.models import User
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
    serializer_class = RecipeSerializer
    pagination_class = RecipePageNumberPagination

    def get_queryset(self):
        search = self.request.query_params.get('search')
        category_slug = self.request.query_params.get('category_slug')
        if search:
            queryset = Recipe.objects.filter(Q(name__icontains=search) | Q(description__icontains=search))
        elif category_slug:
            queryset = Recipe.objects.filter(category__slug=category_slug)
        else:
            queryset = Recipe.objects.all()
        return queryset.order_by('name')

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


class AddToSavedCreateView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        recipe_id = request.data.get('recipe_id')
        if not recipe_id:
            return Response({'recipe_id': 'This field if required.'}, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        recipe.saves.add(request.user)
        data = {'recipe_id': recipe_id, 'user_id': request.user.id}
        return Response(data, status=status.HTTP_201_CREATED)


class RemoveFromSavedDestroyView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, *args, **kwargs):
        recipe_id = request.data.get('recipe_id')
        if not recipe_id:
            return Response({'recipe_id': 'This field if required.'}, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, id=request.user.id, recipe=recipe)
        recipe.saves.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
