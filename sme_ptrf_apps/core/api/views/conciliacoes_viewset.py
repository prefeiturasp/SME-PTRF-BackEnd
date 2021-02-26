import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.users.permissoes import (PermissaoPrestacaoConta, PermissaoVerConciliacaoBancaria,
                                            PermissaoEditarConciliacaoBancaria)

from ....despesas.api.serializers.rateio_despesa_serializer import RateioDespesaListaSerializer
from ....receitas.api.serializers.receita_serializer import ReceitaListaSerializer
from ...models import AcaoAssociacao, ContaAssociacao, ObservacaoConciliacao, Periodo
from ...services import (
    despesas_conciliadas_por_conta_e_acao_na_conciliacao,
    despesas_nao_conciliadas_por_conta_e_acao_no_periodo,
    receitas_conciliadas_por_conta_e_acao_na_conciliacao,
    receitas_nao_conciliadas_por_conta_e_acao_no_periodo,
    info_resumo_conciliacao,
    transacoes_para_conciliacao,
)

logger = logging.getLogger(__name__)


class ConciliacoesViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated & (
        PermissaoPrestacaoConta | PermissaoVerConciliacaoBancaria | PermissaoEditarConciliacaoBancaria)]
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

        result = info_resumo_conciliacao(periodo=periodo, conta_associacao=conta_associacao)
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

        # Define a data e saldo do extrato
        data_extrato = request.data.get('data_extrato', None)
        saldo_extrato = request.data.get('saldo_extrato', 0.0)

        # Define texto
        texto_observacao = request.data.get('observacao')

        ObservacaoConciliacao.criar_atualizar(
            periodo=periodo,
            conta_associacao=conta_associacao,
            texto_observacao=texto_observacao,
            data_extrato=data_extrato,
            saldo_extrato=saldo_extrato
        )

        return Response({'mensagem': 'Informações gravadas'}, status=status.HTTP_200_OK)

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

        observacao = ObservacaoConciliacao.objects.filter(periodo=periodo, conta_associacao=conta_associacao).first()

        result = {}

        if observacao:
            result = {
                'observacao': observacao.texto,
                'data_extrato': observacao.data_extrato,
                'saldo_extrato': observacao.saldo_extrato
            }

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def transacoes(self, request):

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

        # Define o flag de Conferido para o filtro das transações
        conferido = request.query_params.get('conferido')
        if conferido is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o flag de conferido.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if conferido not in ('True', 'False'):
            erro = {
                'erro': 'parametro_inválido',
                'mensagem': 'O parâmetro "conferido" deve receber como valor "True" ou "False". '
                            'O parâmetro é obrigatório.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        conferido = conferido == 'True'

        # Define o tipo de transação para o filtro das transações
        tipo_transacao = request.query_params.get('tipo')
        if tipo_transacao and tipo_transacao not in ('CREDITOS', 'GASTOS'):
            erro = {
                'erro': 'parametro_inválido',
                'mensagem': 'O parâmetro tipo pode receber como valor "CREDITOS" ou "GASTOS". O parâmetro é opcional.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        transacoes = transacoes_para_conciliacao(periodo=periodo, conta_associacao=conta_associacao,
                                                 conferido=conferido,
                                                 acao_associacao=acao_associacao,
                                                 tipo_transacao=tipo_transacao)

        return Response(transacoes, status=status.HTTP_200_OK)
