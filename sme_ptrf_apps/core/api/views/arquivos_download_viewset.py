from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from ...models import ArquivoDownload
from ..serializers.arquivos_download_serializer import ArquivoDownloadSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from ....utils.choices_to_json import choices_to_json
from rest_framework import status
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter, SearchFilter
import mimetypes
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated


class ArquivosDownloadViewSet(mixins.ListModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.DestroyModelMixin,
                              GenericViewSet):

    queryset = ArquivoDownload.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ArquivoDownloadSerializer
    lookup_field = 'uuid'
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('status', 'lido', )

    def get_queryset(self):
        user = self.request.user
        qs = ArquivoDownload.objects.filter(usuario=user).order_by("-criado_em")

        ultima_atualizacao = self.request.query_params.get('ultima_atualizacao')
        if ultima_atualizacao is not None:
            qs = qs.filter(alterado_em__contains=ultima_atualizacao)

        identificador = self.request.query_params.get('identificador')
        if identificador is not None:
            qs = qs.filter(identificador__unaccent__icontains=identificador)

        return qs

    @action(detail=False, methods=['get'], url_path='status')
    def get_status(self, request):
        return Response(choices_to_json(ArquivoDownload.STATUS_CHOICES))

    @action(detail=False, methods=['put'], url_path='marcar-lido')
    def marcar_como_lido_nao_lido(self, request):
        dado = self.request.data

        if not dado['uuid'] and dado['lido']:
            resultado = {
                'erro': 'Dados incompletos',
                'mensagem': 'uuid do arquivo para download e marcação de lido ou não são obrigatórios.'
            }

            status_code = status.HTTP_400_BAD_REQUEST
            return Response(resultado, status=status_code)

        try:
            arquivo_download = ArquivoDownload.objects.filter(uuid=dado['uuid']).first()
            arquivo_download.lido = dado['lido']
            arquivo_download.save()
        except Exception as err:
            resultado = {
                'erro': 'Erro ao realizar atualização',
                'mensagem': str(err)
            }

            status_code = status.HTTP_400_BAD_REQUEST
            return Response(resultado, status=status_code)

        resultado = {
            'mensagem': 'Arquivo atualizado com sucesso'
        }
        status_code = status.HTTP_200_OK

        return Response(resultado, status=status_code)

    @action(detail=False, methods=['get'], url_path='quantidade-nao-lidos')
    def quantidade_de_nao_lidos(self, request):
        user = self.request.user
        quantidade_nao = ArquivoDownload.objects.filter(
            usuario=user).filter(lido=False).exclude(status="EM_PROCESSAMENTO").count()
        data = {
            "quantidade_nao_lidos": quantidade_nao
        }
        return Response(data)

    @action(detail=False, methods=['get'], url_path='download-arquivo')
    def download_arquivo(self, request):
        arquivo_download_uuid = request.query_params.get('arquivo_download_uuid')

        if not arquivo_download_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do arquivo.'
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            arquivo_download = ArquivoDownload.by_uuid(arquivo_download_uuid)
        except ArquivoDownload.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto do arquivo para o uuid {arquivo_download_uuid} não foi encontrado na base."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if arquivo_download and arquivo_download.arquivo and arquivo_download.arquivo.name:
            arquivo_nome = arquivo_download.arquivo.name
            arquivo_path = arquivo_download.arquivo.path
            arquivo_file_mime = mimetypes.guess_type(arquivo_download.arquivo.name)[0]

            try:
                response = HttpResponse(
                    open(arquivo_path, 'rb'),
                    content_type=arquivo_file_mime
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % arquivo_nome
            except Exception as err:
                erro = {
                    'erro': 'arquivo_nao_gerado',
                    'mensagem': str(err)
                }
                return Response(erro, status=status.HTTP_404_NOT_FOUND)

            return response
        else:
            erro = {
                'erro': 'arquivo_nao_encontrado',
                'mensagem': 'Arquivo não encontrado'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)



