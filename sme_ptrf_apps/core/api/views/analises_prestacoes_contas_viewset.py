import logging

from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers.analise_prestacao_conta_serializer import AnalisePrestacaoContaRetrieveSerializer
from ..serializers.analise_documento_prestacao_conta_serializer import AnaliseDocumentoPrestacaoContaRetrieveSerializer
from ...models import AnalisePrestacaoConta, ContaAssociacao, AcaoAssociacao, TipoAcertoLancamento

from sme_ptrf_apps.users.permissoes import (
    PermissaoAPITodosComLeituraOuGravacao,
)

from ...services import (
    lancamentos_da_prestacao,
    get_ajustes_extratos_bancarios
)

from django.http import HttpResponse
from sme_ptrf_apps.core.tasks import gerar_previa_relatorio_acertos_async

logger = logging.getLogger(__name__)


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
            com_ajustes=True
        )

        return Response(lancamentos, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='documentos-com-ajuste',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def documentos_com_ajustes(self, request, uuid):
        analise_prestacao = AnalisePrestacaoConta.by_uuid(uuid)
        documentos = analise_prestacao.analises_de_documento.filter(resultado='AJUSTE').all().order_by('tipo_documento_prestacao_conta__nome')
        return Response(AnaliseDocumentoPrestacaoContaRetrieveSerializer(documentos, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def previa(self, request):
        # Define a análise da prestação de contas
        analise_prestacao_uuid = self.request.query_params.get('analise_prestacao_uuid')

        if analise_prestacao_uuid:
            try:
                analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
            except AnalisePrestacaoConta.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não foi encontrado na base."
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
                    'mensagem': f"O objeto AnalisePrestacaoConta para o uuid {analise_prestacao_uuid} não foi encontrado."
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
                    'mensagem': f"O objeto AnalisePrestacaoConta para o uuid {analise_prestacao_uuid} não foi encontrado."
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
