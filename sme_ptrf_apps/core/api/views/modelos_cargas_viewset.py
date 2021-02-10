import logging

from django.http import HttpResponse
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sme_ptrf_apps.core.api.serializers import ModeloCargaSerializer
from sme_ptrf_apps.core.models import ModeloCarga

logger = logging.getLogger(__name__)


class ModelosCargasViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = "tipo_carga"
    queryset = ModeloCarga.objects.all().order_by('-criado_em')
    serializer_class = ModeloCargaSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filter_fields = ('tipo_carga', )

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, tipo_carga=None):
        logger.info("Download do modelo de arquivo de carga to tipo %s.", tipo_carga)

        if not tipo_carga:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o tipo_carga do Modelo de Carga.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        modelo = ModeloCarga.objects.filter(tipo_carga=tipo_carga).first()
        if not modelo:
            logger.info("Modelo do tipo de carga %s não encontrado.", tipo_carga)
            erro = {
                'erro': 'modelo_nao_encontrado',
                'mensagem': f"Modelo do tipo de carga {tipo_carga} não encontrado."
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        logger.info("Retornando dados do modelo de carga: %s", modelo.arquivo.path)
        filename = modelo.arquivo.name
        try:
            response = HttpResponse(
                open(modelo.arquivo.path, 'rb'),
                content_type='text/csv'
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
