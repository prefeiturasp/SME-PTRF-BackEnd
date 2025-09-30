import logging

from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from ...models import AnaliseLancamentoPrestacaoConta, SolicitacaoAcertoLancamento, AnalisePrestacaoConta, Periodo
from ..serializers import AnaliseLancamentoPrestacaoContaRetrieveSerializer
from sme_ptrf_apps.core.services import AnaliseLancamentoPrestacaoContaService
from sme_ptrf_apps.core.services import SolicitacaoAcertoLancamentoService
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample


logger = logging.getLogger(__name__)


@extend_schema_view(
    limpar_status=extend_schema(
        description="Recebe uma lista de UUIDs de solicitações de acerto e limpa o status delas.",
        request={
            "payload": {
                "type": "object", "required": True, "properties": {
                    "uuids_solicitacoes_acertos_lancamentos": {"type": "array", "items": {"type": "string"}},
                    "justificativa": {"type": "string"}
                }
            }
        },
        responses={200: 'result'},
        examples=[
            OpenApiExample('Resposta', value={"mensagem": "Status alterado com sucesso!", "status": 200})
        ]
    ),
    justificar_nao_realizacao=extend_schema(
        description="Registra uma justificativa para a não realização de uma solicitação de acerto.",
        request={
            "payload": {
                "type": "object", "required": True, "properties": {
                    "uuids_solicitacoes_acertos_lancamentos": {"type": "array", "items": {"type": "string"}},
                    "justificativa": {"type": "string"}
                }
            }
        },
        responses={200: 'result'},
        examples=[
            OpenApiExample('Resposta', value={
                "mensagem": "Status alterados com sucesso!",
                "status": 200,
                "todas_as_solicitacoes_marcadas_como_justificado": True,
            })
        ]
    ),
    marcar_como_realizado=extend_schema(
        description="Marca solicitações de acerto como realizadas.",
        request={
            "payload": {
                "type": "object", "required": True, "properties": {
                    "uuids_solicitacoes_acertos_lancamentos": {"type": "array", "items": {"type": "string"}},
                    "justificativa": {"type": "string"}
                }
            }
        },
        responses={200: 'result'},
        examples=[
            OpenApiExample('Resposta', value={
                "mensagem": "Status alterados com sucesso!",
                "status": status.HTTP_200_OK,
                "todas_as_solicitacoes_marcadas_como_realizado": True,
            })
        ]
    ),
    tabelas=extend_schema(
        description="Retorna tabelas de apoio (status de realização, editabilidade, etc).",
        parameters=[
            OpenApiParameter("uuid_analise_prestacao", str, OpenApiParameter.QUERY,
                             description="UUID da análise de prestação"),
            OpenApiParameter("visao", str, OpenApiParameter.QUERY,
                             description="Visão do usuário"),
        ],
        responses={200: 'result'},
        examples=[
            OpenApiExample('Resposta', value={
                "status_realizacao": "|".join([
                    AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE,
                    AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO,
                    AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_JUSTIFICADO,
                    AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO_JUSTIFICADO,
                    AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO_PARCIALMENTE
                ]),
                "status_realizacao_solicitacao": "|".join([
                    SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE,
                    SolicitacaoAcertoLancamento.STATUS_REALIZACAO_REALIZADO,
                    SolicitacaoAcertoLancamento.STATUS_REALIZACAO_JUSTIFICADO
                ]),
                "editavel": True
            })
        ]
    ),
    marcar_devolucao_tesouro_atualizada=extend_schema(
        description="Atualiza a devolução ao Tesouro como **atualizada**.",
        responses={200: AnaliseLancamentoPrestacaoContaRetrieveSerializer},
    ),
    marcar_devolucao_tesouro_nao_atualizada=extend_schema(
        description="Atualiza a devolução ao Tesouro como **não atualizada**.",
        responses={200: AnaliseLancamentoPrestacaoContaRetrieveSerializer},
    ),
    marcar_lancamento_atualizado=extend_schema(
        description="Marca o lançamento como **atualizado**.",
        responses={200: AnaliseLancamentoPrestacaoContaRetrieveSerializer},
    ),
    marcar_lancamento_excluido=extend_schema(
        description="Marca o lançamento como **excluído**.",
        responses={200: AnaliseLancamentoPrestacaoContaRetrieveSerializer},
    ),
    marcar_como_esclarecido=extend_schema(
        description="Adiciona esclarecimento e marca a solicitação como esclarecida.",
        request={
            "payload": {
                "type": "object", "required": True, "properties": {
                    "uuid_solicitacao_acerto": {"type": "string"},
                    "esclarecimento": {"type": "string"}
                }
            }
        },
        responses={200: 'result'},
        examples=[
            OpenApiExample('Resposta', value={
                "mensagem": "Esclarecimento atualizado com sucesso.",
                "status": 200,
            })
        ]
    ),
    marcar_como_conciliado=extend_schema(
        description="Marca o lançamento como conciliado em um período específico.",
        request={
            "payload": {
                "type": "object", "required": True, "properties": {
                    "uuid_analise_lancamento": {"type": "string"},
                    "uuid_periodo": {"type": "string"}
                }
            }
        },
        responses={200: 'result'},
        examples=[
            OpenApiExample('Resposta', value={
                "mensagem": "Esclarecimento atualizado com sucesso.",
                "status": 200
            })
        ]
    ),
    marcar_como_desconciliado=extend_schema(
        description="Remove a conciliação de um lançamento previamente conciliado.",
        request={
            "payload": {
                "type": "object", "required": True, "properties": {
                    "uuid_analise_lancamento": {"type": "string"},
                }
            }
        },
        responses={200: AnaliseLancamentoPrestacaoContaRetrieveSerializer},
    ),
    tags_informacoes_conferencia_list=extend_schema(
        description="Retorna as tags utilizadas nas informações de conferência.",
        responses={200: 'result'},
        examples=[
            OpenApiExample(
                'Resposta',
                value=AnaliseLancamentoPrestacaoConta.get_tags_informacoes_de_conferencia_list())
        ],
    ),
)
class AnaliseLancamentoPrestacaoContaViewSet(mixins.UpdateModelMixin,
                                             mixins.RetrieveModelMixin,
                                             GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = AnaliseLancamentoPrestacaoConta.objects.all()
    serializer_class = AnaliseLancamentoPrestacaoContaRetrieveSerializer

    @action(detail=False, methods=['post'], url_path='limpar-status',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def limpar_status(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import \
            AcoesStatusSolicitacaoAcertoLancamentoValidateSerializer

        query = AcoesStatusSolicitacaoAcertoLancamentoValidateSerializer(data=self.request.data)
        query.is_valid(raise_exception=True)

        uuids_solicitacoes_acertos_lancamentos = self.request.data.get('uuids_solicitacoes_acertos_lancamentos', None)

        response = SolicitacaoAcertoLancamentoService.limpar_status(
            uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes_acertos_lancamentos,
        )

        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['post'], url_path='justificar-nao-realizacao',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def justificar_nao_realizacao(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import \
            AcoesStatusSolicitacaoAcertoLancamentoValidateSerializer

        query = AcoesStatusSolicitacaoAcertoLancamentoValidateSerializer(data=self.request.data)
        query.is_valid(raise_exception=True)

        uuids_solicitacoes_acertos_lancamentos = self.request.data.get('uuids_solicitacoes_acertos_lancamentos', None)
        justificativa = request.data.get('justificativa', None)

        response = SolicitacaoAcertoLancamentoService.justificar_nao_realizacao(
            uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes_acertos_lancamentos,
            justificativa=justificativa
        )

        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['post'], url_path='marcar-como-realizado',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_como_realizado(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import \
            AcoesStatusSolicitacaoAcertoLancamentoValidateSerializer

        query = AcoesStatusSolicitacaoAcertoLancamentoValidateSerializer(data=self.request.data)

        query.is_valid(raise_exception=True)

        uuids_solicitacoes_acertos_lancamentos = self.request.data.get('uuids_solicitacoes_acertos_lancamentos', None)
        response = SolicitacaoAcertoLancamentoService.marcar_como_realizado(
            uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes_acertos_lancamentos
        )

        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['get'], url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def tabelas(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import \
            TabelasValidateSerializer

        query = TabelasValidateSerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)

        uuid_analise_prestacao = self.request.query_params.get('uuid_analise_prestacao')
        visao = self.request.query_params.get('visao')

        result = {
            "status_realizacao": AnaliseLancamentoPrestacaoConta.status_realizacao_choices_to_json(),
            "status_realizacao_solicitacao": SolicitacaoAcertoLancamento.status_realizacao_choices_to_json(),
            "editavel": AnalisePrestacaoConta.editavel(uuid_analise_prestacao, visao)
        }

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='marcar-devolucao-tesouro-atualizada',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_devolucao_tesouro_atualizada(self, request, uuid):
        uuid_analise_lancamento = uuid

        if not uuid_analise_lancamento:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da Análise de Lançamento da PC'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_lancamento = self.get_object()
        except (ValidationError, Exception):
            erro = {
                'erro': 'objeto_analise_lancamento_pc_nao_encontrado',
                'mensagem': (
                    'Não foi encontrado um objeto Análise de Lançamento da PC com '
                    f'o uuid {uuid_analise_lancamento} na base')
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = AnaliseLancamentoPrestacaoContaService.marcar_devolucao_tesouro_como_atualizada(
                analise_lancamento=analise_lancamento
            )

            return Response(
                AnaliseLancamentoPrestacaoContaRetrieveSerializer(response, many=False).data,
                status=status.HTTP_200_OK)

        except:  # noqa
            erro = {
                'erro': 'erro_ao_passar_devolucao_ao_tesouro_para_autalizada',
                'mensagem': (
                    'Não foi possível passar a Devolução ao Tesouro da Análise de Lançamento da '
                    f'PC {uuid_analise_lancamento} para atualizada')
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='marcar-devolucao-tesouro-nao-atualizada',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_devolucao_tesouro_nao_atualizada(self, request, uuid):
        uuid_analise_lancamento = uuid

        if not uuid_analise_lancamento:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da Análise de Lançamento da PC'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_lancamento = self.get_object()
        except (ValidationError, Exception):
            erro = {
                'erro': 'objeto_analise_lancamento_pc_nao_encontrado',
                'mensagem': (
                    f'Não foi encontrado um objeto Análise de Lançamento da PC com o uuid {uuid_analise_lancamento} '
                    'na base')
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = AnaliseLancamentoPrestacaoContaService.marcar_devolucao_tesouro_como_nao_atualizada(
                analise_lancamento=analise_lancamento
            )

            return Response(
                AnaliseLancamentoPrestacaoContaRetrieveSerializer(response, many=False).data,
                status=status.HTTP_200_OK)

        except:  # noqa
            erro = {
                'erro': 'erro_ao_passar_devolucao_ao_tesouro_para_nao_autalizada',
                'mensagem': (
                    'Não foi possível passar a Devolução ao Tesouro da Análise de Lançamento da '
                    f'PC {uuid_analise_lancamento} para não atualizada')
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='marcar-lancamento-atualizado',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_lancamento_atualizado(self, request, uuid):
        uuid_analise_lancamento = uuid

        if not uuid_analise_lancamento:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da Análise de Lançamento da PC'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_lancamento = self.get_object()
        except (ValidationError, Exception):
            erro = {
                'erro': 'objeto_analise_lancamento_pc_nao_encontrado',
                'mensagem': (
                    f'Não foi encontrado um objeto Análise de Lançamento da PC com o uuid {uuid_analise_lancamento} '
                    'na base')
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = AnaliseLancamentoPrestacaoContaService.marcar_lancamento_como_atualizado(
                analise_lancamento=analise_lancamento
            )

            return Response(
                AnaliseLancamentoPrestacaoContaRetrieveSerializer(response, many=False).data,
                status=status.HTTP_200_OK)

        except:  # noqa
            erro = {
                'erro': 'erro_ao_passar_devolucao_ao_tesouro_para_autalizada',
                'mensagem': (
                    f'Não foi possível passar o Lançamento da Análise UUID: {uuid_analise_lancamento} para atualizado')
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='marcar-lancamento-excluido',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_lancamento_excluido(self, request, uuid):
        uuid_analise_lancamento = uuid

        if not uuid_analise_lancamento:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da Análise de Lançamento da PC'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_lancamento = self.get_object()
        except (ValidationError, Exception):
            erro = {
                'erro': 'objeto_analise_lancamento_pc_nao_encontrado',
                'mensagem': (
                    f'Não foi encontrado um objeto Análise de Lançamento da PC com o uuid {uuid_analise_lancamento} '
                    'na base')
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = AnaliseLancamentoPrestacaoContaService.marcar_lancamento_como_excluido(
                analise_lancamento=analise_lancamento
            )

            return Response(
                AnaliseLancamentoPrestacaoContaRetrieveSerializer(response, many=False).data,
                status=status.HTTP_200_OK)

        except:  # noqa
            erro = {
                'erro': 'erro_ao_passar_devolucao_ao_tesouro_para_autalizada',
                'mensagem': (
                    f'Não foi possível passar o Lançamento da Análise UUID: {uuid_analise_lancamento} para excluído')
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='marcar-como-esclarecido',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_como_esclarecido(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import \
            GravarEsclarecimentoAcertoLancamentoValidateSerializer

        query = GravarEsclarecimentoAcertoLancamentoValidateSerializer(data=self.request.data)

        query.is_valid(raise_exception=True)

        uuid_solicitacao_acerto = self.request.data.get('uuid_solicitacao_acerto', None)
        esclarecimento = self.request.data.get('esclarecimento', None)

        response = SolicitacaoAcertoLancamentoService.marcar_como_esclarecido(
            uuid_solicitacao_acerto=uuid_solicitacao_acerto,
            esclarecimento=esclarecimento,
        )

        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['post'], url_path='marcar-como-conciliado',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_como_conciliado(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import \
            GravarConciliacaoAnaliseLancamentoValidateSerializer

        query = GravarConciliacaoAnaliseLancamentoValidateSerializer(data=self.request.data)

        query.is_valid(raise_exception=True)

        uuid_analise_lancamento = self.request.data.get('uuid_analise_lancamento', None)
        uuid_periodo = self.request.data.get('uuid_periodo', None)

        analise_lancamento = AnaliseLancamentoPrestacaoConta.by_uuid(uuid_analise_lancamento)
        periodo = Periodo.by_uuid(uuid_periodo)

        try:
            response = AnaliseLancamentoPrestacaoContaService.marcar_lancamento_como_conciliado(
                analise_lancamento=analise_lancamento,
                periodo=periodo
            )

            return Response(AnaliseLancamentoPrestacaoContaRetrieveSerializer(
                response, many=False).data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(f'Ocorreu um erro ao tentar conciliar o lançamento: {uuid_analise_lancamento} : {e}')

            erro = {
                'erro': 'erro_ao_conciliar',
                'mensagem': (
                    f'Não foi possível passar o Lançamento da Análise UUID: {uuid_analise_lancamento} '
                    'para conciliado')
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='marcar-como-desconciliado',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_como_desconciliado(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import \
            GravarDesconciliacaoAnaliseLancamentoValidateSerializer

        query = GravarDesconciliacaoAnaliseLancamentoValidateSerializer(data=self.request.data)
        query.is_valid(raise_exception=True)

        uuid_analise_lancamento = self.request.data.get('uuid_analise_lancamento', None)
        analise_lancamento = AnaliseLancamentoPrestacaoConta.by_uuid(uuid_analise_lancamento)

        try:
            response = AnaliseLancamentoPrestacaoContaService.marcar_lancamento_como_desconciliado(
                analise_lancamento=analise_lancamento,
            )

            return Response(AnaliseLancamentoPrestacaoContaRetrieveSerializer(
                response, many=False).data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(f'Ocorreu um erro ao tentar desconciliar o lançamento: {uuid_analise_lancamento} : {e}')

            erro = {
                'erro': 'erro_ao_desconciliar',
                'mensagem': (
                    f'Não foi possível passar o Lançamento da Análise UUID: {uuid_analise_lancamento} '
                    'para desconciliado')
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, url_path='tags-informacoes-conferencia',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def tags_informacoes_conferencia_list(self, request):

        result = AnaliseLancamentoPrestacaoConta.get_tags_informacoes_de_conferencia_list()

        return Response(result)
