from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class CategoryPageNumberPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 32


class RecipePageNumberPagination(PageNumberPagination):
    page_size = settings.RECIPES_PAGINATE_BY
    page_size_query_param = 'page_size'
    max_page_size = 32
