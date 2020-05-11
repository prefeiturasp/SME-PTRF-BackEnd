from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..serializers.rateio_despesa_serializer import RateioDespesaListaSerializer
from ...models import RateioDespesa


class RateiosDespesasViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = RateioDespesa.objects.all().order_by('-despesa__data_documento')
    serializer_class = RateioDespesaListaSerializer
    permission_classes = [AllowAny]
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    ordering_fields = ('data_documento',)
    search_fields = ('uuid', 'id', 'especificacao_material_servico__descricao')
    filter_fields = ('aplicacao_recurso', 'acao_associacao__uuid', 'despesa__status', 'associacao__uuid', 'conferido')

    def get_queryset(self):
        user = self.request.user
        return RateioDespesa.objects.filter(associacao__usuario=user).all().order_by('-despesa__data_documento')

    def get_serializer_class(self):
        return RateioDespesaListaSerializer

    @action(detail=True, methods=['patch'])
    def conciliar(self, request, uuid):
        rateio_despesa_conciliado = RateioDespesa.conciliar(uuid=uuid)
        return Response(RateioDespesaListaSerializer(rateio_despesa_conciliado, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def desconciliar(self, request, uuid):
        rateio_despesa_desconciliado = RateioDespesa.desconciliar(uuid=uuid)
        return Response(RateioDespesaListaSerializer(rateio_despesa_desconciliado, many=False).data,
                        status=status.HTTP_200_OK)
