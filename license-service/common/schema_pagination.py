"""
Schema Pagination
"""

from rest_framework.pagination import LimitOffsetPagination


class StandardLimitOffsetPagination(LimitOffsetPagination):
    """
    Standard Limit Off set Pagination
    """

    default_limit = 20
    max_limit = 100
