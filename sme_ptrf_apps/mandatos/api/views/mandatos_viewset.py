from rest_framework import viewsets

from sme_ptrf_apps.users.permissoes import PermissaoApiSME
from ...models import Mandato
from ..serializers.mandato_serializer import MandatoSerializer
from rest_framework.permissions import IsAuthenticated

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10


class CustomPagination(PageNumberPagination):
    page = DEFAULT_PAGE
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
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


class MandatosViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiSME]
    lookup_field = 'uuid'
    queryset = Mandato.objects.all().order_by('-referencia_mandato')
    serializer_class = MandatoSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = self.queryset

        filtro_referencia = self.request.query_params.get('referencia', None)

        if filtro_referencia is not None:
            qs = qs.filter(referencia_mandato__unaccent__icontains=filtro_referencia)

        return qs
