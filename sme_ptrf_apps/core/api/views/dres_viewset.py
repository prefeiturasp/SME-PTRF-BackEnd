from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers import UnidadeSerializer
from ...models import Unidade


class DresViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet, ):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = Unidade.dres.all()
    filters = (filters.DjangoFilterBackend, SearchFilter,)
    serializer_class = UnidadeSerializer
    filter_fields = ('codigo_eol')

    def get_queryset(self):
        qs = Unidade.dres.all()

        codigo_eol = self.request.query_params.get('codigo_eol')
        if codigo_eol:
            qs = qs.filter(codigo_eol=codigo_eol)

        search = self.request.query_params.get('search')
        if search is not None:
            qs = qs.filter(nome__unaccent__icontains=search)

        return qs

    @action(detail=True, url_path='qtd-unidades')
    def qtd_unidades(self, request, uuid=None):
        dre = self.get_object()
        quantidade = dre.unidades_da_dre.count()
        result = {
            "uuid": f'{uuid}',
            "qtd-unidades": quantidade,
        }

        return Response(result)
