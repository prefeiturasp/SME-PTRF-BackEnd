import logging

from django.db.utils import IntegrityError
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers import PrestacaoContaLookUpSerializer
from ...models import PrestacaoConta, Periodo, Associacao
from ...services import (concluir_prestacao_de_contas, reabrir_prestacao_de_contas)

logger = logging.getLogger(__name__)

class PrestacoesContasViewSet(mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              GenericViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = PrestacaoConta.objects.all()
    serializer_class = PrestacaoContaLookUpSerializer

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

    @action(detail=True, methods=['patch'])
    def reabrir(self, request, uuid):
        prestacao_de_conta_revista = reabrir_prestacao_de_contas(prestacao_contas_uuid=uuid)
        return Response(PrestacaoContaLookUpSerializer(prestacao_de_conta_revista, many=False).data,
                        status=status.HTTP_200_OK)


    @action(detail=True, methods=['get'])
    def ata(self, request, uuid):
        #TODO Rever endpoint ata
        return self._funcionalidade_ata_inativa()
        #
        # prestacao_conta = PrestacaoConta.by_uuid(uuid)
        #
        # ata = prestacao_conta.ultima_ata()
        #
        # if not ata:
        #     erro = {
        #         'mensagem': 'Ainda não existe uma ata para essa prestação de contas.'
        #     }
        #     return Response(erro, status=status.HTTP_404_NOT_FOUND)
        #
        # return Response(AtaLookUpSerializer(ata, many=False).data, status=status.HTTP_200_OK)

    def _funcionalidade_ata_inativa(self):
        #TODO Remover método após rever a funcionalidade de ata
        erro = {
            'mensagem': 'Sistema em manutenção. Funcionalidade inativa provisoriamente.'
        }
        return Response(erro, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='iniciar-ata')
    def iniciar_ata(self, request, uuid):
        #TODO Rever endpoint iniciar-ata
        return self._funcionalidade_ata_inativa()
        # prestacao_conta = PrestacaoConta.by_uuid(uuid)
        #
        # ata = prestacao_conta.ultima_ata()
        #
        # if ata:
        #     erro = {
        #         'erro': 'ata-ja-iniciada',
        #         'mensagem': 'Já existe uma ata iniciada para essa prestação de contas.'
        #     }
        #     return Response(erro, status=status.HTTP_409_CONFLICT)
        #
        # ata = Ata.iniciar(prestacao_conta=prestacao_conta)
        #
        # return Response(AtaLookUpSerializer(ata, many=False).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='info-para-ata')
    def info_para_ata(self, request, uuid):
        #TODO Rever endpoint info-para-ata
        return self._funcionalidade_ata_inativa()
        # prestacao_conta = self.get_object()
        # result = informacoes_financeiras_para_atas(prestacao_contas=prestacao_conta)
        # return Response(result, status=status.HTTP_200_OK)


    @action(detail=False, methods=['get'], url_path='fique-de-olho')
    def fique_de_olho(self, request, uuid=None):
        from sme_ptrf_apps.core.models import Parametros
        fique_de_olho = Parametros.get().fique_de_olho

        return Response({'detail': fique_de_olho}, status=status.HTTP_200_OK)
