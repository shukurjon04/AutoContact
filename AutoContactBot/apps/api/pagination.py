"""Pagination classes for REST API."""
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Standart pagination — 20 ta element har bir sahifada."""
    page_size = 20
    page_size_query_param = 'page_size'
    page_size_query_description = "Sahifada nechta element ko'rsatish (max: 100)"
    max_page_size = 100


class LargeResultsSetPagination(PageNumberPagination):
    """Katta pagination — 100 ta element."""
    page_size = 100
    page_size_query_param = 'page_size'
    page_size_query_description = "Sahifada nechta element ko'rsatish (max: 500)"
    max_page_size = 500
