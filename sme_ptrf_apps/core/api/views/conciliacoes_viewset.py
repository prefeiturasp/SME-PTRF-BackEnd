import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse)

from django.http import HttpResponse

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao,
    PermissaoAPITodosComGravacao,
)

from ....despesas.api.serializers.rateio_despesa_serializer import RateioDespesaListaSerializer
from ....receitas.api.serializers.receita_serializer import ReceitaListaSerializer
from ...models import AcaoAssociacao, ContaAssociacao, ObservacaoConciliacao, Periodo, Associacao
from ...services import (
    despesas_conciliadas_por_conta_e_acao_na_conciliacao,
    despesas_nao_conciliadas_por_conta_e_acao_no_periodo,
    receitas_conciliadas_por_conta_e_acao_na_conciliacao,
    receitas_nao_conciliadas_por_conta_e_acao_no_periodo,
    info_resumo_conciliacao,
    transacoes_para_conciliacao,
    conciliar_transacao,
    desconciliar_transacao,
    salva_conciliacao_bancaria,
    permite_editar_campos_extrato
)
from ....despesas.models import Despesa
from ....receitas.models import Receita

import mimetypes

logger = logging.getLogger(__name__)


class ConciliacoesViewSet(GenericViewSet):
    lookup_field = 'uuid'

    permission_classes = [IsAuthenticated & PermissaoApiUe]
    queryset = ObservacaoConciliacao.objects.all()

    @extend_schema(
        parameters=[
            OpenApiParameter(name='conta_associacao', description='UUID da Conta da Associação', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='periodo', description='UUID do Período', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiResponse(
            response={
                'type': 'object',
                'properties': {
                    'saldo_anterior': {'type': 'number'},
                    'saldo_anterior_conciliado': {'type': 'number'},
                    'saldo_anterior_nao_conciliado': {'type': 'number'},
                    'receitas_total': {'type': 'number'},
                    'receitas_conciliadas': {'type': 'number'},
                    'receitas_nao_conciliadas': {'type': 'number'},
                    'despesas_total': {'type': 'number'},
                    'despesas_conciliadas': {'type': 'number'},
                    'despesas_nao_conciliadas': {'type': 'number'},
                    'despesas_outros_periodos': {'type': 'number'},
                    'despesas_outros_periodos_conciliadas': {'type': 'number'},
                    'despesas_outros_periodos_nao_conciliadas': {'type': 'number'},
                    'saldo_posterior_total': {'type': 'number'},
                    'saldo_posterior_conciliado': {'type': 'number'},
                    'saldo_posterior_nao_conciliado': {'type': 'number'},
                },
            }
        )},
    )
    @action(detail=False, methods=['get'], url_path='tabela-valores-pendentes',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
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

    @extend_schema(
        parameters=[
            OpenApiParameter(name='conta_associacao', description='UUID da Conta da Associação', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='acao_associacao', description='UUID da Ação Associação', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='periodo', description='UUID do Período', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='conferido', description='Conferido?', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, enum=['True', 'False']),
        ],
        responses={200: ReceitaListaSerializer(many=True)},
    )
    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
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

    @extend_schema(
        parameters=[
            OpenApiParameter(name='periodo', description='UUID do Período', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='conta_associacao', description='UUID da Conta da Associação', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='acao_associacao', description='UUID da Ação Associação', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='conferido', description='Conferido?', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, enum=['True', 'False']),
        ],
        responses={200: RateioDespesaListaSerializer(many=True)},
    )
    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
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

    @action(detail=False, methods=['patch'], url_path='salvar-observacoes',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def salvar_observacoes(self, request):
        # Define o período de conciliação
        periodo_uuid = request.data.get('periodo_uuid')

        # Define se é um cadastro de justificativa ou extrato bancario
        justificativa_ou_extrato_bancario = request.data.get('justificativa_ou_extrato_bancario')

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
        texto_observacao = request.data.get('observacao', "")

        # Define comprovante extrato bancario
        comprovante_extrato = request.data.get('comprovante_extrato', None)
        data_atualizacao_comprovante_extrato = request.data.get('data_atualizacao_comprovante_extrato', None)

        salva_conciliacao_bancaria(justificativa_ou_extrato_bancario, texto_observacao, periodo,
                                   conta_associacao, data_extrato, saldo_extrato, comprovante_extrato,
                                   data_atualizacao_comprovante_extrato, ObservacaoConciliacao)

        return Response({'mensagem': 'Informações gravadas'}, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='associacao', description='UUID da Associação', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='periodo', description='UUID do Período', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='conta_associacao', description='UUID da Conta da Associação', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='conferido', description='Conferido?', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, enum=['True', 'False']),
        ],
        responses={200: OpenApiResponse(
            response={
                'type': 'object',
                'properties': {
                    'data_encerramento': {'type': 'string', 'format': 'date'},
                    'saldo_encerramewnto': {'type': 'number'},
                    'possui_solicitacao_encerramento': {'type': 'boolean'},
                    'data_extrato': {'type': 'string', 'format': 'date'},
                    'saldo_extrato': {'type': 'number'},
                    'observacao_uuid': {'type': 'string'},
                    'observacao': {'type': 'string'},
                    'comprovante_extrato': {'type': 'string'},
                    'data_atualizacao_comprovante_extrato': {'type': 'string', 'format': 'date'},
                    'permite_editar_campos_extrato': {'type': 'boolean'},
                },
            }
        )},
    )
    @action(detail=False, methods=['get'], url_path='observacoes',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def observacoes(self, request):

        # Define a Associacao
        associacao_uuid = self.request.query_params.get('associacao')

        if not associacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associacao para o uuid {associacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

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

        comprovante_extrato_nome = ''

        if observacao and observacao.comprovante_extrato and observacao.comprovante_extrato.name:
            comprovante_extrato_nome = observacao.comprovante_extrato.name

        info_solicitacao = conta_associacao.get_info_solicitacao_encerramento(periodo)

        permite_editar = permite_editar_campos_extrato(
            associacao,
            periodo,
            conta_associacao
        )

        result = {
            'observacao_uuid': observacao.uuid if observacao else None,
            'observacao': observacao.texto if observacao else None,
            'saldo_extrato': observacao.saldo_extrato if observacao else None,
            'data_extrato': observacao.data_extrato if observacao else None,
            'comprovante_extrato': comprovante_extrato_nome if observacao else None,
            'data_atualizacao_comprovante_extrato': observacao.data_atualizacao_comprovante_extrato if observacao else None,
            'data_encerramento': info_solicitacao["data_encerramento"] if info_solicitacao["possui_solicitacao_encerramento"] else None,
            'saldo_encerramewnto': info_solicitacao["saldo"] if info_solicitacao["possui_solicitacao_encerramento"] else None,
            'possui_solicitacao_encerramento': info_solicitacao["possui_solicitacao_encerramento"],
            'permite_editar_campos_extrato': permite_editar
        }

        # Regra US #129997
        if info_solicitacao["possui_solicitacao_encerramento"]:
            result['data_extrato'] = info_solicitacao["data_encerramento"]
        else:
            result['data_extrato'] = periodo.data_fim_realizacao_despesas

        return Response(result, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='observacao_uuid', description='UUID da Observação', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiTypes.BINARY},
    )
    @action(detail=False, methods=['get'], url_path='download-extrato-bancario',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao]
            )
    def download_extrato_bancario(self, request):
        # Define o observacao da conciliacao
        observacao_uuid = request.query_params.get('observacao_uuid')

        if not observacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da observacao da conciliação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            observacao = ObservacaoConciliacao.by_uuid(observacao_uuid)
        except ObservacaoConciliacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto observacao para o uuid {observacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f'Download do extrato bancário para a Observacao uuid {observacao_uuid}')

        observacao = ObservacaoConciliacao.by_uuid(observacao_uuid)

        if observacao and observacao.comprovante_extrato and observacao.comprovante_extrato.name:
            comprovante_extrato_nome = observacao.comprovante_extrato.name
            comprovante_extrato_path = observacao.comprovante_extrato.path
            comprovante_extrato_file_mime = mimetypes.guess_type(observacao.comprovante_extrato.name)[0]

            logger.info("Retornando dados do extrato bancario: %s", comprovante_extrato_path)

            try:
                response = HttpResponse(
                    open(comprovante_extrato_path, 'rb'),
                    content_type=comprovante_extrato_file_mime
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % comprovante_extrato_nome
            except Exception as err:
                erro = {
                    'erro': 'extrato_bancario_nao_gerado',
                    'mensagem': str(err)
                }
                logger.info("Erro: %s", str(err))
                return Response(erro, status=status.HTTP_404_NOT_FOUND)

            return response

        else:
            erro = {
                'erro': 'extrato_bancario_nao_encontrado',
                'mensagem': 'Extrato bancário não encontrado'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='transacoes-despesa',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def transacoes_despesas(self, request):

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

        # Ordenação
        ordenar_por_numero_do_documento = self.request.query_params.get('ordenar_por_numero_do_documento')
        ordenar_por_data_especificacao = self.request.query_params.get('ordenar_por_data_especificacao')
        ordenar_por_valor = self.request.query_params.get('ordenar_por_valor')
        ordenar_por_imposto = self.request.query_params.get('ordenar_por_imposto')

        transacoes = transacoes_para_conciliacao(
            periodo=periodo, conta_associacao=conta_associacao,
            conferido=conferido,
            acao_associacao=acao_associacao,
            ordenar_por_numero_do_documento=ordenar_por_numero_do_documento,
            ordenar_por_data_especificacao=ordenar_por_data_especificacao,
            ordenar_por_valor=ordenar_por_valor,
            ordenar_por_imposto=ordenar_por_imposto
        )

        return Response(transacoes, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='conciliar-despesa',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def conciliar_despesa(self, request):

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

        # Define a transação
        transacao_uuid = self.request.query_params.get('transacao')

        if not transacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da transação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            transacao = Despesa.completas.get(uuid=transacao_uuid)
        except Despesa.DoesNotExist:
            erro = {
                'erro': 'Gasto não encontrado.',
                'mensagem': f"O objeto de gasto para o uuid {transacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        transacao_conciliada = conciliar_transacao(
            periodo=periodo,
            conta_associacao=conta_associacao,
            transacao=transacao,
        )

        return Response(transacao_conciliada, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='desconciliar-despesa',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def desconciliar_despesa(self, request):

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

        # Define a transação
        transacao_uuid = self.request.query_params.get('transacao')

        if not transacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da transação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            transacao = Despesa.completas.get(uuid=transacao_uuid)
        except (Despesa.DoesNotExist, Receita.DoesNotExist):
            erro = {
                'erro': 'Gasto não encontrado.',
                'mensagem': f"O objeto de Gasto para o uuid {transacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        transacao_desconciliada = desconciliar_transacao(
            conta_associacao=conta_associacao,
            transacao=transacao,
        )

        return Response(transacao_desconciliada, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='extrato-bancario',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao]
            )
    def extrato_bancario(self, request, uuid):

        observacao = ObservacaoConciliacao.by_uuid(uuid)

        if observacao and observacao.comprovante_extrato and observacao.comprovante_extrato.name:
            comprovante_extrato_nome = observacao.comprovante_extrato.name
            comprovante_extrato_path = observacao.comprovante_extrato.path
            comprovante_extrato_file_mime = mimetypes.guess_type(observacao.comprovante_extrato.name)[0]

            logger.info("Retornando dados do extrato bancario: %s", comprovante_extrato_path)

            try:
                response = HttpResponse(
                    open(comprovante_extrato_path, 'rb'),
                    content_type=comprovante_extrato_file_mime
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % comprovante_extrato_nome
            except Exception as err:
                erro = {
                    'erro': 'extrato_bancario_nao_gerado',
                    'mensagem': str(err)
                }
                logger.info("Erro: %s", str(err))
                return Response(erro, status=status.HTTP_404_NOT_FOUND)

            return response

        else:
            erro = {
                'erro': 'extrato_bancario_nao_encontrado',
                'mensagem': 'Extrato bancário não encontrado'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='tem_ajuste_bancario',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def tem_ajuste_bancario(self, request):

        # Define a Associacao
        associacao_uuid = self.request.query_params.get('associacao')

        if not associacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associacao para o uuid {associacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

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

        permite_editar = permite_editar_campos_extrato(
            associacao,
            periodo,
            conta_associacao
        )

        result = {
            'permite_editar_campos_extrato': permite_editar,
        }

        return Response(result, status=status.HTTP_200_OK)
