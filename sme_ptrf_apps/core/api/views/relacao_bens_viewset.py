from datetime import datetime
from io import BytesIO

from django.http import HttpResponse
from openpyxl.writer.excel import save_virtual_workbook
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.models import (
    ContaAssociacao,
    Periodo,
    PeriodoPrevia,
    PrestacaoConta,
    RelacaoBens,
)
from sme_ptrf_apps.core.services.relacao_bens import gerar


class RelacaoBensViewSet(GenericViewSet):
    permission_classes = [AllowAny]
    queryset = RelacaoBens.objects.all()

    @action(detail=False, methods=['get'])
    def previa(self, request):
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')
        periodo_uuid = self.request.query_params.get('periodo')

        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')

        if not conta_associacao_uuid or not periodo_uuid or (not data_inicio or not data_fim):
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período o uuid da conta da associação e as datas de inicio e fim do período.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if datetime.strptime(data_fim, "%Y-%m-%d") < datetime.strptime(data_inicio, "%Y-%m-%d"):
            erro = {
                'erro': 'erro_nas_datas',
                'mensagem': 'Data fim não pode ser menor que a data inicio.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        periodo = Periodo.objects.filter(uuid=periodo_uuid).get()

        if periodo.data_fim_realizacao_despesas and datetime.strptime(data_fim, "%Y-%m-%d").date() > periodo.data_fim_realizacao_despesas:
            erro = {
                'erro': 'erro_nas_datas',
                'mensagem': 'Data fim não pode ser maior que a data fim da realização as despesas do periodo.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        periodoPrevia = PeriodoPrevia(periodo.uuid, periodo.referencia, data_inicio, data_fim)

        xlsx = self._gerar_planilha(periodoPrevia, conta_associacao_uuid, previa=True)

        result = BytesIO(save_virtual_workbook(xlsx))

        filename = 'relacao_bens.xlsx'
        response = HttpResponse(
            result,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response


    @action(detail=False, methods=['get'], url_path='documento-final')
    def documento_final(self, request):
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')
        periodo_uuid = self.request.query_params.get('periodo')

        if not conta_associacao_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período e o uuid da conta da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        conta_associacao = ContaAssociacao.objects.filter(uuid=conta_associacao_uuid).get()
        periodo = Periodo.objects.filter(uuid=periodo_uuid).get()

        prestacao_conta = PrestacaoConta.objects.filter(associacao=conta_associacao.associacao, periodo=periodo).first()
        relacao_bens = RelacaoBens.objects.filter(conta_associacao=conta_associacao, prestacao_conta=prestacao_conta).first()

        if not relacao_bens:
            erro = {
                'erro': 'arquivo_nao_gerado',
                'mensagem': 'Não existe um arquivo de relação de bens para download.'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        filename = 'relacao_bens.xlsx'
        response = HttpResponse(
            open(relacao_bens.arquivo.path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

    @action(detail=False, methods=['get'], url_path='relacao-bens-info')
    def relacao_bens_info(self, request):
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')
        periodo_uuid = self.request.query_params.get('periodo')
        conta_associacao = ContaAssociacao.by_uuid(conta_associacao_uuid)
        prestacao_conta = PrestacaoConta.objects.filter(associacao=conta_associacao.associacao, periodo__uuid=periodo_uuid).first()
        relacao_bens = RelacaoBens.objects.filter(conta_associacao__uuid=conta_associacao_uuid, prestacao_conta=prestacao_conta).first()

        msg = str(relacao_bens) if relacao_bens else 'Documento pendente de geração'
        return Response(msg)

    def _gerar_planilha(self, periodo, conta_associacao_uuid, previa=False):
        conta_associacao = ContaAssociacao.objects.filter(uuid=conta_associacao_uuid).get()

        xlsx = gerar(periodo, conta_associacao, previa=previa)
        return xlsx
