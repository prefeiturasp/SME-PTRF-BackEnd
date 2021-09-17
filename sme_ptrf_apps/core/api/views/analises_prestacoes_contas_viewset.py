import logging

from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers.analise_prestacao_conta_serializer import AnalisePrestacaoContaRetrieveSerializer
from ..serializers.analise_documento_prestacao_conta_serializer import AnaliseDocumentoPrestacaoContaRetrieveSerializer
from ...models import AnalisePrestacaoConta, ContaAssociacao, AcaoAssociacao

from sme_ptrf_apps.users.permissoes import (
    PermissaoAPITodosComLeituraOuGravacao,
)

from ...services import (
    lancamentos_da_prestacao,
)

logger = logging.getLogger(__name__)


class AnalisesPrestacoesContasViewSet(
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = AnalisePrestacaoConta.objects.all().order_by('id')
    serializer_class = AnalisePrestacaoContaRetrieveSerializer

    @action(detail=True, methods=['get'],
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

        lancamentos = analise_prestacao.analises_de_lancamentos.filter(
            resultado='AJUSTE',
            conta_associacao=conta_associacao
        )

        if acao_associacao:
            lancamentos = lancamentos.filter(acao_associacao=acao_associacao)

        lancamentos = lancamentos_da_prestacao(
            analise_prestacao_conta=analise_prestacao,
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            tipo_transacao=tipo_transacao
        )

        return Response(lancamentos, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='documentos-com-ajuste',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def documentos_com_ajustes(self, request, uuid):
        analise_prestacao = AnalisePrestacaoConta.by_uuid(uuid)
        documentos = analise_prestacao.analises_de_documento.filter(resultado='AJUSTE').all().order_by('tipo_documento_prestacao_conta__nome')
        return Response(AnaliseDocumentoPrestacaoContaRetrieveSerializer(documentos, many=True).data, status=status.HTTP_200_OK)
