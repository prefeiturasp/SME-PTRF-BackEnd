import logging
from datetime import datetime

from django.http import HttpResponse

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.models import ContaAssociacao, Periodo, PrestacaoConta, RelacaoBens

from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao,
    PermissaoAPITodosComGravacao
)

from sme_ptrf_apps.core.tasks import gerar_previa_relacao_de_bens_async

logger = logging.getLogger(__name__)


class RelacaoBensViewSet(GenericViewSet):
    lookup_field = 'uuid'

    permission_classes = [IsAuthenticated & PermissaoApiUe]
    queryset = RelacaoBens.objects.all()

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def previa(self, request):
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')
        periodo_uuid = self.request.query_params.get('periodo')

        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')

        if not conta_associacao_uuid or not periodo_uuid or (not data_inicio or not data_fim):
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período o uuid da conta da associação e as datas de inicio '
                            'e fim do período.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if datetime.strptime(data_fim, "%Y-%m-%d") < datetime.strptime(data_inicio, "%Y-%m-%d"):
            erro = {
                'erro': 'erro_nas_datas',
                'mensagem': 'Data fim não pode ser menor que a data inicio.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        periodo = Periodo.objects.filter(uuid=periodo_uuid).get()

        if periodo.data_fim_realizacao_despesas and datetime.strptime(data_fim,
                                                                      "%Y-%m-%d").date() > periodo.data_fim_realizacao_despesas:
            erro = {
                'erro': 'erro_nas_datas',
                'mensagem': 'Data fim não pode ser maior que a data fim da realização as despesas do periodo.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        gerar_previa_relacao_de_bens_async.delay(periodo_uuid=periodo_uuid,
                                                 conta_associacao_uuid=conta_associacao_uuid,
                                                 data_inicio=data_inicio,
                                                 data_fim=data_fim,
                                                 usuario=request.user.username,
                                                 )

        return Response({'mensagem': 'Arquivo na fila para processamento.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='documento-final',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def documento_final(self, request):
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

        conta_associacao = ContaAssociacao.objects.filter(uuid=conta_associacao_uuid).get()
        periodo = Periodo.objects.filter(uuid=periodo_uuid).get()

        prestacao_conta = PrestacaoConta.objects.filter(associacao=conta_associacao.associacao, periodo=periodo).first()
        relacao_bens = RelacaoBens.objects.filter(conta_associacao=conta_associacao,
                                                  prestacao_conta=prestacao_conta).first()

        if not relacao_bens:
            erro = {
                'erro': 'arquivo_nao_gerado',
                'mensagem': 'Não existe um arquivo de relação de bens para download.'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        try:
            if formato_arquivo == 'PDF':
                filename = 'relacao_bens.pdf'
                response = HttpResponse(
                    open(relacao_bens.arquivo_pdf.path, 'rb'),
                    content_type='application/pdf'
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
            else:
                filename = 'relacao_bens.xlsx'
                response = HttpResponse(
                    open(relacao_bens.arquivo.path, 'rb'),
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

        conta_associacao = ContaAssociacao.objects.filter(uuid=conta_associacao_uuid).get()
        periodo = Periodo.objects.filter(uuid=periodo_uuid).get()

        relacao_bens = RelacaoBens.objects.filter(
            conta_associacao=conta_associacao,
            periodo_previa=periodo,
            versao=RelacaoBens.VERSAO_PREVIA
        ).first()

        try:
            if formato_arquivo == 'PDF':
                filename = 'relacao_de_bens.pdf'
                response = HttpResponse(
                    open(relacao_bens.arquivo_pdf.path, 'rb'),
                    content_type='application/pdf'
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
            else:
                filename = 'relacao_bens.xlsx'
                response = HttpResponse(
                    open(relacao_bens.arquivo.path, 'rb'),
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

    @action(detail=False, methods=['get'], url_path='relacao-bens-info',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def relacao_bens_info(self, request):
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')
        periodo_uuid = self.request.query_params.get('periodo')
        periodo = Periodo.by_uuid(periodo_uuid)
        conta_associacao = ContaAssociacao.by_uuid(conta_associacao_uuid)
        prestacao_conta = PrestacaoConta.objects.filter(associacao=conta_associacao.associacao,
                                                        periodo__uuid=periodo_uuid).first()
        relacao_bens = RelacaoBens.objects.filter(conta_associacao__uuid=conta_associacao_uuid,
                                                  prestacao_conta=prestacao_conta).first()

        msg = ""
        if not relacao_bens:
            rateios = RateioDespesa.rateios_da_conta_associacao_no_periodo(
                conta_associacao=conta_associacao, periodo=periodo, aplicacao_recurso=APLICACAO_CAPITAL)
            if rateios:
                msg = 'Documento pendente de geração'
            else:
                msg = "Não houve bem adquirido ou produzido no referido período."
        else:
            msg = str(relacao_bens)

        return Response(msg)

    @action(detail=True, methods=['get'], url_path='pdf', permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def pdf(self, request, uuid):
        """/api/relacao-bens/{uuid}/pdf"""
        relacao_bens = RelacaoBens.by_uuid(uuid)

        if not relacao_bens:
            erro = {
                'erro': 'arquivo_nao_gerado',
                'mensagem': 'Não existe um arquivo de relação de bens para download.'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        try:
            filename = 'relacao_bens.pdf'
            response = HttpResponse(
                open(relacao_bens.arquivo_pdf.path, 'rb'),
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

