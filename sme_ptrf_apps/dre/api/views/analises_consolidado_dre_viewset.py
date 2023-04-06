import logging

from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from sme_ptrf_apps.users.permissoes import PermissaoApiDre, PermissaoAPIApenasDreComLeituraOuGravacao
from ...models.analise_consolidado_dre import AnaliseConsolidadoDre
from ..serializers.analise_consolidado_dre_serializer import AnaliseConsolidadoDreRetriveSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from sme_ptrf_apps.sme.tasks import gerar_relatorio_devolucao_acertos_async
from django.http import HttpResponse


logger = logging.getLogger(__name__)


class AnalisesConsolidadoDreViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = AnaliseConsolidadoDre.objects.all()
    serializer_class = AnaliseConsolidadoDreRetriveSerializer

    @action(detail=False, methods=['get'], url_path='previa-relatorio-devolucao-acertos',
            permission_classes=[IsAuthenticated & PermissaoApiDre])
    def previa_relatorio_devolucao_acertos(self, request):
        from sme_ptrf_apps.dre.api.validation_serializers.analise_consolidado_dre_serializer \
            import AnaliseConsolidadoDreSerializer

        query = AnaliseConsolidadoDreSerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)

        analise_consolidado_uuid = self.request.query_params.get('analise_consolidado_uuid')

        gerar_relatorio_devolucao_acertos_async.delay(
            analise_consolidado_uuid=analise_consolidado_uuid,
            username=request.user.username,
            previa=True
        )

        return Response({'mensagem': 'Arquivo na fila para processamento.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='status-info_relatorio_devolucao_acertos',
            permission_classes=[IsAuthenticated & PermissaoApiDre])
    def status_info_relatorio_devolucao_acertos(self, request):
        from sme_ptrf_apps.dre.api.validation_serializers.analise_consolidado_dre_serializer \
            import AnaliseConsolidadoDreSerializer

        query = AnaliseConsolidadoDreSerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)

        analise_consolidado_uuid = self.request.query_params.get('analise_consolidado_uuid')
        analise_consolidado = AnaliseConsolidadoDre.by_uuid(analise_consolidado_uuid)

        return Response(analise_consolidado.get_status_relatorio_devolucao_acertos())

    @action(detail=False, methods=['get'], url_path='download-documento-pdf_devolucao_acertos',
            permission_classes=[IsAuthenticated & PermissaoApiDre])
    def download_documento_pdf_devolucao_acertos(self, request):
        from sme_ptrf_apps.dre.api.validation_serializers.analise_consolidado_dre_serializer \
            import AnaliseConsolidadoDreSerializer

        query = AnaliseConsolidadoDreSerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)

        analise_consolidado_uuid = self.request.query_params.get('analise_consolidado_uuid')
        analise_consolidado = AnaliseConsolidadoDre.by_uuid(analise_consolidado_uuid)

        try:
            filename = 'relatorio_devolucao_acertos.pdf'
            response = HttpResponse(
                open(analise_consolidado.relatorio_acertos_pdf.path, 'rb'),
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
