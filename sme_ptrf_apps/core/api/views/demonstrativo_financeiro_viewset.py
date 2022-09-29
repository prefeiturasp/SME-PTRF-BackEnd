import logging
from datetime import datetime

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
    PrestacaoConta,
)

from sme_ptrf_apps.core.tasks import gerar_previa_demonstrativo_financeiro_async

from sme_ptrf_apps.core.services.info_por_acao_services import info_acoes_associacao_no_periodo

from django.http import HttpResponse

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
                'mensagem': 'É necessário enviar o uuid da conta da associação o periodo_uuid e as datas de inicio e '
                            'fim do período.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if datetime.strptime(data_fim, "%Y-%m-%d") < datetime.strptime(data_inicio, "%Y-%m-%d"):
            erro = {
                'erro': 'erro_nas_datas',
                'mensagem': 'Data fim não pode ser menor que a data inicio.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        periodo = Periodo.objects.filter(uuid=periodo_uuid).get()

        if (
            periodo.data_fim_realizacao_despesas and
            datetime.strptime(data_fim, "%Y-%m-%d").date() > periodo.data_fim_realizacao_despesas
        ):
            erro = {
                'erro': 'erro_nas_datas',
                'mensagem': 'Data fim não pode ser maior que a data fim da realização as despesas do periodo.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        gerar_previa_demonstrativo_financeiro_async.delay(periodo_uuid=periodo_uuid,
                                                          conta_associacao_uuid=conta_associacao_uuid,
                                                          data_inicio=data_inicio,
                                                          data_fim=data_fim,
                                                          usuario=request.user.username,
                                                          )

        return Response({'mensagem': 'Arquivo na fila para processamento.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='documento-final',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def documento_final(self, request):
        logger.info("Download do documento Final.")
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')
        periodo_uuid = self.request.query_params.get('periodo')
        formato_arquivo = self.request.query_params.get('formato_arquivo')

        if formato_arquivo and formato_arquivo not in ['XLSX', 'PDF']:
            erro = {
                'erro': 'parametro_inválido',
                'mensagem': 'O parâmetro formato_arquivo espera os valores XLSX ou PDF.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if not formato_arquivo:
            formato_arquivo = 'XLSX'

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

        logger.info("Prestacao de conta: %s, Demonstrativo Financeiro: %s", str(prestacao_conta),
                    str(demonstrativo_financeiro))

        if not demonstrativo_financeiro:
            erro = {
                'erro': 'arquivo_nao_gerado',
                'mensagem': 'Não existe um arquivo de demostrativo financeiro para download.'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        logger.info("Retornando dados do arquivo: %s", demonstrativo_financeiro.arquivo_pdf.path)

        try:
            if formato_arquivo == 'PDF':
                filename = 'demonstrativo_financeiro.pdf'
                response = HttpResponse(
                    open(demonstrativo_financeiro.arquivo_pdf.path, 'rb'),
                    content_type='application/pdf'
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
            else:
                filename = 'demonstrativo_financeiro.xlsx'
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

    @action(detail=False, methods=['get'], url_path='documento-previa',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def documento_previa(self, request):
        logger.info("Download do documento Prévia.")
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')
        periodo_uuid = self.request.query_params.get('periodo')
        formato_arquivo = self.request.query_params.get('formato_arquivo')

        if formato_arquivo and formato_arquivo not in ['XLSX', 'PDF']:
            erro = {
                'erro': 'parametro_inválido',
                'mensagem': 'O parâmetro formato_arquivo espera os valores XLSX ou PDF.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if not formato_arquivo:
            formato_arquivo = 'PDF'

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

        demonstrativo_financeiro = DemonstrativoFinanceiro.objects.filter(conta_associacao=conta_associacao,
                                                                          periodo_previa=periodo,
                                                                          versao=DemonstrativoFinanceiro.VERSAO_PREVIA
                                                                          ).first()

        logger.info("Demonstrativo Financeiro: %s", str(demonstrativo_financeiro))

        if not demonstrativo_financeiro:
            erro = {
                'erro': 'arquivo_nao_gerado',
                'mensagem': 'Não existe um arquivo de prévia de demostrativo financeiro para download.'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        logger.info("Retornando dados do arquivo: %s", demonstrativo_financeiro.arquivo_pdf.path)

        try:
            if formato_arquivo == 'PDF':
                filename = 'demonstrativo_financeiro.pdf'
                response = HttpResponse(
                    open(demonstrativo_financeiro.arquivo_pdf.path, 'rb'),
                    content_type='application/pdf'
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
            else:
                filename = 'demonstrativo_financeiro.xlsx'
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

        info_acoes = info_acoes_associacao_no_periodo(associacao_uuid=associacao_uuid, periodo=periodo,
                                                      conta=conta_associacao)
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
        prestacao_conta = PrestacaoConta.objects.filter(associacao=conta_associacao.associacao,
                                                        periodo__uuid=periodo_uuid
                                                        ).first()

        demonstrativo_financeiro = DemonstrativoFinanceiro.objects.filter(conta_associacao__uuid=conta_associacao_uuid,
                                                                          prestacao_conta=prestacao_conta).first()

        if not demonstrativo_financeiro:
            msg = 'Documento pendente de geração'
        else:
            msg = str(demonstrativo_financeiro)

        return Response(msg)

    @action(detail=True, methods=['get'], url_path='pdf',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def pdf(self, request, uuid):
        """/api/demonstrativo-financeiro/{uuid}/pdf"""
        logger.info("Download do documento Final.")

        demonstrativo_financeiro = DemonstrativoFinanceiro.by_uuid(uuid)

        logger.info("Demonstrativo Financeiro: %s", str(demonstrativo_financeiro))

        try:

            filename = 'demonstrativo_financeiro.pdf'
            response = HttpResponse(
                open(demonstrativo_financeiro.arquivo_pdf.path, 'rb'),
                content_type='application/pdf'
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
