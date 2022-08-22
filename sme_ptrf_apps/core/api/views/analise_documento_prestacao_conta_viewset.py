from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from ...models import AnaliseDocumentoPrestacaoConta
from ..serializers import AnaliseDocumentoPrestacaoContaUpdateSerializer
from sme_ptrf_apps.core.services.analise_documento_prestacao_conta_service import (
    AnaliseDocumentoPrestacaoContaService,
)
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from rest_framework.response import Response
from rest_framework.decorators import action


class AnaliseDocumentoPrestacaoContaViewSet(mixins.UpdateModelMixin,
                                            mixins.RetrieveModelMixin,
                                            GenericViewSet):

    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = AnaliseDocumentoPrestacaoConta.objects.all()
    serializer_class = AnaliseDocumentoPrestacaoContaUpdateSerializer

    @action(detail=False, methods=['post'], url_path='limpar-status',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def limpar_status(self, request):
        uuids_analises_documentos = request.data.get('uuids_analises_documentos', None)

        response = AnaliseDocumentoPrestacaoContaService.limpar_status(
            uuids_analises_documentos=uuids_analises_documentos
        )
        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['post'], url_path='justificar-nao-realizacao',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def justificar_nao_realizacao(self, request):
        uuids_analises_documentos = request.data.get('uuids_analises_documentos', None)
        justificativa = request.data.get('justificativa', None)

        response = AnaliseDocumentoPrestacaoContaService.justificar_nao_realizacao(
            uuids_analises_documentos=uuids_analises_documentos,
            justificativa=justificativa
        )
        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['post'], url_path='marcar-como-realizado',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_como_realizado(self, request):
        uuids_analises_documentos = request.data.get('uuids_analises_documentos', None)

        response = AnaliseDocumentoPrestacaoContaService.marcar_como_realizado(
            uuids_analises_documentos=uuids_analises_documentos
        )
        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['get'], url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def tabelas(self, request):
        result = {
            "status_realizacao": AnaliseDocumentoPrestacaoConta.status_realizacao_choices_to_json(),
        }

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='marcar-como-credito-incluido',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def marcar_como_credito_incluido(self, request, uuid):
        uuid_credito_incluido = request.data.get('uuid_credito_incluido', None)

        response = AnaliseDocumentoPrestacaoContaService.marcar_como_credito_incluido(
            uuid_analise_documento=uuid,
            uuid_credito_incluido=uuid_credito_incluido
        )

        status_response = response.pop("status")

        return Response(response, status=status_response)
