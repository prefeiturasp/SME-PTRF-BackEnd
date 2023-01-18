from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from ...models import AnaliseLancamentoPrestacaoConta, SolicitacaoAcertoLancamento, AnalisePrestacaoConta
from ..serializers import AnaliseLancamentoPrestacaoContaRetrieveSerializer
from sme_ptrf_apps.core.services import AnaliseLancamentoPrestacaoContaService
from sme_ptrf_apps.core.services import SolicitacaoAcertoLancamentoService
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError


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
                'mensagem': f'Não foi encontrado um objeto Análise de Lançamento da PC com o uuid {uuid_analise_lancamento} na base'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = AnaliseLancamentoPrestacaoContaService.marcar_devolucao_tesouro_como_atualizada(
                analise_lancamento=analise_lancamento
            )

            return Response(AnaliseLancamentoPrestacaoContaRetrieveSerializer(response, many=False).data, status=status.HTTP_200_OK)

        except:
            erro = {
                'erro': 'erro_ao_passar_devolucao_ao_tesouro_para_autalizada',
                'mensagem': f'Não foi possível passar a Devolução ao Tesouro da Análise de Lançamento da PC {uuid_analise_lancamento} para atualizada'
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
                'mensagem': f'Não foi encontrado um objeto Análise de Lançamento da PC com o uuid {uuid_analise_lancamento} na base'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = AnaliseLancamentoPrestacaoContaService.marcar_devolucao_tesouro_como_nao_atualizada(
                analise_lancamento=analise_lancamento
            )

            return Response(AnaliseLancamentoPrestacaoContaRetrieveSerializer(response, many=False).data, status=status.HTTP_200_OK)

        except:
            erro = {
                'erro': 'erro_ao_passar_devolucao_ao_tesouro_para_nao_autalizada',
                'mensagem': f'Não foi possível passar a Devolução ao Tesouro da Análise de Lançamento da PC {uuid_analise_lancamento} para não atualizada'
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
                'mensagem': f'Não foi encontrado um objeto Análise de Lançamento da PC com o uuid {uuid_analise_lancamento} na base'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = AnaliseLancamentoPrestacaoContaService.marcar_lancamento_como_atualizado(
                analise_lancamento=analise_lancamento
            )

            return Response(AnaliseLancamentoPrestacaoContaRetrieveSerializer(response, many=False).data, status=status.HTTP_200_OK)

        except:
            erro = {
                'erro': 'erro_ao_passar_devolucao_ao_tesouro_para_autalizada',
                'mensagem': f'Não foi possível passar o Lançamento da Análise UUID: {uuid_analise_lancamento} para atualizado'
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
                'mensagem': f'Não foi encontrado um objeto Análise de Lançamento da PC com o uuid {uuid_analise_lancamento} na base'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = AnaliseLancamentoPrestacaoContaService.marcar_lancamento_como_excluido(
                analise_lancamento=analise_lancamento
            )

            return Response(AnaliseLancamentoPrestacaoContaRetrieveSerializer(response, many=False).data, status=status.HTTP_200_OK)

        except:
            erro = {
                'erro': 'erro_ao_passar_devolucao_ao_tesouro_para_autalizada',
                'mensagem': f'Não foi possível passar o Lançamento da Análise UUID: {uuid_analise_lancamento} para excluído'
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


