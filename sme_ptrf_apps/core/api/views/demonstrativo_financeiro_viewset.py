import logging
from datetime import datetime
from io import BytesIO

from django.http import HttpResponse
from openpyxl.writer.excel import save_virtual_workbook
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao,
    PermissaoAPITodosComGravacao
)

from sme_ptrf_apps.core.models import (
    ContaAssociacao,
    DemonstrativoFinanceiro,
    Periodo,
    PeriodoPrevia,
    PrestacaoConta,
)

from sme_ptrf_apps.core.services.demonstrativo_financeiro import gerar
from sme_ptrf_apps.core.services.info_por_acao_services import info_acoes_associacao_no_periodo

logger = logging.getLogger(__name__)


class DemonstrativoFinanceiroViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = DemonstrativoFinanceiro.objects.all()

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def previa(self, request):
        logger.info("Previa do demonstrativo financeiro")
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')

        periodo_uuid = self.request.query_params.get('periodo')

        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')

        if not conta_associacao_uuid or not periodo_uuid or (not data_inicio or not data_fim):
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da conta da associação o periodo_uuid e as datas de inicio e fim do período.'
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
        xlsx = self._gerar_planilha(conta_associacao_uuid, periodoPrevia, previa=True)

        result = BytesIO(save_virtual_workbook(xlsx))

        filename = 'demonstrativo_financeiro.xlsx'
        response = HttpResponse(
            result,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        logger.info("Previa Pronta. Retornando conteúdo para o frontend")
        return response

    @action(detail=False, methods=['get'], url_path='documento-final',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def documento_final(self, request):
        logger.info("Download do documento Final.")
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')
        periodo_uuid = self.request.query_params.get('periodo')

        if not conta_associacao_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período e o uuid da conta da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        logger.info("Consultando dados da conta_associacao: %s e do periodo %s.", conta_associacao_uuid, periodo_uuid)
        try:
            conta_associacao = ContaAssociacao.objects.filter(uuid=conta_associacao_uuid).get()
            periodo = Periodo.objects.filter(uuid=periodo_uuid).get()
        except Exception as err:
            erro = {
                'erro': 'arquivo_nao_gerado',
                'mensagem': str(err)
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        prestacao_conta = PrestacaoConta.objects.filter(associacao=conta_associacao.associacao, periodo=periodo).first()
        demonstrativo_financeiro = DemonstrativoFinanceiro.objects.filter(conta_associacao=conta_associacao,
                                                                          prestacao_conta=prestacao_conta).first()

        logger.info("Prestacao de conta: %s, Demonstrativo Financeiro: %s", str(prestacao_conta), str(demonstrativo_financeiro))
        filename = 'demonstrativo_financeiro.xlsx'
        if not demonstrativo_financeiro:
            erro = {
                'erro': 'arquivo_nao_gerado',
                'mensagem': 'Não existe um arquivo de demostrativo financeiro para download.'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)
        logger.info("Retornando dados do arquivo: %s", demonstrativo_financeiro.arquivo.path)

        try:
            response = HttpResponse(
                open(demonstrativo_financeiro.arquivo.path, 'rb'),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
        except Exception as err:
            erro = {
                'erro': 'arquivo_nao_gerado',
                'mensagem': str(err)
            }
            logger.info("Erro: %s", str(err))
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        return response

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def acoes(self, request):
        periodo = None

        associacao_uuid = request.query_params.get('associacao_uuid')
        periodo_uuid = request.query_params.get('periodo_uuid')
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')

        if not conta_associacao_uuid or not associacao_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período, uuid da associação e o uuid da conta da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if periodo_uuid:
            periodo = Periodo.by_uuid(periodo_uuid)

        if not periodo:
            periodo = Periodo.periodo_atual()

        conta_associacao = ContaAssociacao.by_uuid(conta_associacao_uuid)

        info_acoes = info_acoes_associacao_no_periodo(associacao_uuid=associacao_uuid, periodo=periodo, conta=conta_associacao)
        result = {
            'info_acoes': [info for info in info_acoes if
                           info['saldo_reprogramado'] or info['receitas_no_periodo'] or info['despesas_no_periodo']]
        }

        return Response(result)

    @action(detail=False, methods=['get'], url_path='__demonstrativo-info',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def __demonstrativo_info(self, request):
        acao_associacao_uuid = self.request.query_params.get('acao-associacao')
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')
        periodo_uuid = self.request.query_params.get('periodo')

        if not acao_associacao_uuid or not conta_associacao_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período, o uuid da ação da associação e o uuid da conta da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        conta_associacao = ContaAssociacao.by_uuid(conta_associacao_uuid)
        prestacao_conta = PrestacaoConta.objects.filter(associacao=conta_associacao.associacao,
                                                        periodo__uuid=periodo_uuid).first()

        demonstrativo_financeiro = DemonstrativoFinanceiro.objects.filter(acao_associacao__uuid=acao_associacao_uuid,
                                                                          conta_associacao__uuid=conta_associacao_uuid,
                                                                          prestacao_conta=prestacao_conta).last()
        msg = str(demonstrativo_financeiro) if demonstrativo_financeiro else 'Documento pendente de geração'

        return Response(msg)

    @action(detail=False, methods=['get'], url_path='demonstrativo-info',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def demonstrativo_info(self, request):
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')
        periodo_uuid = self.request.query_params.get('periodo')
        conta_associacao = ContaAssociacao.by_uuid(conta_associacao_uuid)
        prestacao_conta = PrestacaoConta.objects.filter(associacao=conta_associacao.associacao, periodo__uuid=periodo_uuid).first()

        demonstrativo_financeiro = DemonstrativoFinanceiro.objects.filter(conta_associacao__uuid=conta_associacao_uuid, prestacao_conta=prestacao_conta).first()

        msg = ""
        if not demonstrativo_financeiro:
            msg = 'Documento pendente de geração'
        else:
            msg = str(demonstrativo_financeiro)

        return Response(msg)

    def _gerar_planilha(self, conta_associacao_uuid, periodo, previa=False):
        conta_associacao = ContaAssociacao.objects.filter(uuid=conta_associacao_uuid).get()
        acoes = conta_associacao.associacao.acoes.filter(status='ATIVA')

        xlsx = gerar("", acoes, periodo, conta_associacao, previa=previa)
        return xlsx
