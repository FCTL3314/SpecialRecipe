from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, UpdateModelMixin)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from accounts.models import User
from api.pagination import (CategoryPageNumberPagination,
                            CommentPageNumberPagination,
                            RecipePageNumberPagination)
from api.serializers.recipe import (CategorySerializer, CommentSerializer,
                                    IngredientSerializer,
                                    RecipeBookmarkSerializer, RecipeSerializer)
from common.views import CacheMixin
from recipe.models import Category, Comment, Ingredient, Recipe, RecipeBookmark


class CategoryModelViewSet(CacheMixin, ModelViewSet):
    serializer_class = CategorySerializer
    pagination_class = CategoryPageNumberPagination

    def get_queryset(self):
        queryset = self.get_cached_data_or_new('categories', lambda: Category.objects.all(), 60 * 60)
        return queryset.order_by('name')

    def get_permissions(self):
        if self.action in ('create', 'update', 'destroy'):
            self.permission_classes = (IsAdminUser,)
        return super().get_permissions()


class RecipeModelViewSet(CacheMixin, ModelViewSet):
    serializer_class = RecipeSerializer
    pagination_class = RecipePageNumberPagination
    queryset = Recipe.objects.all()
    ordering = ('name',)

    def get_queryset(self):
        initial_queryset = self.get_cached_data_or_new('recipes', lambda: self.queryset, 60 * 60)
        search = self.request.query_params.get('search')
        category_slug = self.request.query_params.get('category_slug')
        if search:
            queryset = initial_queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        elif category_slug:
            queryset = initial_queryset.filter(category__slug=category_slug)
        else:
            queryset = initial_queryset
        return queryset.order_by(*self.ordering)

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


class CommentGenericViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    authentication_classes = (SessionAuthentication,)
    serializer_class = CommentSerializer
    pagination_class = CommentPageNumberPagination

    def list(self, request, *args, **kwargs):
        recipe_id = request.GET.get('recipe_id')
        if not recipe_id:
            return Response({'recipe_id': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        comments = Comment.objects.filter(recipe_id=recipe_id).order_by('-created_date')
        paginated_comments = self.paginate_queryset(comments)
        serializer = self.serializer_class(paginated_comments, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.action in ('create', 'update', 'destroy'):
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()


class RecipeBookmarkGenericViewSet(GenericViewSet, ListModelMixin, CreateModelMixin, DestroyModelMixin):
    authentication_classes = (SessionAuthentication,)
    serializer_class = RecipeBookmarkSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = RecipePageNumberPagination
    ordering = ('-created_date',)

    def list(self, request, *args, **kwargs):
        bookmarks = RecipeBookmark.objects.filter(user=request.user).prefetch_related('recipe').order_by(*self.ordering)
        paginated_bookmarks = self.paginate_queryset(bookmarks)
        serializer = self.serializer_class(paginated_bookmarks, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        recipe_id = request.data.get('recipe_id')
        if not recipe_id:
            return Response({'recipe_id': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        recipe.bookmarks.add(request.user, through_defaults=None)
        bookmark = RecipeBookmark.objects.get(recipe=recipe, user=request.user)
        serializer = self.serializer_class(bookmark)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe_id = kwargs.get('pk')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = get_object_or_404(User, id=request.user.id, recipe=recipe)
        recipe.bookmarks.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
