import logging

from django.db.models import Sum
from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao,
    PermissaoAPITodosComGravacao
)

from ....core.models import Associacao, Parametros, Periodo
from ....core.services import saldos_insuficientes_para_rateios
from ...models import RateioDespesa
from ..serializers.rateio_despesa_serializer import RateioDespesaListaSerializer

logger = logging.getLogger(__name__)


class RateiosDespesasViewSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             GenericViewSet):
    lookup_field = 'uuid'
    queryset = RateioDespesa.objects.all().order_by('-despesa__data_documento')
    serializer_class = RateioDespesaListaSerializer
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    ordering_fields = ('data_documento',)
    filter_fields = ('aplicacao_recurso', 'acao_associacao__uuid', 'despesa__status', 'associacao__uuid', 'conferido')

    def get_queryset(self):
        associacao_uuid = self.request.query_params.get('associacao_uuid') or self.request.query_params.get('associacao__uuid')
        if associacao_uuid is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da associação como parâmetro..'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        qs = RateioDespesa.objects.filter(associacao__uuid=associacao_uuid).all().order_by('-despesa__data_documento')

        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')
        if data_inicio is not None and data_fim is not None:
            qs = qs.filter(despesa__data_documento__range=[data_inicio, data_fim])

        fornecedor = self.request.query_params.get('fornecedor')
        if fornecedor is not None:
            qs = qs.filter(despesa__nome_fornecedor__unaccent__icontains=fornecedor)

        search = self.request.query_params.get('search')
        if search is not None:
            qs = qs.filter(especificacao_material_servico__descricao__unaccent__icontains=search)

        return qs

    def get_serializer_class(self):
        return RateioDespesaListaSerializer

    @action(detail=True, methods=['patch'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def conciliar(self, request, uuid):

        # Define o período de conciliação
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período de conciliação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        rateio_despesa_conciliado = RateioDespesa.conciliar(uuid=uuid, periodo_conciliacao=periodo)
        return Response(RateioDespesaListaSerializer(rateio_despesa_conciliado, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def desconciliar(self, request, uuid):
        rateio_despesa_desconciliado = RateioDespesa.desconciliar(uuid=uuid)
        return Response(RateioDespesaListaSerializer(rateio_despesa_desconciliado, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=False, url_path='verificar-saldos', methods=['post'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
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
                'aceitar_lancamento': Parametros.get().permite_saldo_conta_negativo
            }
        else:
            result = {
                'situacao_do_saldo': 'saldo_insuficiente',
                'mensagem': 'Não há saldo disponível em alguma das ações da despesa.',
                'saldos_insuficientes': saldos_insuficientes['saldos_insuficientes'],
                'aceitar_lancamento': True
            }

        return Response(result)

    @action(detail=False, url_path='totais', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def totais(self, request):
        associacao__uuid = request.query_params.get('associacao__uuid')

        if not associacao__uuid:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da conta da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        associacao = Associacao.by_uuid(associacao__uuid)

        queryset = RateioDespesa.objects.filter(associacao=associacao).all().order_by('-despesa__data_documento')
        filtered_queryset = self.get_queryset()
        for field in self.filter_fields:
            filter_value = request.query_params.get(field)
            if filter_value:
                filtered_queryset = filtered_queryset.filter(**{field: filter_value})

        total_despesas_com_filtro = filtered_queryset.aggregate(Sum('valor_rateio'))['valor_rateio__sum']
        total_despesas_sem_filtro = queryset.aggregate(Sum('valor_rateio'))['valor_rateio__sum']

        result = {
            "associacao_uuid": f'{associacao__uuid}',
            "total_despesas_sem_filtro": total_despesas_sem_filtro,
            "total_despesas_com_filtro": total_despesas_com_filtro
        }
        return Response(result)
