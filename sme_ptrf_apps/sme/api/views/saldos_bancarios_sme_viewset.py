import logging

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from ...services.saldo_bancario_service import saldo_por_tipo_de_unidade, saldo_por_dre, saldo_por_ue_dre

from sme_ptrf_apps.core.models.observacao_conciliacao import ObservacaoConciliacao
from sme_ptrf_apps.core.models.periodo import Periodo
from sme_ptrf_apps.core.models.tipo_conta import TipoConta

from sme_ptrf_apps.users.permissoes import PermissaoAPIApenasSmeComLeituraOuGravacao

logger = logging.getLogger(__name__)


class SaldosBancariosSMEViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao]
    queryset = ObservacaoConciliacao.objects.all()

    @action(detail=False, methods=['get'], url_path='saldo-por-tipo-unidade',
            permission_classes=[IsAuthenticated, PermissaoAPIApenasSmeComLeituraOuGravacao])
    def saldo_por_tipo_de_unidade(self, request):
        periodo_uuid = request.query_params.get('periodo')
        conta_uuid = request.query_params.get('conta')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'saldo-por-tipo-unidade',
                'mensagem': 'Faltou informar o uuid do periodo. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            Periodo.objects.get(uuid=periodo_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if not conta_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'saldo-por-tipo-unidade',
                'mensagem': 'Faltou informar o uuid da conta. ?conta=uuid_da_conta'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            TipoConta.objects.get(uuid=conta_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto tipo_conta para o uuid {conta_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        saldos = saldo_por_tipo_de_unidade(self.queryset, periodo=periodo_uuid, conta=conta_uuid)

        return Response(saldos, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='saldo-por-dre',
            permission_classes=[IsAuthenticated, PermissaoAPIApenasSmeComLeituraOuGravacao])
    def saldo_por_dre(self, request):
        periodo_uuid = request.query_params.get('periodo')
        conta_uuid = request.query_params.get('conta')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'saldo-por-dre',
                'mensagem': 'Faltou informar o uuid do periodo. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            Periodo.objects.get(uuid=periodo_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if not conta_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'saldo-por-dre',
                'mensagem': 'Faltou informar o uuid da conta. ?conta=uuid_da_conta'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            TipoConta.objects.get(uuid=conta_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto tipo_conta para o uuid {conta_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        saldos = saldo_por_dre(self.queryset, periodo=periodo_uuid, conta=conta_uuid)

        return Response(saldos, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='saldo-por-ue-dre',
            permission_classes=[IsAuthenticated, PermissaoAPIApenasSmeComLeituraOuGravacao])
    def saldo_por_ue_dre(self, request):
        periodo_uuid = request.query_params.get('periodo')
        conta_uuid = request.query_params.get('conta')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'saldo-por-ue-dre',
                'mensagem': 'Faltou informar o uuid do periodo. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            Periodo.objects.get(uuid=periodo_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if not conta_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'saldo-por-ue-dre',
                'mensagem': 'Faltou informar o uuid da conta. ?conta=uuid_da_conta'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            TipoConta.objects.get(uuid=conta_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto tipo_conta para o uuid {conta_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        saldos = saldo_por_ue_dre(self.queryset, periodo=periodo_uuid, conta=conta_uuid)

        return Response(saldos, status=status.HTTP_200_OK)

