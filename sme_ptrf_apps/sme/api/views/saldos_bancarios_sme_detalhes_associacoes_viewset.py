import logging

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.models.periodo import Periodo
from sme_ptrf_apps.core.models.tipo_conta import TipoConta
from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.core.models.unidade import Unidade

from sme_ptrf_apps.users.permissoes import PermissaoAPIApenasSmeComLeituraOuGravacao

from ...services.saldo_bancario_service import saldo_detalhe_associacao

from rest_framework.decorators import action
from sme_ptrf_apps.core.tasks import gerar_xlsx_extrato_dres_async

logger = logging.getLogger(__name__)


class SaldosBancariosSmeDetalhesAsocciacoesViewSet(mixins.ListModelMixin,
                                                   mixins.RetrieveModelMixin,
                                                   GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao]
    lookup_field = 'uuid'
    queryset = Associacao.objects.all()

    @action(detail=False, methods=['get'], url_path='saldos-detalhes-associacoes',
            permission_classes=[IsAuthenticated, PermissaoAPIApenasSmeComLeituraOuGravacao])
    def saldo_detalhes_associacoes(self, request):
        periodo_uuid = request.query_params.get('periodo')
        conta_uuid = request.query_params.get('conta')
        dre_uuid = request.query_params.get('dre')
        unidade = request.query_params.get('unidade')
        tipo_ue = request.query_params.get('tipo_ue')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'saldos-detalhes-associacoes',
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
                'operacao': 'saldos-detalhes-associacoes',
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

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'saldos-detalhes-associacoes',
                'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            Unidade.dres.get(uuid=dre_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        saldos = saldo_detalhe_associacao(periodo_uuid=periodo_uuid, conta_uuid=conta_uuid, dre_uuid=dre_uuid,
                                          unidade=unidade, tipo_ue=tipo_ue)

        return Response(saldos, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='exporta_xlsx_dres',
            permission_classes=[IsAuthenticated, PermissaoAPIApenasSmeComLeituraOuGravacao])
    def exporta_xlsx_dres(self, request):
        periodo_uuid = request.query_params.get('periodo')
        conta_uuid = request.query_params.get('conta')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'saldos-detalhes-associacoes',
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
                'operacao': 'saldos-detalhes-associacoes',
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

        gerar_xlsx_extrato_dres_async.delay(
            periodo_uuid=periodo_uuid,
            conta_uuid=conta_uuid,
            username=request.user.username
        )

        return Response({'mensagem': 'Arquivo na fila para processamento.'}, status=status.HTTP_200_OK)
