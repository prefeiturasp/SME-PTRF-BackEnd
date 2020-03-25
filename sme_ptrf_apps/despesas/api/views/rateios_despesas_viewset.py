from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny

from ..serializers.rateio_despesa_serializer import RateioDespesaListaSerializer
from ...models import RateioDespesa


class RateiosDespesasViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = RateioDespesa.objects.all().order_by('-despesa__data_documento')
    serializer_class = RateioDespesaListaSerializer
    permission_classes = [AllowAny]
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    ordering_fields = ('data_documento',)
    search_fields = ('uuid', 'id', 'especificacao_material_servico.descricao')

    def get_queryset(self):
        return self.queryset

    def get_serializer_class(self):
        return RateioDespesaListaSerializer
