from rest_framework import pagination


class MaxSizePerPage30(pagination.PageNumberPagination):
    page_size = 30


class MaxSizePerPage10(pagination.PageNumberPagination):
    page_size = 10


class MaxSizePerPage5(pagination.PageNumberPagination):
    page_size = 5
