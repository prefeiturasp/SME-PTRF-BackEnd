import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.users.permissoes import PermissaoPrestacaoConta, PermissaoVerConciliacaoBancaria, PermissaoEditarConciliacaoBancaria

from ....despesas.api.serializers.rateio_despesa_serializer import RateioDespesaListaSerializer
from ....receitas.api.serializers.receita_serializer import ReceitaListaSerializer
from ...models import AcaoAssociacao, ContaAssociacao, ObservacaoConciliacao, Periodo
from ...services import (
    despesas_conciliadas_por_conta_e_acao_na_conciliacao,
    despesas_nao_conciliadas_por_conta_e_acao_no_periodo,
    info_conciliacao_pendente,
    receitas_conciliadas_por_conta_e_acao_na_conciliacao,
    receitas_nao_conciliadas_por_conta_e_acao_no_periodo,
)

logger = logging.getLogger(__name__)


class ConciliacoesViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated & (PermissaoPrestacaoConta | PermissaoVerConciliacaoBancaria | PermissaoEditarConciliacaoBancaria)]
    queryset = ObservacaoConciliacao.objects.all()

    @action(detail=False, methods=['get'], url_path='tabela-valores-pendentes')
    def tabela_valores_pendentes(self, request):
        conta_associacao_uuid = self.request.query_params.get('conta_associacao')
        periodo_uuid = self.request.query_params.get('periodo')

        if not conta_associacao_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período e o uuid da conta da associação.'
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

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = info_conciliacao_pendente(periodo=periodo, conta_associacao=conta_associacao)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def receitas(self, request):

        # Define o período de conciliação
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período de conciliação.'
            }
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

        # Define a conta de concliação
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
        acao_associacao_uuid = request.query_params.get('acao_associacao')
        if acao_associacao_uuid is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da ação da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            acao_associacao = AcaoAssociacao.objects.get(uuid=acao_associacao_uuid)
        except AcaoAssociacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ação-associação para o uuid {acao_associacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Define o flag de Conferido para o filtro das transações
        conferido = request.query_params.get('conferido')
        if conferido is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o flag de conferido.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if conferido == 'True':
            receitas = receitas_conciliadas_por_conta_e_acao_na_conciliacao(conta_associacao=conta_associacao,
                                                                            acao_associacao=acao_associacao,
                                                                            periodo=periodo)
        else:
            receitas = receitas_nao_conciliadas_por_conta_e_acao_no_periodo(conta_associacao=conta_associacao,
                                                                            acao_associacao=acao_associacao,
                                                                            periodo=periodo)

        return Response(ReceitaListaSerializer(receitas, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def despesas(self, request):

        # Define o período de conciliação
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período de conciliação.'
            }
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

        # Define a conta de concliação
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
        acao_associacao_uuid = request.query_params.get('acao_associacao')
        if acao_associacao_uuid is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da ação da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            acao_associacao = AcaoAssociacao.objects.get(uuid=acao_associacao_uuid)
        except AcaoAssociacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ação-associação para o uuid {acao_associacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Define o flag de Conferido para o filtro das transações
        conferido = request.query_params.get('conferido')
        if conferido is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o flag de conferido.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if conferido == 'True':
            despesas = despesas_conciliadas_por_conta_e_acao_na_conciliacao(conta_associacao=conta_associacao,
                                                                            acao_associacao=acao_associacao,
                                                                            periodo=periodo)
        else:
            despesas = despesas_nao_conciliadas_por_conta_e_acao_no_periodo(conta_associacao=conta_associacao,
                                                                            acao_associacao=acao_associacao,
                                                                            periodo=periodo)

        return Response(RateioDespesaListaSerializer(despesas, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='salvar-observacoes')
    def salvar_observacoes(self, request):
        # Define o período de conciliação
        periodo_uuid = request.data.get('periodo_uuid')

        if not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período de conciliação.'
            }
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

        # Define a conta de conciliação
        conta_associacao_uuid = request.data.get('conta_associacao_uuid')

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

        observacoes = request.data.get('observacoes')

        ObservacaoConciliacao.criar_atualizar(periodo=periodo, conta_associacao=conta_associacao, lista_observacoes=observacoes)

        return Response({'mensagem': 'observacoes gravadas'},status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='observacoes')
    def observacoes(self, request):
        # Define o período de conciliação
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período de conciliação.'
            }
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

        # Define a conta de concliação
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

        observacoes = ObservacaoConciliacao.objects.filter(periodo=periodo, conta_associacao=conta_associacao).all()
        result = []
        if observacoes:
            for obs in observacoes:
                result.append({'observacao': obs.texto})

        return Response(result, status=status.HTTP_200_OK)
