from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from ...models import AnaliseLancamentoPrestacaoConta
from ..serializers import AnaliseLancamentoPrestacaoContaUpdateSerializer, AnaliseLancamentoPrestacaoContaRetrieveSerializer
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
    serializer_class = AnaliseLancamentoPrestacaoContaUpdateSerializer

    @action(detail=False, methods=['post'], url_path='limpar-status',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def limpar_status(self, request):
        uuids_analises_lancamentos = request.data.get('uuids_analises_lancamentos', None)

        response = AnaliseLancamentoPrestacaoContaService.limpar_status(
            uuids_analises_lancamentos=uuids_analises_lancamentos
        )
        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['post'], url_path='justificar-nao-realizacao',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def justificar_nao_realizacao(self, request):
        uuids_analises_lancamentos = request.data.get('uuids_analises_lancamentos', None)
        justificativa = request.data.get('justificativa', None)

        response = AnaliseLancamentoPrestacaoContaService.justificar_nao_realizacao(
            uuids_analises_lancamentos=uuids_analises_lancamentos,
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

        # remover esse bloco após testar endpoint
        # uuids_analises_lancamentos = request.data.get('uuids_analises_lancamentos', None)

        # response = AnaliseLancamentoPrestacaoContaService.marcar_como_realizado(
        #     uuids_analises_lancamentos=uuids_analises_lancamentos
        # )

        uuids_solicitacoes_acertos_lancamentos = self.request.data.get('uuids_solicitacoes_acertos_lancamentos', None)

        response = SolicitacaoAcertoLancamentoService.marcar_como_realizado(
            uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes_acertos_lancamentos
        )

        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['get'], url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def tabelas(self, request):
        result = {
            "status_realizacao": AnaliseLancamentoPrestacaoConta.status_realizacao_choices_to_json(),
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

    @action(detail=True, methods=['post'], url_path='marcar-como-esclarecido',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_como_esclarecido(self, request, uuid):
        esclarecimento = request.data.get('esclarecimento', None)

        uuid_analise_lancamento = uuid

        if not uuid_analise_lancamento:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da Análise de Lançamento da PC'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        response = AnaliseLancamentoPrestacaoContaService.marcar_como_esclarecido(
            uuid_analise_lancamento=uuid_analise_lancamento,
            esclarecimento=esclarecimento,
        )

        status_response = response.pop("status")

        return Response(response, status=status_response)


