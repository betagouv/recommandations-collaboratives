from rest_framework.pagination import LimitOffsetPagination


class LargeResultsSetPagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 1000


class StandardResultsSetPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 1000
