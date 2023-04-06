from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from ...models import AnaliseDocumentoPrestacaoConta, ObservacaoConciliacao
from ..serializers import AnaliseDocumentoPrestacaoContaRetrieveSerializer
from sme_ptrf_apps.core.services import SolicitacaoAcertoDocumentoService
from sme_ptrf_apps.core.models import SolicitacaoAcertoDocumento, AnalisePrestacaoConta
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from rest_framework.response import Response
from rest_framework.decorators import action


class AnaliseDocumentoPrestacaoContaViewSet(mixins.UpdateModelMixin,
                                            mixins.RetrieveModelMixin,
                                            GenericViewSet):

    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = AnaliseDocumentoPrestacaoConta.objects.all()
    serializer_class = AnaliseDocumentoPrestacaoContaRetrieveSerializer

    @action(detail=False, methods=['post'], url_path='limpar-status',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def limpar_status(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import \
            AcoesStatusSolicitacaoAcertoDocumentoValidateSerializer

        query = AcoesStatusSolicitacaoAcertoDocumentoValidateSerializer(data=self.request.data)
        query.is_valid(raise_exception=True)

        uuids_solicitacoes_acertos_documentos = self.request.data.get('uuids_solicitacoes_acertos_documentos', None)
        response = SolicitacaoAcertoDocumentoService.limpar_status(
            uuids_solicitacoes_acertos_documentos=uuids_solicitacoes_acertos_documentos,
        )

        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['post'], url_path='justificar-nao-realizacao',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def justificar_nao_realizacao(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import \
            AcoesStatusSolicitacaoAcertoDocumentoValidateSerializer

        query = AcoesStatusSolicitacaoAcertoDocumentoValidateSerializer(data=self.request.data)
        query.is_valid(raise_exception=True)

        uuids_solicitacoes_acertos_documentos = self.request.data.get('uuids_solicitacoes_acertos_documentos', None)
        justificativa = self.request.data.get('justificativa', None)

        response = SolicitacaoAcertoDocumentoService.justificar_nao_realizacao(
            uuids_solicitacoes_acertos_documentos=uuids_solicitacoes_acertos_documentos,
            justificativa=justificativa
        )

        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['post'], url_path='marcar-como-realizado',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_como_realizado(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import \
            AcoesStatusSolicitacaoAcertoDocumentoValidateSerializer

        query = AcoesStatusSolicitacaoAcertoDocumentoValidateSerializer(data=self.request.data)
        query.is_valid(raise_exception=True)

        uuids_solicitacoes_acertos_documentos = self.request.data.get('uuids_solicitacoes_acertos_documentos', None)
        response = SolicitacaoAcertoDocumentoService.marcar_como_realizado(
            uuids_solicitacoes_acertos_documentos=uuids_solicitacoes_acertos_documentos
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
            "status_realizacao": AnaliseDocumentoPrestacaoConta.status_realizacao_choices_to_json(),
            "status_realizacao_solicitacao": SolicitacaoAcertoDocumento.status_realizacao_choices_to_json(),
            "editavel": AnalisePrestacaoConta.editavel(uuid_analise_prestacao, visao)
        }

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='marcar-como-credito-incluido',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_como_credito_incluido(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import \
            GravarCreditoIncluidoDocumentoValidateSerializer

        query = GravarCreditoIncluidoDocumentoValidateSerializer(data=self.request.data)
        query.is_valid(raise_exception=True)

        uuid_solicitacao_acerto = self.request.data.get('uuid_solicitacao_acerto', None)
        uuid_credito_incluido = self.request.data.get('uuid_credito_incluido', None)

        response = SolicitacaoAcertoDocumentoService.marcar_como_credito_incluido(
            uuid_solicitacao_acerto=uuid_solicitacao_acerto,
            uuid_credito_incluido=uuid_credito_incluido
        )

        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['post'], url_path='marcar-como-gasto-incluido',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_como_gasto_incluido(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import \
            GravarGastoIncluidoDocumentoValidateSerializer

        query = GravarGastoIncluidoDocumentoValidateSerializer(data=self.request.data)
        query.is_valid(raise_exception=True)

        uuid_solicitacao_acerto = self.request.data.get('uuid_solicitacao_acerto', None)
        uuid_gasto_incluido = self.request.data.get('uuid_gasto_incluido', None)

        response = SolicitacaoAcertoDocumentoService.marcar_como_gasto_incluido(
            uuid_solicitacao_acerto=uuid_solicitacao_acerto,
            uuid_gasto_incluido=uuid_gasto_incluido
        )

        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['post'], url_path='marcar-como-esclarecido',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_como_esclarecido(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import \
            GravarEsclarecimentoAcertoDocumentoValidateSerializer

        query = GravarEsclarecimentoAcertoDocumentoValidateSerializer(data=self.request.data)
        query.is_valid(raise_exception=True)

        uuid_solicitacao_acerto = self.request.data.get('uuid_solicitacao_acerto', None)
        esclarecimento = self.request.data.get('esclarecimento', None)

        response = SolicitacaoAcertoDocumentoService.marcar_como_esclarecido(
            uuid_solicitacao_acerto=uuid_solicitacao_acerto,
            esclarecimento=esclarecimento,
        )

        status_response = response.pop("status")

        return Response(response, status=status_response)


    @action(detail=False, methods=['post'], url_path='editar-informacao-conciliacao',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def editar_informacao_conciliacao(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import EditarInformacaoConciliacaoValidateSerializer

        query = EditarInformacaoConciliacaoValidateSerializer(data=self.request.data)
        query.is_valid(raise_exception=True)

        uuid_analise_documento = self.request.data.get('uuid_analise_documento', None)
        justificativa_conciliacao = self.request.data.get('justificativa_conciliacao', None)

        response = SolicitacaoAcertoDocumentoService.editar_informacao_conciliacao(
            uuid_analise_documento=uuid_analise_documento,
            justificativa_conciliacao=justificativa_conciliacao
        )

        status_response = response.pop("status")

        return Response(response, status=status_response)


    @action(detail=False, methods=['post'], url_path='restaurar-justificativa-original',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def reataurar_justificativa_original(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers import DesfazerEditacaoInformacaoConciliacaoValidateSerializer

        query = DesfazerEditacaoInformacaoConciliacaoValidateSerializer(data=self.request.data)
        query.is_valid(raise_exception=True)

        uuid_solicitacao_acerto = self.request.data.get('uuid_solicitacao_acerto', None)

        response = SolicitacaoAcertoDocumentoService.reataurar_justificativa_original(
            uuid_solicitacao_acerto=uuid_solicitacao_acerto,
        )

        status_response = response.pop("status")

        return Response(response, status=status_response)
