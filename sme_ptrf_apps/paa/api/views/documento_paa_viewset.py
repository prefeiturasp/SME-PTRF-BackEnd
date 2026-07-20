import logging

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet
from rest_framework import status

from django.http import HttpResponse

from drf_spectacular.utils import extend_schema_view

from sme_ptrf_apps.paa.models import DocumentoPaa


logger = logging.getLogger(__name__)


@extend_schema_view()
class DocumentoPaaViewSet(GenericViewSet):
    """
    ViewSet responsável pelo gerenciamento do documento PAA.

    Disponibiliza operações de download do arquivo PDF do documento PAA,
    permitindo a filtragem pelo uuid do documento.
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = DocumentoPaa.objects.all()

    @action(detail=True, methods=['get'], url_path='download',
            permission_classes=[IsAuthenticated])
    def download(self, request: Request, uuid: str | None = None):
        """
        Endpoint para fazer download do arquivo PDF do documento PAA

        URL Parameters:
            - uuid (required): UUID do documento PAA
        """
        documento_paa = self.get_object()

        try:
            if not documento_paa.arquivo_pdf:
                erro = {
                    'erro': 'arquivo_nao_gerado',
                    'mensagem': 'O arquivo PDF não foi gerado para este documento.'
                }
                logger.warning("Arquivo não encontrado para o documento PAA %s", documento_paa.uuid)
                return Response(erro, status=status.HTTP_404_NOT_FOUND)

            filename = 'documento-paa.pdf'
            response = HttpResponse(
                open(documento_paa.arquivo_pdf.path, 'rb'),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = 'attachment; filename=%s' % filename

        except Exception as err:
            erro = {
                'erro': 'arquivo_nao_gerado',
                'mensagem': str(err)
            }
            logger.error("Erro ao baixar documento PAA %s: %s", documento_paa.uuid, str(err))
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        return response
