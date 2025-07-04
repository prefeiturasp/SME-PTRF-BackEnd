import logging

from datetime import datetime

from django.db.models import Sum
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CHOICES
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_CHOICES
from sme_ptrf_apps.despesas.services.filtra_despesas_por_tags import filtra_despesas_por_tags

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao,
    PermissaoAPITodosComGravacao
)

from ....core.models import Associacao, Periodo
from ....core.services import valida_rateios_quanto_aos_saldos
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
    filterset_fields = (
        'aplicacao_recurso',
        'acao_associacao__uuid',
        'despesa__status',
        'associacao__uuid',
        'conferido',
        'conta_associacao__uuid',
        'tag__uuid'
    )

    def get_queryset(self):
        if self.action == 'retrieve':
            return RateioDespesa.objects.filter(uuid=self.kwargs['uuid'])

        associacao_uuid = self.request.query_params.get('associacao_uuid') \
            or self.request.query_params.get('associacao__uuid')
        if associacao_uuid is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da associação como parâmetro..'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        qs = RateioDespesa.objects.filter(associacao__uuid=associacao_uuid).all().order_by('-despesa__data_documento')

        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')
        if data_inicio is not None and data_fim is not None and data_inicio != '' and data_fim != '':
            qs = qs.filter(despesa__data_documento__range=[data_inicio, data_fim])

        fornecedor = self.request.query_params.get('fornecedor')
        if fornecedor is not None and fornecedor != '':
            qs = qs.filter(despesa__nome_fornecedor__unaccent__icontains=fornecedor)

        search = self.request.query_params.get('search')
        if search is not None and search != '':
            qs = qs.filter(especificacao_material_servico__descricao__unaccent__icontains=search)

        return qs

    def get_serializer_class(self):
        return RateioDespesaListaSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='uuid', description='UUID do Rateio despesa', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.PATH),
            OpenApiParameter(name='periodo', description='UUID do Período', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        description="Conciliação de despesas."
    )
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

    @extend_schema(
        parameters=[
            OpenApiParameter(name='despesa_uuid', description='UUID da despesa para exclude', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        description="Verifica Saldos"
    )
    @action(detail=False, url_path='verificar-saldos', methods=['post'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def verificar_saldos(self, request):
        despesa_uuid = request.query_params.get('despesa_uuid')

        despesa = request.data
        data_documento = datetime.strptime(despesa['data_transacao'], '%Y-%m-%d').date()
        associacao_uuid = despesa['associacao']

        if not associacao_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'verificar saldos',
                'mensagem': 'O UUID da associação não foi enviado na requisição'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associação para o uuid {associacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = valida_rateios_quanto_aos_saldos(
            rateios=despesa['rateios'],
            associacao=associacao,
            data_documento=data_documento,
            exclude_despesa=despesa_uuid
        )

        return Response(result)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='associacao__uuid', description='UUID da Associação', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='aplicacao_recurso', description='Tipo de Aplicação', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                             enum=[i[0] for i in APLICACAO_CHOICES]),
            OpenApiParameter(name='acao_associacao__uuid', description='UUID da Ação Associação', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='despesa__status', description='Status de despesas', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                             enum=[i[0] for i in STATUS_CHOICES]),
            OpenApiParameter(name='associacao__uuid', description='UUID da Associação', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='conferido', description='Conferido?', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, enum=['True', 'False']),
            OpenApiParameter(name='conta_associacao__uuid', description='UUID da Conta Associação', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='tag__uuid', description='UUID da Tag', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        description="Valores totais"
    )
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

        queryset = RateioDespesa.objects \
            .filter(associacao=associacao).exclude(despesa__status='INATIVO').all().order_by('-despesa__data_documento')
        filtered_queryset = self.get_queryset()
        for field in self.filterset_fields:
            filter_value = request.query_params.get(field)
            if filter_value:
                filtered_queryset = filtered_queryset.exclude(despesa__status='INATIVO').filter(**{field: filter_value})

        filtro_informacoes = self.request.query_params.get('filtro_informacoes')
        filtro_informacoes_list = filtro_informacoes.split(',') if filtro_informacoes else []

        if filtro_informacoes_list:
            ids_para_excluir = [
                item.id for item in filtered_queryset if filtra_despesas_por_tags(item, filtro_informacoes_list)]
            filtered_queryset = filtered_queryset.exclude(id__in=ids_para_excluir)

        filtro_vinculo_atividades = self.request.query_params.get('filtro_vinculo_atividades')
        filtro_vinculo_atividades_list = filtro_vinculo_atividades.split(',') if filtro_vinculo_atividades else []

        if filtro_vinculo_atividades_list:
            filtered_queryset = filtered_queryset.filter(tag__in=filtro_vinculo_atividades_list)

        total_despesas_com_filtro = filtered_queryset.aggregate(Sum('valor_rateio'))['valor_rateio__sum']
        total_despesas_sem_filtro = queryset.aggregate(Sum('valor_rateio'))['valor_rateio__sum']

        result = {
            "associacao_uuid": f'{associacao__uuid}',
            "total_despesas_sem_filtro": total_despesas_sem_filtro,
            "total_despesas_com_filtro": total_despesas_com_filtro
        }
        return Response(result)
