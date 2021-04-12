import logging
from datetime import datetime
from decimal import Decimal

from django.http import HttpResponse

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
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

logger = logging.getLogger(__name__)

from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string

from weasyprint import HTML

from django.http import HttpResponse

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template

from django.core.files.uploadedfile import SimpleUploadedFile

from weasyprint import HTML, CSS


class DemonstrativoFinanceiroViewSet(GenericViewSet):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = DemonstrativoFinanceiro.objects.all()

    dados_demonstrativo = {
        'cabecalho': {'titulo': 'Demonstrativo Financeiro - FINAL', 'periodo': '2020.2 - 2020-07-01 a 2020-12-31',
                      'conta': 'Cheque'},
        'identificacao_apm': {'nome_associacao': 'AGUA AZUL', 'cnpj_associacao': '12.749.195/0001-56',
                              'codigo_eol_associacao': '200237', 'nome_dre_associacao': 'GUAIANASES',
                              'presidente_diretoria_executiva': '', 'presidente_conselho_fiscal': ''},
        'identificacao_conta': {'banco': 'Banco do Brasil', 'agencia': '7370', 'conta': '12345-6',
                                'data_extrato': '12/04/2021', 'saldo_extrato': '0,00'},
        'resumo_por_acao': {
            'resumo_acoes': [
                {'acao_associacao': 'Rolê Cultural',
                 'linha_custeio': {
                     'saldo_anterior': '0,00',
                     'credito': '0,00',
                     'despesa_realizada': '0,00',
                     'despesa_nao_realizada': '0,00',
                     'despesa_nao_demostrada_outros_periodos': '100,00',
                     'saldo_reprogramado_proximo': '0,00',
                     'saldo_bancario': '100,00',
                     'valor_saldo_reprogramado_proximo_periodo_custeio': 0,
                     'valor_saldo_bancario_custeio': Decimal('100.00'),
                     'credito_nao_demonstrado': 0
                 },
                 'linha_capital': {
                     'saldo_anterior': '',
                     'credito': '',
                     'despesa_realizada': '',
                     'despesa_nao_realizada': '',
                     'despesa_nao_demostrada_outros_periodos': '',
                     'saldo_reprogramado_proximo': '',
                     'saldo_bancario': '',
                     'valor_saldo_reprogramado_proximo_periodo_capital': 0,
                     'valor_saldo_bancario_capital': 0, 'credito_nao_demonstrado': 0
                 },
                 'linha_livre': {
                     'saldo_anterior': '',
                     'credito': '',
                     'saldo_reprogramado_proximo': '',
                     'valor_saldo_reprogramado_proximo_periodo_livre': 0,
                     'credito_nao_demonstrado': 0
                 },
                 'saldo_bancario': '', 'total_valores': 0,
                 'total_conciliacao': Decimal('100.00')
                 },
                {'acao_associacao': ' PTRF',
                     'linha_custeio': {
                         'saldo_anterior': '',
                         'credito': '',
                         'despesa_realizada': '',
                         'despesa_nao_realizada': '',
                         'despesa_nao_demostrada_outros_periodos': '',
                         'saldo_reprogramado_proximo': '',
                         'saldo_bancario': '',
                         'valor_saldo_reprogramado_proximo_periodo_custeio': 0,
                         'valor_saldo_bancario_custeio': 0,
                         'credito_nao_demonstrado': 0},
                     'linha_capital': {
                         'saldo_anterior': '',
                         'credito': '',
                         'despesa_realizada': '',
                         'despesa_nao_realizada': '',
                         'despesa_nao_demostrada_outros_periodos': '',
                         'saldo_reprogramado_proximo': '',
                         'saldo_bancario': '',
                         'valor_saldo_reprogramado_proximo_periodo_capital': 0,
                         'valor_saldo_bancario_capital': 0,
                         'credito_nao_demonstrado': 0
                     },
                     'linha_livre': {'saldo_anterior': '',
                                     'credito': '',
                                     'saldo_reprogramado_proximo': '',
                                     'valor_saldo_reprogramado_proximo_periodo_livre': 0,
                                     'credito_nao_demonstrado': 0
                                     },
                     'saldo_bancario': '',
                     'total_valores': 0,
                     'total_conciliacao': 0
                     },
                {'acao_associacao': 'Ação ABC',
                 'linha_custeio': {
                     'saldo_anterior': '',
                     'credito': '',
                     'despesa_realizada': '',
                     'despesa_nao_realizada': '',
                     'despesa_nao_demostrada_outros_periodos': '',
                     'saldo_reprogramado_proximo': '', 'saldo_bancario': '',
                     'valor_saldo_reprogramado_proximo_periodo_custeio': 0,
                     'valor_saldo_bancario_custeio': 0, 'credito_nao_demonstrado': 0},
                 'linha_capital': {
                     'saldo_anterior': '0,00',
                     'credito': '0,00',
                     'despesa_realizada': '0,00',
                     'despesa_nao_realizada': '100,00',
                     'despesa_nao_demostrada_outros_periodos': '0,00',
                     'saldo_reprogramado_proximo': '0,00',
                     'saldo_bancario': '0,00',
                     'valor_saldo_reprogramado_proximo_periodo_capital': Decimal('-100.00'),
                     'valor_saldo_bancario_capital': 0, 'credito_nao_demonstrado': 0
                 },
                 'linha_livre': {
                     'saldo_anterior': '0,00',
                     'credito': '0,00',
                     'saldo_reprogramado_proximo': '-100,00',
                     'valor_saldo_reprogramado_proximo_periodo_livre': Decimal('-100.00'),
                     'credito_nao_demonstrado': 0}, 'saldo_bancario': '-100,00',
                 'total_valores': Decimal('-100.00'), 'total_conciliacao': Decimal('-100.00')
                 }
            ],
            'total_valores': {
                'saldo_anterior': {'C': 0, 'K': 0, 'L': 0},
                'credito': {'C': 0, 'K': 0, 'L': 0},
                'despesa_realizada': {'C': 0, 'K': 0, 'L': 0},
                'despesa_nao_realizada': {'C': Decimal('100.00'), 'K': 0, 'L': 0},
                'saldo_reprogramado_proximo': {'C': Decimal('-100.00'), 'K': 0, 'L': 0},
                'despesa_nao_demostrada_outros_periodos': {'C': Decimal('100.00'), 'K': 0, 'L': 0},
                'saldo_bancario': {'C': Decimal('100.00'), 'K': 0, 'L': 0},
                'valor_saldo_reprogramado_proximo_periodo': {'C': Decimal('-200.00'), 'K': 0, 'L': 0},
                'valor_saldo_bancario': {'C': Decimal('100.00'), 'K': 0, 'L': 0},
                'credito_nao_demonstrado': {'C': 0, 'K': 0, 'L': 0},
                'total_valores': Decimal('-100.00')
            },
            'total_conciliacao': '0,00'
        }, 'creditos_demonstrados': {'linhas': [], 'valor_total': '0,00'},
        'despesas_demonstradas': {'linhas': [], 'valor_total': '0,00'}, 'despesas_nao_demonstradas': {'linhas': [
            {'razao_social': 'Teste cpf', 'cnpj_cpf': '006.443.212-29', 'tipo_documento': 'NFe',
             'numero_documento': '111111111111111111111111111111111', 'nome_acao_documento': 'Ação ABC',
             'especificacao_material': 'Acess point', 'tipo_despesa': 'CAPITAL', 'tipo_transacao': '7677767',
             'data_documento': '28/07/2020', 'valor': '100,00'}], 'valor_total': '100,00'},
        'despesas_anteriores_nao_demonstradas': {'linhas': [
            {'razao_social': 'Fornecedor 01', 'cnpj_cpf': '51.510.540/0001-56',
             'tipo_documento': 'Guia de Recolhimento', 'numero_documento': '', 'nome_acao_documento': 'Rolê Cultural',
             'especificacao_material': 'Alfaiataria, costura e congêneres', 'tipo_despesa': 'CUSTEIO',
             'tipo_transacao': '', 'data_documento': '29/06/2020', 'valor': '100,00'}], 'valor_total': '100,00'},
        'observacoes_acoes': '',
        'data_geracao_documento': 'Documento final gerado pelo usuário usuarioteste, via SIG - Escola, em: 12/04/2021',
        'data_geracao': '12/04/2021'}

    @action(detail=False, methods=['get'], url_path='ver-pdf', permission_classes=[AllowAny])
    def ver_pdf(self, request):
        html_template = get_template('pdf/demonstrativo_financeiro/pdf.html')

        rendered_html = html_template.render(
            {'dados': self.dados_demonstrativo, 'base_static_url': staticfiles_storage.location})

        pdf_file = HTML(
            string=rendered_html,
            base_url=staticfiles_storage.location
        ).write_pdf(
            stylesheets=[CSS(staticfiles_storage.location + '/css/pdf-demo-financeiro.css')])

        # return HttpResponse(rendered_html)
        return HttpResponse(pdf_file, content_type='application/pdf')

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
                                                          data_fim=data_fim
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
        logger.info("Retornando dados do arquivo: %s", demonstrativo_financeiro.arquivo.path)

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
        logger.info("Retornando dados do arquivo: %s", demonstrativo_financeiro.arquivo.path)

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
                                                        periodo__uuid=periodo_uuid).first()

        demonstrativo_financeiro = DemonstrativoFinanceiro.objects.filter(conta_associacao__uuid=conta_associacao_uuid,
                                                                          prestacao_conta=prestacao_conta).first()

        if not demonstrativo_financeiro:
            msg = 'Documento pendente de geração'
        else:
            msg = str(demonstrativo_financeiro)

        return Response(msg)
