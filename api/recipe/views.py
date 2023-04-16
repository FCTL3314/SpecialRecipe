
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, UpdateModelMixin)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from api.recipe.pagination import (CategoryPageNumberPagination,
                                   CommentPageNumberPagination,
                                   RecipePageNumberPagination)
from api.recipe.serializers import (CategorySerializer, CommentSerializer,
                                    IngredientSerializer,
                                    RecipeBookmarkSerializer, RecipeSerializer)
from interactions.models import RecipeBookmark
from recipe.models import Category, Ingredient, Recipe


class CategoryModelViewSet(ModelViewSet):
    model = Category
    serializer_class = CategorySerializer
    pagination_class = CategoryPageNumberPagination

    def get_queryset(self):
        queryset = self.model.objects.cached_queryset()
        return queryset.order_by('name')

    def get_permissions(self):
        if self.action in ('create', 'update', 'destroy'):
            self.permission_classes = (IsAdminUser,)
        return super().get_permissions()


class RecipeModelViewSet(ModelViewSet):
    model = Recipe
    serializer_class = RecipeSerializer
    pagination_class = RecipePageNumberPagination
    ordering = ('name',)

    def get_queryset(self):
        queryset = self.model.objects.cached_queryset()

        selected_category_slug = self.request.query_params.get('category_slug')
        search = self.request.query_params.get('search')

        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        elif selected_category_slug:
            queryset = queryset.filter(category__slug=selected_category_slug)

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
        recipe = get_object_or_404(Recipe, id=recipe_id)
        comments = recipe.comments().order_by('-created_date')
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
    model = RecipeBookmark
    authentication_classes = (SessionAuthentication,)
    serializer_class = RecipeBookmarkSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = RecipePageNumberPagination
    ordering = ('-created_date',)

    def list(self, request, *args, **kwargs):
        bookmarks = RecipeBookmark.objects.user_bookmarks(request.user).order_by(*self.ordering)
        paginated_bookmarks = self.paginate_queryset(bookmarks)
        serializer = self.serializer_class(paginated_bookmarks, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        recipe_id = request.data.get('recipe_id')
        if not recipe_id:
            return Response({'recipe_id': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        recipe.bookmarks.add(request.user, through_defaults=None)
        bookmark = self.model.objects.get(recipe=recipe, user=request.user)
        serializer = self.serializer_class(bookmark)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe_id = kwargs.get('pk')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        recipe.bookmarks.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
