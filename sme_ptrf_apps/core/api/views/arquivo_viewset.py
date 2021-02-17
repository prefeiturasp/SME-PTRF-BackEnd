import logging

from django.db.models import Q
from django.http import HttpResponse
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sme_ptrf_apps.core.api.serializers import ArquivoSerializer
from sme_ptrf_apps.core.models import Arquivo
from sme_ptrf_apps.core.tasks import processa_carga_async

logger = logging.getLogger(__name__)


class ArquivoViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]
    lookup_field = "uuid"
    queryset = Arquivo.objects.all().order_by('-criado_em')
    serializer_class = ArquivoSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filter_fields = ('status', 'tipo_carga')

    def get_queryset(self):
        qs = Arquivo.objects.all()

        data_execucao = self.request.query_params.get('data_execucao')
        if data_execucao is not None:
            qs = qs.filter(ultima_execucao__date=data_execucao)

        identificador = self.request.query_params.get('identificador')
        if identificador is not None:
            qs = qs.filter(Q(identificador__unaccent__icontains=identificador))

        return qs

    @action(detail=False, methods=['get'], url_path='tabelas')
    def tabelas(self, _):
        result = {
            'status': Arquivo.status_to_json(),
            'tipos_cargas': Arquivo.tipos_cargas_to_json(),
            'tipos_delimitadores': Arquivo.delimitadores_to_json()
        }
        return Response(result)

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, uuid=None):
        logger.info("Download do arquivo de carga com uuid %s.", uuid)

        if not uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do Arquivo.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        arquivo = Arquivo.objects.filter(uuid=uuid).first()
        if not arquivo:
            logger.info("Arquivo com uuid %s não encontrado.", uuid)
            erro = {
                'erro': 'arquivo_nao_encontrado',
                'mensagem': f"Arquivo com uuid {uuid} não encontrado."
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        logger.info("Retornando dados do arquivo: %s", arquivo.conteudo.path)
        filename = arquivo.conteudo.name
        try:
            response = HttpResponse(
                open(arquivo.conteudo.path, 'rb'),
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

    @action(detail=True, methods=['post'], url_path='processar')
    def processar(self, request, uuid):
        logger.info("Processando arquivo de carga com uuid %s.", uuid)

        if not uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do Arquivo.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        arquivo = self.get_object()
        if not arquivo:
            logger.info("Arquivo com uuid %s não encontrado.", uuid)
            erro = {
                'erro': 'arquivo_nao_encontrado',
                'mensagem': f"Arquivo com uuid {uuid} não encontrado."
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        processa_carga_async.delay(uuid)

        return Response({'mensagem': 'Arquivo na fila para processamento.'}, status=status.HTTP_200_OK)
