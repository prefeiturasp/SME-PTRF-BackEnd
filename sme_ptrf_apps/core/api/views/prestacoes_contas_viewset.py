import logging

from django.db.models import Q
from django.db.utils import IntegrityError
from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers import (PrestacaoContaLookUpSerializer, PrestacaoContaListSerializer,
                           PrestacaoContaRetrieveSerializer, AtaLookUpSerializer)
from ...models import PrestacaoConta, Periodo, Associacao, Ata, Unidade
from ...services import (concluir_prestacao_de_contas, reabrir_prestacao_de_contas, informacoes_financeiras_para_atas)
from ....dre.models import TecnicoDre, Atribuicao

logger = logging.getLogger(__name__)


class PrestacoesContasViewSet(mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.ListModelMixin,
                              GenericViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = PrestacaoConta.objects.all()
    serializer_class = PrestacaoContaLookUpSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filter_fields = ('associacao__unidade__dre__uuid', 'periodo__uuid', 'associacao__unidade__tipo_unidade')

    def get_queryset(self):
        qs = PrestacaoConta.objects.all()

        status = self.request.query_params.get('status')
        if status is not None:
            if status in ['APROVADA', 'APROVADA_RESSALVA']:
                qs = qs.filter(Q(status='APROVADA') | Q(status='APROVADA_RESSALVA'))
            else:
                qs = qs.filter(status=status)

        nome = self.request.query_params.get('nome')
        if nome is not None:
            qs = qs.filter(Q(associacao__nome__unaccent__icontains=nome) | Q(
                associacao__unidade__nome__unaccent__icontains=nome))

        dre_uuid = self.request.query_params.get('associacao__unidade__dre__uuid')
        periodo_uuid = self.request.query_params.get('periodo__uuid')
        tecnico_uuid = self.request.query_params.get('tecnico')
        if tecnico_uuid and dre_uuid and periodo_uuid:

            try:
                dre = Unidade.dres.get(uuid=dre_uuid)
            except Unidade.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
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

            try:
                tecnico = TecnicoDre.objects.get(uuid=tecnico_uuid)
            except TecnicoDre.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto tecnico_dre para o uuid {tecnico_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

            atribuicoes = Atribuicao.objects.filter(
                tecnico=tecnico,
                periodo=periodo,
                unidade__dre=dre
            ).values_list('unidade__codigo_eol', flat=True)

            qs = qs.filter(associacao__unidade__codigo_eol__in=atribuicoes)

        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')
        if data_inicio is not None and data_fim is not None:
            qs = qs.filter(data_recebimento__range=[data_inicio, data_fim])

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return PrestacaoContaListSerializer
        elif self.action == 'retrieve':
            return PrestacaoContaRetrieveSerializer
        else:
            return PrestacaoContaLookUpSerializer

    @action(detail=False, url_path='por-associacao-e-periodo')
    def por_associacao_e_periodo(self, request):
        associacao_uuid = request.query_params.get('associacao_uuid')
        periodo_uuid = request.query_params.get('periodo_uuid')
        return Response(PrestacaoContaLookUpSerializer(
            self.queryset.filter(associacao__uuid=associacao_uuid).filter(
                periodo__uuid=periodo_uuid).first(), many=False).data)

    @action(detail=False, methods=['post'])
    def concluir(self, request):
        associacao_uuid = request.query_params.get('associacao_uuid')
        if not associacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da associação.'
            }
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

        periodo_uuid = request.query_params.get('periodo_uuid')
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

        try:
            prestacao_de_contas = concluir_prestacao_de_contas(associacao=associacao, periodo=periodo)
        except(IntegrityError):
            erro = {
                'erro': 'prestacao_ja_iniciada',
                'mensagem': 'Você não pode iniciar uma prestação de contas que já foi iniciada.'
            }
            return Response(erro, status=status.HTTP_409_CONFLICT)

        return Response(PrestacaoContaLookUpSerializer(prestacao_de_contas, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def reabrir(self, request, uuid):
        reaberta = reabrir_prestacao_de_contas(prestacao_contas_uuid=uuid)
        if reaberta:
            response = {
                'uuid': f'{uuid}',
                'mensagem': 'Prestação de contas reaberta com sucesso. Todos os seus registros foram apagados.'
            }
            return Response(response, status=status.HTTP_204_NO_CONTENT)
        else:
            response = {
                'uuid': f'{uuid}',
                'mensagem': 'Houve algum erro ao tentar reabrir a prestação de contas.'
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def receber(self, request, uuid):
        prestacao_conta = self.get_object()

        data_recebimento = request.data.get('data_recebimento', None)
        if not data_recebimento:
            response = {
                'uuid': f'{uuid}',
                'mensagem': 'Faltou informar a data de recebimento da Prestação de Contas.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prestacao_recebida = prestacao_conta.receber(data_recebimento=data_recebimento)

        return Response(PrestacaoContaRetrieveSerializer(prestacao_recebida, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='desfazer-recebimento')
    def desfazer_recebimento(self, request, uuid):
        prestacao_conta = self.get_object()

        if prestacao_conta.status != PrestacaoConta.STATUS_RECEBIDA:
            response = {
                'uuid': f'{prestacao_conta.uuid}',
                'status': prestacao_conta.status,
                'erro': 'operacao_nao_permitida',
                'mensagem': 'Impossível desfazer recebimento de uma PC com status diferente de RECEBIDA.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prestacao_atualizada = prestacao_conta.desfazer_recebimento()

        return Response(PrestacaoContaRetrieveSerializer(prestacao_atualizada, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def ata(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        ata = prestacao_conta.ultima_ata()

        if not ata:
            erro = {
                'mensagem': 'Ainda não existe uma ata para essa prestação de contas.'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        return Response(AtaLookUpSerializer(ata, many=False).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='iniciar-ata')
    def iniciar_ata(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        ata = prestacao_conta.ultima_ata()

        if ata:
            erro = {
                'erro': 'ata-ja-iniciada',
                'mensagem': 'Já existe uma ata iniciada para essa prestação de contas.'
            }
            return Response(erro, status=status.HTTP_409_CONFLICT)

        ata = Ata.iniciar(prestacao_conta=prestacao_conta)

        return Response(AtaLookUpSerializer(ata, many=False).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='info-para-ata')
    def info_para_ata(self, request, uuid):
        prestacao_conta = self.get_object()
        result = informacoes_financeiras_para_atas(prestacao_contas=prestacao_conta)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='fique-de-olho')
    def fique_de_olho(self, request, uuid=None):
        from sme_ptrf_apps.core.models import Parametros
        fique_de_olho = Parametros.get().fique_de_olho

        return Response({'detail': fique_de_olho}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path="dashboard")
    def dashboard(self, request):
        dre_uuid = request.query_params.get('dre_uuid')
        periodo = request.query_params.get('periodo')

        if not dre_uuid or not periodo:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da dre (dre_uuid) e o periodo como parâmetros.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        total_associacoes_dre = Associacao.objects.filter(unidade__dre__uuid=dre_uuid).count()

        cards = PrestacaoConta.dashboard(periodo, dre_uuid)
        dashboard = {
            "total_associacoes_dre": total_associacoes_dre,
            "cards": cards
        }

        return Response(dashboard)

    @action(detail=False, url_path='tabelas')
    def tabelas(self, _):
        result = {
            'status': PrestacaoConta.status_to_json(),
        }
        return Response(result)
