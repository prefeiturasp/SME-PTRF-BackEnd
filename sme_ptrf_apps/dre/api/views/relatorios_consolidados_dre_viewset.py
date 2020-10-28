import logging

from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import status

from sme_ptrf_apps.core.models import (
    Unidade,
    Periodo,
    TipoConta,
)
from ...models import RelatorioConsolidadoDRE

from ...services import status_de_geracao_do_relatorio

logger = logging.getLogger(__name__)

class RelatoriosConsolidadosDREViewSet(GenericViewSet):

    permission_classes = [AllowAny]
    queryset = RelatorioConsolidadoDRE.objects.all()

    @action(detail=False, methods=['get'], url_path='fique-de-olho')
    def fique_de_olho(self, request, uuid=None):
        from sme_ptrf_apps.core.models import Parametros
        fique_de_olho = Parametros.get().fique_de_olho_relatorio_dre
        return Response({'detail': fique_de_olho}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='status-relatorio')
    def status_relatorio(self, request):
        from rest_framework import status
        # Determina a DRE
        dre_uuid = self.request.query_params.get('dre')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'status-relatorio',
                'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except Unidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o tipo de conta
        tipo_conta_uuid = self.request.query_params.get('tipo_conta')

        if not tipo_conta_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'status-relatorio',
                'mensagem': 'Faltou informar o uuid do tipo de conta. ?tipo_conta=uuid_do_tipo_conta'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            tipo_conta = TipoConta.objects.get(uuid=tipo_conta_uuid)
        except TipoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto tipo de conta para o uuid {tipo_conta_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'status-relatorio',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
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


        status = status_de_geracao_do_relatorio(dre=dre, periodo=periodo, tipo_conta=tipo_conta)

        return Response(status)
