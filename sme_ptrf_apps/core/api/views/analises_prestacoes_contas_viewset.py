import logging

from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers.analise_prestacao_conta_serializer import AnalisePrestacaoContaRetrieveSerializer
from ..serializers.analise_documento_prestacao_conta_serializer \
    import AnaliseDocumentoPrestacaoContaSolicitacoesAgrupadasRetrieveSerializer
from ...models import AnalisePrestacaoConta, ContaAssociacao, AcaoAssociacao, TipoAcertoLancamento, TaskCelery

from sme_ptrf_apps.users.permissoes import (
    PermissaoAPITodosComLeituraOuGravacao,
)

from ...services import (
    lancamentos_da_prestacao,
    get_ajustes_extratos_bancarios
)

from django.http import HttpResponse
from sme_ptrf_apps.core.tasks import gerar_previa_relatorio_acertos_async, gerar_previa_relatorio_apos_acertos_async

from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiExample, OpenApiTypes, OpenApiResponse
)

logger = logging.getLogger(__name__)


@extend_schema_view(
    ajustes_em_extratos_bancarios=extend_schema(
        description="Retorna os ajustes encontrados para a conta da associação vinculada à análise de prestação.",
        responses={200: 'result'},
        parameters=[
            OpenApiParameter("conta_associacao", str, OpenApiParameter.QUERY,
                             description="UUID da conta da associação", required=True)
        ],
        examples=[
            OpenApiExample(
                "Exemplo de resposta",
                value={
                    "uuid": "bb3e7b79-b915-4976-b8aa-98491cda7126",
                    "prestacao_conta": "19576d1f-1678-4dbc-9bfb-a1e9c5d51301",
                    "conta_associacao": {
                        "uuid": "a5b5e686-d787-4fb3-bd2b-0369761ba937",
                        "tipo_conta": {
                            "uuid": "38c381e1-6a11-44a9-a2dd-39243799fac1",
                            "id": 1,
                            "nome": "Cheque",
                            "banco_nome": "",
                            "agencia": "",
                            "numero_conta": "",
                            "numero_cartao": "",
                            "apenas_leitura": False,
                            "permite_inativacao": True
                        },
                        "banco_nome": "001",
                        "agencia": "0687",
                        "numero_conta": "376787",
                        "solicitacao_encerramento": None,
                        "saldo_atual_conta": 576138.23,
                        "habilitar_solicitar_encerramento": False,
                        "nome": "Cheque",
                        "status": "ATIVA",
                        "periodo_encerramento_conta": None,
                        "mostrar_alerta_valores_reprogramados_ao_solicitar": False
                    },
                    "data_extrato": None,
                    "saldo_extrato": "442149.03",
                    "analise_prestacao_conta": "95d04126-b30e-4ee7-a0a9-253679d56af9",
                    "solicitar_envio_do_comprovante_do_saldo_da_conta": False,
                    "solicitar_correcao_da_data_do_saldo_da_conta": False,
                    "observacao_solicitar_envio_do_comprovante_do_saldo_da_conta": None,
                    "solicitar_correcao_de_justificativa_de_conciliacao": False
                },
                response_only=True
            )
        ]
    ),
    despesas_periodos_anteriores_com_ajustes=extend_schema(
        description="Lista as despesas de períodos anteriores ajustadas, filtradas por conta/ação.",
        responses={200: OpenApiResponse(description="Lista de despesas de períodos anteriores ajustadas")},
        parameters=[
            OpenApiParameter("conta_associacao", str, OpenApiParameter.QUERY,
                             description="UUID da conta da associação", required=True),
            OpenApiParameter("acao_associacao", str, OpenApiParameter.QUERY,
                             description="UUID da ação da associação", required=False),
            OpenApiParameter("tipo_acerto", str, OpenApiParameter.QUERY,
                             description="UUID do Tipo de Acerto do Lançamento", required=False),
            OpenApiParameter("tipo", str, OpenApiParameter.QUERY, required=False,
                             description="Tipo da transação: CREDITOS ou GASTOS", enum=['CREDITOS', 'GASTOS']),
        ]
    ),
    verifica_se_tem_ajustes_extratos=extend_schema(
        description="Verifica se existem ajustes em extratos bancários para a análise de prestação.",
        responses={200: OpenApiResponse(description="Resultado da verificação")}
    ),
    documentos_com_ajustes=extend_schema(
        description="Retorna os documentos que possuem ajustes vinculados à análise.",
        responses={200: AnaliseDocumentoPrestacaoContaSolicitacoesAgrupadasRetrieveSerializer(many=True)}
    ),
    lancamentos_com_ajustes=extend_schema(
        description="Retorna os lançamentos vinculados à análise da prestação, com filtros opcionais.",
        responses={200: OpenApiResponse(description="Lista de lançamentos com ajustes")},
        parameters=[
            OpenApiParameter("conta_associacao", str, OpenApiParameter.QUERY,
                             description="UUID da conta da associação", required=True),
            OpenApiParameter("acao_associacao", str, OpenApiParameter.QUERY,
                             description="UUID da ação da associação", required=False),
            OpenApiParameter("tipo", str, OpenApiParameter.QUERY, required=False,
                             description="Tipo da transação: CREDITOS ou GASTOS", enum=['CREDITOS', 'GASTOS']),
            OpenApiParameter("tipo_acerto", str, OpenApiParameter.QUERY,
                             description="UUID do Tipo de Acerto do Lançamento", required=False),
        ]
    ),
    download_documento_pdf=extend_schema(
        description="Realiza o download do arquivo PDF da análise.",
        responses={(200, 'application/pdf'): OpenApiTypes.BINARY},
        parameters=[
            OpenApiParameter("analise_prestacao_uuid", str, OpenApiParameter.QUERY,
                             description="UUID da análise da prestação de contas", required=True),
        ]
    ),
    previa=extend_schema(
        description="Gera uma prévia do relatório de acertos e envia para processamento em background.",
        responses={200: 'Arquivo na fila para processamento.'},
        parameters=[
            OpenApiParameter("analise_prestacao_uuid", str, OpenApiParameter.QUERY,
                             description="UUID da análise da prestação de contas", required=True),
        ],
        examples=[
            OpenApiExample(
                'Resposta',
                value={'mensagem': 'Arquivo na fila para processamento.'}
            )
        ],
    ),
    status_info=extend_schema(
        description="Retorna o status atual da análise da prestação de contas.",
        responses={200: OpenApiResponse(description="Status da análise")},
        parameters=[
            OpenApiParameter("analise_prestacao_uuid", str, OpenApiParameter.QUERY,
                             description="UUID da análise da prestação de contas", required=True),
        ]
    ),
    previa_relatorio_apos_acertos=extend_schema(
        description="Gera uma prévia do relatório após acertos e envia para processamento.",
        responses={200: 'Arquivo na fila para processamento.'},
        parameters=[
            OpenApiParameter("analise_prestacao_uuid", str, OpenApiParameter.QUERY,
                             description="UUID da análise da prestação de contas", required=True),
        ],
        examples=[
            OpenApiExample(
                'Resposta',
                value={'mensagem': 'Arquivo na fila para processamento.'}
            )
        ],
    ),
    status_info_relatorio_apos_acertos=extend_schema(
        description="Consulta o status do relatório após os acertos.",
        responses={200: OpenApiResponse(description="Status do relatório após acertos")},
        parameters=[
            OpenApiParameter("analise_prestacao_uuid", str, OpenApiParameter.QUERY,
                             description="UUID da análise da prestação de contas", required=True),
        ]
    ),
    download_documento_pdf_apos_acertos=extend_schema(
        description="Permite o download do PDF do relatório gerado após os acertos.",
        responses={(200, 'application/pdf'): OpenApiTypes.BINARY},
        parameters=[
            OpenApiParameter("analise_prestacao_uuid", str, OpenApiParameter.QUERY,
                             description="UUID da análise da prestação de contas", required=True),
        ]
    ),
    regerar_relatorio_apos_acertos=extend_schema(
        description="Regerar relatório após acertos e envia para a fila de processamento.",
        responses={200: 'Arquivo na fila para processamento.'},
        parameters=[
            OpenApiParameter("analise_prestacao_uuid", str, OpenApiParameter.QUERY,
                             description="UUID da análise da prestação de contas", required=True),
        ],
        examples=[
            OpenApiExample(
                'Resposta',
                value={'mensagem': 'Arquivo na fila para processamento.'}
            )
        ],
    ),
    regerar_previa_relatorio_apos_acertos=extend_schema(
        description="Regerar da prévia do relatório após acertos e envia para a fila de processamento.",
        responses={200: OpenApiResponse(description="Mensagem de confirmação de envio para processamento")},
        parameters=[
            OpenApiParameter("analise_prestacao_uuid", str, OpenApiParameter.QUERY,
                             description="UUID da análise da prestação de contas", required=True),
        ],
        examples=[
            OpenApiExample(
                'Resposta',
                value={'mensagem': 'Arquivo na fila para processamento.'}
            )
        ],
    ),
)
class AnalisesPrestacoesContasViewSet(
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = AnalisePrestacaoConta.objects.all().order_by('id')
    serializer_class = AnalisePrestacaoContaRetrieveSerializer

    @action(detail=True, methods=['get'], url_path='ajustes-extratos-bancarios',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def ajustes_em_extratos_bancarios(self, request, uuid):
        try:
            analise_prestacao = AnalisePrestacaoConta.by_uuid(uuid)
        except AnalisePrestacaoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise-prestacao para o uuid {uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Define a conta
        conta_associacao_uuid = self.request.query_params.get('conta_associacao')
        if not conta_associacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da conta da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            conta_associacao = ContaAssociacao.objects.get(uuid=conta_associacao_uuid)
        except ContaAssociacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto conta-associação para o uuid {conta_associacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = get_ajustes_extratos_bancarios(analise_prestacao, conta_associacao)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='verifica-ajustes-extratos',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def verifica_se_tem_ajustes_extratos(self, request, uuid):
        try:
            analise_prestacao = AnalisePrestacaoConta.by_uuid(uuid)
        except AnalisePrestacaoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise-prestacao para o uuid {uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = get_ajustes_extratos_bancarios(analise_prestacao)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='lancamentos-com-ajustes',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def lancamentos_com_ajustes(self, request, uuid):
        analise_prestacao = AnalisePrestacaoConta.by_uuid(uuid)

        # Define a conta de conciliação
        conta_associacao_uuid = self.request.query_params.get('conta_associacao')
        if not conta_associacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da conta da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            conta_associacao = ContaAssociacao.objects.get(uuid=conta_associacao_uuid)
        except ContaAssociacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto conta-associação para o uuid {conta_associacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Define a ação para o filtro de transações
        acao_associacao = None
        acao_associacao_uuid = request.query_params.get('acao_associacao')
        if acao_associacao_uuid:
            try:
                acao_associacao = AcaoAssociacao.objects.get(uuid=acao_associacao_uuid)
            except AcaoAssociacao.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto ação-associação para o uuid {acao_associacao_uuid} não foi encontrado."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Define o tipo de transação para o filtro das transações
        tipo_transacao = request.query_params.get('tipo')
        if tipo_transacao and tipo_transacao not in ('CREDITOS', 'GASTOS'):
            erro = {
                'erro': 'parametro_inválido',
                'mensagem': 'O parâmetro tipo pode receber como valor "CREDITOS" ou "GASTOS". O parâmetro é opcional.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Define o tipo de acerto para o filtro de transações
        tipo_acerto = None
        tipo_acerto_uuid = request.query_params.get('tipo_acerto')
        if tipo_acerto_uuid:
            try:
                tipo_acerto = TipoAcertoLancamento.objects.get(uuid=tipo_acerto_uuid)
            except TipoAcertoLancamento.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto TipoAcertoLancamento para o uuid {tipo_acerto_uuid} não foi encontrado."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        lancamentos = lancamentos_da_prestacao(
            analise_prestacao_conta=analise_prestacao,
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            tipo_transacao=tipo_transacao,
            tipo_acerto=tipo_acerto,
            com_ajustes=True,
            inclui_inativas=True,
        )
        return Response(lancamentos, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='despesas-periodos-anteriores-com-ajustes',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def despesas_periodos_anteriores_com_ajustes(self, request, uuid):
        analise_prestacao = AnalisePrestacaoConta.by_uuid(uuid)

        # Define a conta de conciliação
        conta_associacao_uuid = self.request.query_params.get('conta_associacao')
        if not conta_associacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da conta da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            conta_associacao = ContaAssociacao.objects.get(uuid=conta_associacao_uuid)
        except ContaAssociacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto conta-associação para o uuid {conta_associacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Define a ação para o filtro de transações
        acao_associacao = None
        acao_associacao_uuid = request.query_params.get('acao_associacao')
        if acao_associacao_uuid:
            try:
                acao_associacao = AcaoAssociacao.objects.get(uuid=acao_associacao_uuid)
            except AcaoAssociacao.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto ação-associação para o uuid {acao_associacao_uuid} não foi encontrado."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Define o tipo de transação para o filtro das transações
        tipo_transacao = request.query_params.get('tipo')
        if tipo_transacao and tipo_transacao not in ('CREDITOS', 'GASTOS'):
            erro = {
                'erro': 'parametro_inválido',
                'mensagem': 'O parâmetro tipo pode receber como valor "CREDITOS" ou "GASTOS". O parâmetro é opcional.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Define o tipo de acerto para o filtro de transações
        tipo_acerto = None
        tipo_acerto_uuid = request.query_params.get('tipo_acerto')
        if tipo_acerto_uuid:
            try:
                tipo_acerto = TipoAcertoLancamento.objects.get(uuid=tipo_acerto_uuid)
            except TipoAcertoLancamento.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto TipoAcertoLancamento para o uuid {tipo_acerto_uuid} não foi encontrado."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        lancamentos = lancamentos_da_prestacao(
            analise_prestacao_conta=analise_prestacao,
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            tipo_acerto=tipo_acerto,
            com_ajustes=True,
            inclui_inativas=True,
            tipo_transacao="GASTOS",
            apenas_despesas_de_periodos_anteriores=True,
        )
        return Response(lancamentos, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='documentos-com-ajuste',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def documentos_com_ajustes(self, request, uuid):
        analise_prestacao = AnalisePrestacaoConta.by_uuid(uuid)
        documentos = analise_prestacao.analises_de_documento.filter(
            resultado='AJUSTE').all().order_by('tipo_documento_prestacao_conta__nome')
        return Response(AnaliseDocumentoPrestacaoContaSolicitacoesAgrupadasRetrieveSerializer(
            documentos, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def previa(self, request):
        # Define a análise da prestação de contas
        analise_prestacao_uuid = self.request.query_params.get('analise_prestacao_uuid')

        if analise_prestacao_uuid:
            try:
                AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
            except AnalisePrestacaoConta.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': (
                        f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não "
                        "foi encontrado na base.")
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                erro = {
                    'erro': 'Ocorreu um erro!',
                    'mensagem': f"{e}"
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
        else:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da analise.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        gerar_previa_relatorio_acertos_async.delay(
            analise_prestacao_uuid=analise_prestacao_uuid,
            usuario=request.user.username
        )

        return Response({'mensagem': 'Arquivo na fila para processamento.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='status-info',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def status_info(self, request):
        analise_prestacao_uuid = request.query_params.get('analise_prestacao_uuid')

        if analise_prestacao_uuid:
            try:
                analise_prestacao = AnalisePrestacaoConta.by_uuid(analise_prestacao_uuid)
            except AnalisePrestacaoConta.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': (
                        f"O objeto AnalisePrestacaoConta para o uuid {analise_prestacao_uuid} não foi encontrado.")
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                erro = {
                    'erro': 'Ocorreu um erro!',
                    'mensagem': f"{e}"
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
        else:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da analise.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        return Response(analise_prestacao.get_status())

    @action(detail=False, methods=['get'], url_path='download-documento-pdf',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def download_documento_pdf(self, request):
        logger.info("Download do documento pdf.")

        analise_prestacao_uuid = request.query_params.get('analise_prestacao_uuid')

        if analise_prestacao_uuid:
            try:
                analise_prestacao = AnalisePrestacaoConta.by_uuid(analise_prestacao_uuid)
            except AnalisePrestacaoConta.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': (
                        f"O objeto AnalisePrestacaoConta para o uuid {analise_prestacao_uuid} não foi encontrado.")
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                erro = {
                    'erro': 'Ocorreu um erro!',
                    'mensagem': f"{e}"
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
        else:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da analise.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            filename = 'relatorio_acertos.pdf'
            response = HttpResponse(
                open(analise_prestacao.arquivo_pdf.path, 'rb'),
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

    @action(detail=False, methods=['get'], url_path='previa-relatorio-apos-acertos',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def previa_relatorio_apos_acertos(self, request):
        # Define a análise da prestação de contas
        analise_prestacao_uuid = self.request.query_params.get('analise_prestacao_uuid')

        if analise_prestacao_uuid:
            try:
                AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
            except AnalisePrestacaoConta.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': (
                        f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não "
                        "foi encontrado na base.")
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                erro = {
                    'erro': 'Ocorreu um erro!',
                    'mensagem': f"{e}"
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
        else:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da analise.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        gerar_previa_relatorio_apos_acertos_async.delay(
            analise_prestacao_uuid=analise_prestacao_uuid,
            usuario=request.user.username
        )

        return Response({'mensagem': 'Arquivo na fila para processamento.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='status-info_relatorio_apos_acertos',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def status_info_relatorio_apos_acertos(self, request):
        analise_prestacao_uuid = request.query_params.get('analise_prestacao_uuid')

        if analise_prestacao_uuid:
            try:
                analise_prestacao = AnalisePrestacaoConta.by_uuid(analise_prestacao_uuid)
            except AnalisePrestacaoConta.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': (
                        f"O objeto AnalisePrestacaoConta para o uuid {analise_prestacao_uuid} não foi encontrado.")
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                erro = {
                    'erro': 'Ocorreu um erro!',
                    'mensagem': f"{e}"
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
        else:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da analise.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        return Response(analise_prestacao.get_status_relatorio_apos_acertos())

    @action(detail=False, methods=['get'], url_path='download-documento-pdf_apos_acertos',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def download_documento_pdf_apos_acertos(self, request):
        logger.info("Download do documento pdf após acertos.")

        analise_prestacao_uuid = request.query_params.get('analise_prestacao_uuid')

        if analise_prestacao_uuid:
            try:
                analise_prestacao = AnalisePrestacaoConta.by_uuid(analise_prestacao_uuid)
            except AnalisePrestacaoConta.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': (
                        f"O objeto AnalisePrestacaoConta para o uuid {analise_prestacao_uuid} não foi encontrado.")
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                erro = {
                    'erro': 'Ocorreu um erro!',
                    'mensagem': f"{e}"
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
        else:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da analise.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            filename = 'relatorio_apos_acertos.pdf'
            response = HttpResponse(
                open(analise_prestacao.arquivo_pdf_apresentacao_apos_acertos.path, 'rb'),
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

    @action(detail=False, methods=['get'], url_path='regerar-relatorio-apos-acertos',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def regerar_relatorio_apos_acertos(self, request):
        from sme_ptrf_apps.core.tasks import (
            gerar_relatorio_apos_acertos_v2_async,
        )

        # Define a análise da prestação de contas
        analise_prestacao_uuid = self.request.query_params.get('analise_prestacao_uuid')

        if analise_prestacao_uuid:
            try:
                analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
            except AnalisePrestacaoConta.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': (
                        f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não "
                        "foi encontrado na base.")
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                erro = {
                    'erro': 'Ocorreu um erro!',
                    'mensagem': f"{e}"
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
        else:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da analise.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        task_celery_geracao_relatorio_apos_acerto = TaskCelery.objects.create(
            nome_task="regerar_relatorio_apos_acertos_v2_async",
            associacao=analise_prestacao.prestacao_conta.associacao,
            periodo=analise_prestacao.prestacao_conta.periodo,
            usuario=request.user
        )

        gerar_relatorio_apos_acertos_v2_async.apply_async(
            (
                task_celery_geracao_relatorio_apos_acerto.uuid,
                analise_prestacao.prestacao_conta.associacao.uuid,
                analise_prestacao.prestacao_conta.periodo.uuid,
                request.user.username,
                analise_prestacao.uuid
            ), countdown=1
        )

        return Response({'mensagem': 'Arquivo na fila para processamento.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='regerar-previa-relatorio-apos-acertos',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def regerar_previa_relatorio_apos_acertos(self, request):
        from sme_ptrf_apps.core.tasks import (
            gerar_previa_relatorio_apos_acertos_v2_async,
        )

        # Define a análise da prestação de contas
        analise_prestacao_uuid = self.request.query_params.get('analise_prestacao_uuid')

        if analise_prestacao_uuid:
            try:
                analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
            except AnalisePrestacaoConta.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': (
                        f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não "
                        "foi encontrado na base.")
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                erro = {
                    'erro': 'Ocorreu um erro!',
                    'mensagem': f"{e}"
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
        else:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da analise.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        task_celery_geracao_relatorio_apos_acerto = TaskCelery.objects.create(
            nome_task="regerar_previa_relatorio_apos_acertos_v2_async",
            associacao=analise_prestacao.prestacao_conta.associacao,
            periodo=analise_prestacao.prestacao_conta.periodo,
            usuario=request.user
        )

        gerar_previa_relatorio_apos_acertos_v2_async.apply_async(
            (
                task_celery_geracao_relatorio_apos_acerto.uuid,
                analise_prestacao.prestacao_conta.associacao.uuid,
                analise_prestacao.prestacao_conta.periodo.uuid,
                request.user.username,
                analise_prestacao.uuid
            ), countdown=1
        )

        return Response({'mensagem': 'Arquivo na fila para processamento.'}, status=status.HTTP_200_OK)
