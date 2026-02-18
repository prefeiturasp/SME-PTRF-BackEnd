import logging
import mimetypes
from django.http import FileResponse
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from drf_spectacular.utils import extend_schema, OpenApiTypes

from sme_ptrf_apps.paa.api.serializers import ModeloCargaPaaSerializer
from sme_ptrf_apps.paa.models import ModeloCargaPaa

logger = logging.getLogger(__name__)


class ModelosCargasPaaViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = "tipo_carga"
    queryset = ModeloCargaPaa.objects.all().order_by('-criado_em')
    serializer_class = ModeloCargaPaaSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filterset_fields = ('tipo_carga', )
    http_method_names = ['get',]

    @extend_schema(
        responses={
            (200, 'application/octet-stream'): OpenApiTypes.BINARY,
        },
        description="Retorna um arquivo."
    )
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, tipo_carga=None):
        logger.info("Download do modelo de arquivo de carga to tipo %s.", tipo_carga)

        if not tipo_carga:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o tipo_carga do Modelo de Carga.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        modelo = ModeloCargaPaa.objects.filter(tipo_carga=tipo_carga).first()
        if not modelo:
            logger.info("Modelo do tipo de carga %s não encontrado.", tipo_carga)
            erro = {
                'erro': 'modelo_nao_encontrado',
                'mensagem': f"Modelo do tipo de carga {tipo_carga} não encontrado."
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        logger.info("Retornando dados do modelo de carga: %s", modelo.arquivo.path)
        try:
            file_path = modelo.arquivo.path
            filename = modelo.arquivo.name
            content_type, _ = mimetypes.guess_type(filename)
            content_type = content_type or 'application/octet-stream'
            response = FileResponse(
                open(file_path, 'rb'),
                content_type=content_type,
                as_attachment=True,
                filename=filename,
            )
        except Exception as err:
            erro = {
                'erro': 'arquivo_nao_gerado',
                'mensagem': str(err)
            }
            logger.info("Erro: %s", str(err))
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        return response
