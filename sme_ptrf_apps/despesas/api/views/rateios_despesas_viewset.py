from django.db.models import Sum
from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers.rateio_despesa_serializer import RateioDespesaListaSerializer
from ...models import RateioDespesa
from ....core.models import Periodo
from ....core.services import saldos_insuficientes_para_rateios


class RateiosDespesasViewSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             GenericViewSet):
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

    @action(detail=False, url_path='verificar-saldos', methods=['post'])
    def verificar_saldos(self, request):
        despesa_uuid = request.query_params.get('despesa_uuid')

        despesa = request.data
        data_documento = despesa['data_documento']

        if data_documento:
            periodo_despesa = Periodo.da_data(data_documento)
            rateios = despesa['rateios']
            saldos_insuficientes = saldos_insuficientes_para_rateios(
                rateios=rateios,
                periodo=periodo_despesa,
                exclude_despesa=despesa_uuid
            )
        else:
            return Response({
                'situacao_do_saldo': 'impossível_determinar',
                'mensagem': 'Sem informar a data da despesa não há como determinar o saldo disponível.',
                'saldos_insuficientes': [],
                'aceitar_lancamento': True
            })

        if not saldos_insuficientes['saldos_insuficientes']:
            return Response( {
                'situacao_do_saldo': 'saldo_suficiente',
                'mensagem': 'Há saldo disponível para cobertura da despesa.',
                'saldos_insuficientes': [],
                'aceitar_lancamento': True
            })

        if saldos_insuficientes['tipo_saldo'] == 'CONTA':
            result = {
                'situacao_do_saldo': 'saldo_conta_insuficiente',
                'mensagem': 'Não há saldo disponível em alguma das contas da despesa.',
                'saldos_insuficientes': saldos_insuficientes['saldos_insuficientes'],
                'aceitar_lancamento': False
            }
        else:
            result = {
                'situacao_do_saldo': 'saldo_insuficiente',
                'mensagem': 'Não há saldo disponível em alguma das ações da despesa.',
                'saldos_insuficientes': saldos_insuficientes['saldos_insuficientes'],
                'aceitar_lancamento': True
            }

        return Response(result)

    @action(detail=False, url_path='totais', methods=['get'])
    def totais(self, request):
        associacao__uuid = request.query_params.get('associacao__uuid')

        if not associacao__uuid:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da conta da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()
        filtered_queryset = queryset
        for field in self.filter_fields:
            filter_value = request.query_params.get(field)
            if filter_value:
                filtered_queryset = filtered_queryset.filter(**{field: filter_value})

        search_value = request.query_params.get('search')
        if search_value:
            filtered_queryset = filtered_queryset.filter(
                especificacao_material_servico__descricao__icontains=search_value)

        total_despesas_com_filtro = filtered_queryset.aggregate(Sum('valor_rateio'))['valor_rateio__sum']
        total_despesas_sem_filtro = queryset.aggregate(Sum('valor_rateio'))['valor_rateio__sum']

        result = {
            "associacao_uuid": f'{associacao__uuid}',
            "total_despesas_sem_filtro": total_despesas_sem_filtro,
            "total_despesas_com_filtro": total_despesas_com_filtro
        }
        return Response(result)
