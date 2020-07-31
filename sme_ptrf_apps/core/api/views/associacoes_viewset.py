import datetime
import logging

from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers.acao_associacao_serializer import AcaoAssociacaoLookUpSerializer
from ..serializers.associacao_serializer import (AssociacaoCreateSerializer, AssociacaoSerializer,
                                                 AssociacaoListSerializer, AssociacaoCompletoSerializer)
from ..serializers.conta_associacao_serializer import (
    ContaAssociacaoCreateSerializer,
    ContaAssociacaoDadosSerializer,
    ContaAssociacaoLookUpSerializer,
)
from ..serializers.periodo_serializer import PeriodoLookUpSerializer
from ...models import Associacao, ContaAssociacao, Periodo, Unidade
from ...services import (
    implanta_saldos_da_associacao,
    implantacoes_de_saldo_da_associacao,
    info_acoes_associacao_no_periodo,
    status_aceita_alteracoes_em_transacoes,
    status_periodo_associacao,
)

logger = logging.getLogger(__name__)


class AssociacoesViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         GenericViewSet, ):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = Associacao.objects.all()
    serializer_class = AssociacaoSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filter_fields = ('unidade__dre__uuid', 'status_regularidade', 'unidade__tipo_unidade')

    def get_serializer_class(self):
        if self.action =='retrieve':
            return AssociacaoCompletoSerializer
        elif self.action == 'list':
            return AssociacaoListSerializer
        else:
            return AssociacaoCreateSerializer

    def get_queryset(self):
        qs = Associacao.objects.all()

        nome = self.request.query_params.get('nome')
        if nome is not None:
            qs = qs.filter(Q(nome__unaccent__icontains=nome) | Q(
                unidade__nome__unaccent__icontains=nome))

        return qs

    @action(detail=True, url_path='painel-acoes')
    def painel_acoes(self, request, uuid=None):

        periodo = None

        periodo_uuid = request.query_params.get('periodo_uuid')
        if periodo_uuid:
            periodo = Periodo.by_uuid(periodo_uuid)

        if not periodo:
            periodo = Periodo.periodo_atual()

        periodo_status = status_periodo_associacao(periodo_uuid=periodo.uuid, associacao_uuid=uuid)
        ultima_atualizacao = datetime.datetime.now()
        info_acoes = info_acoes_associacao_no_periodo(associacao_uuid=uuid, periodo=periodo)

        info_acoes = [info for info in info_acoes if
                      info['saldo_reprogramado'] or info['receitas_no_periodo'] or info['despesas_no_periodo']]

        result = {
            'associacao': f'{uuid}',
            'periodo_referencia': periodo.referencia,
            'periodo_status': periodo_status,
            'data_inicio_realizacao_despesas': f'{periodo.data_inicio_realizacao_despesas if periodo else ""}',
            'data_fim_realizacao_despesas': f'{periodo.data_fim_realizacao_despesas if periodo else ""}',
            'data_prevista_repasse': f'{periodo.data_prevista_repasse if periodo else ""}',
            'ultima_atualizacao': f'{ultima_atualizacao}',
            'info_acoes': info_acoes
        }

        return Response(result)

    @action(detail=True, url_path='status-periodo')
    def status_periodo(self, request, uuid=None):

        data = request.query_params.get('data')

        if data is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar a data que você quer consultar o status.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        periodo = Periodo.da_data(data)
        if periodo:
            periodo_referencia = periodo.referencia
            periodo_status = status_periodo_associacao(periodo_uuid=periodo.uuid, associacao_uuid=uuid)
            aceita_alteracoes = status_aceita_alteracoes_em_transacoes(periodo_status)
        else:
            periodo_referencia = ''
            periodo_status = 'PERIODO_NAO_ENCONTRADO'
            aceita_alteracoes = True

        result = {
            'associacao': f'{uuid}',
            'periodo_referencia': periodo_referencia,
            'periodo_status': periodo_status,
            'aceita_alteracoes': aceita_alteracoes,
        }

        return Response(result)

    @action(detail=True, url_path='permite-implantacao-saldos', methods=['get'])
    def permite_implantacao_saldos(self, request, uuid=None):

        associacao = self.get_object()

        result = None

        if not associacao.periodo_inicial:
            result = {
                'permite_implantacao': False,
                'erro': 'periodo_inicial_nao_definido',
                'mensagem': 'Período inicial não foi definido para essa associação. Verifique com o administrador.'
            }

        if associacao.prestacoes_de_conta_da_associacao.exists():
            result = {
                'permite_implantacao': False,
                'erro': 'prestacao_de_contas_existente',
                'mensagem': 'Os saldos não podem ser implantados, já existe uma prestação de contas da associação.'
            }

        if not result:
            result = {
                'permite_implantacao': True,
                'erro': '',
                'mensagem': 'Os saldos podem ser implantados normalmente.'
            }

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, url_path='implantacao-saldos', methods=['get'])
    def implantacao_saldos(self, request, uuid=None):

        associacao = self.get_object()

        if not associacao.periodo_inicial:
            erro = {
                'erro': 'periodo_inicial_nao_definido',
                'mensagem': 'Período inicial não foi definido para essa associação. Verifique com o administrador.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if associacao.prestacoes_de_conta_da_associacao.exists():
            erro = {
                'erro': 'prestacao_de_contas_existente',
                'mensagem': 'Os saldos não podem ser implantados, já existe uma prestação de contas da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        saldos = []
        implantacoes = implantacoes_de_saldo_da_associacao(associacao=associacao)
        for implantacao in implantacoes:
            saldo = {
                'acao_associacao': AcaoAssociacaoLookUpSerializer(implantacao['acao_associacao']).data,
                'conta_associacao': ContaAssociacaoLookUpSerializer(implantacao['conta_associacao']).data,
                'aplicacao': implantacao['aplicacao'],
                'saldo': implantacao['saldo']
            }
            saldos.append(saldo)

        result = {
            'associacao': f'{uuid}',
            'periodo': PeriodoLookUpSerializer(associacao.periodo_inicial).data,
            'saldos': saldos,
        }

        return Response(result)

    @action(detail=True, url_path='implanta-saldos', methods=['post'])
    def implanta_saldos(self, request, uuid=None):

        associacao = self.get_object()

        saldos = request.data.get('saldos', None)

        if not saldos:
            result_error = {
                'erro': 'campo_requerido',
                'mensagem': 'É necessário enviar os saldos para implantação.'
            }
            return Response(result_error, status=status.HTTP_400_BAD_REQUEST)

        resultado_implantacao = implanta_saldos_da_associacao(associacao=associacao, saldos=saldos)

        if resultado_implantacao['saldo_implantado']:
            result = {
                'associacao': f'{uuid}',
                'periodo': PeriodoLookUpSerializer(associacao.periodo_inicial).data,
                'saldos': saldos,
            }
            status_code = status.HTTP_200_OK
        else:
            result = {
                'erro': resultado_implantacao['codigo_erro'],
                'mensagem': resultado_implantacao['mensagem']
            }
            status_code = status.HTTP_400_BAD_REQUEST

        return Response(result, status=status_code)

    @action(detail=True, url_path='contas', methods=['get'])
    def contas(self, request, uuid=None):
        associacao = self.get_object()
        contas = ContaAssociacao.objects.filter(associacao=associacao).all()
        contas_data = ContaAssociacaoDadosSerializer(contas, many=True).data
        return Response(contas_data)

    @action(detail=True, url_path='contas-update', methods=['post'])
    def contas_update(self, request, uuid=None):
        logger.info("Atualizando Contas da Associação: %s", uuid)

        lista_contas = self.request.data

        if not lista_contas:
            resultado = {
                'erro': 'Lista Vazia',
                'mensagem': 'A lista de contas está vazia.'
            }

            status_code = status.HTTP_400_BAD_REQUEST
            logger.info('Erro: %r', resultado)

        for dado_conta in lista_contas:
            try:
                conta_associacao = ContaAssociacao.objects.get(uuid=dado_conta['uuid'])
            except ContaAssociacao.DoesNotExist:
                resultado = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto conta-associação para o uuid {dado_conta['uuid']} não foi encontrado na base."
                }
                status_code = status.HTTP_404_NOT_FOUND
                logger.info('Erro: %r', resultado)

            conta_serializer = ContaAssociacaoCreateSerializer(conta_associacao, data=dado_conta, partial=True)
            if conta_serializer.is_valid(raise_exception=False):
                conta_serializer.save()
            else:
                logger.info('Erro: %r', conta_serializer.errors)
                resultado = {
                    'erro': 'Erro de validação',
                    'mensagem': conta_serializer.errors
                }
                status_code = status.HTTP_404_NOT_FOUND

            resultado = {
                'mensagem': 'Contas atualizadas com sucesso'
            }
            status_code = status.HTTP_200_OK

        return Response(resultado, status=status_code)

    @action(detail=False, url_path='tabelas')
    def tabelas(self, request):
        result = {
            'tipos_unidade': Unidade.tipos_unidade_to_json(),
            'status_regularidade': Associacao.status_regularidade_to_json(),
        }
        return Response(result)
