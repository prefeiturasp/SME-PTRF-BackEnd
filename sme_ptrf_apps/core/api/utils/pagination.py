from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10


class CustomPagination(PageNumberPagination):
    page = DEFAULT_PAGE
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'

    pagination_query_param = 'pagination'
    desabilita_paginacao = False

    def paginate_queryset(self, queryset, request, view=None):
        # Se usarmos o parâmetro pagination=false, o queryset será retornado sem paginacao, considerando a
        # mesma estrutura de data.results
        pagination_param_value = request.query_params.get(self.pagination_query_param)
        self.desabilita_paginacao = pagination_param_value == 'false'

        if self.desabilita_paginacao is True:
            self.queryset = queryset
            return queryset

        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        if self.desabilita_paginacao:
            # sem paginacao, mantendo a estrutura de results
            return Response({
                'links': {
                    'next': None,
                    'previous': None
                },
                'count': len(data),
                'page': 1,
                'page_size': len(data),
                'results': data
            })
        else:
            return Response({
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                },
                'count': self.page.paginator.count,
                'page': int(self.request.GET.get('page', DEFAULT_PAGE)),
                'page_size': int(self.request.GET.get('page_size', self.page_size)),
                'results': data
            })
