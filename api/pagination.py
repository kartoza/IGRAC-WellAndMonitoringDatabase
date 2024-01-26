# coding=utf-8

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class Pagination(PageNumberPagination):
    """Pagination for API."""

    page_size_query_param = 'page_size'

    def get_paginated_response_data(self, data):
        """Return paginated only data."""
        return {
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'page': self.page.number,
            'total_page': self.page.paginator.num_pages,
            'page_size': self.page.paginator.per_page,
            'results': data,
        }

    def get_paginated_response(self, data):
        """Response for pagination."""
        return Response(self.get_paginated_response_data(data))
