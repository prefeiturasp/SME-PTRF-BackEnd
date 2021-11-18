import logging
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta
from sme_ptrf_apps.core.models.periodo import Periodo
from django.core.exceptions import ValidationError
from sme_ptrf_apps.core.tasks import gerar_arquivo_ata_async

from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoAPITodosComLeituraOuGravacao

from ....utils.choices_to_json import choices_to_json
from ...models import Ata
from ..serializers import AtaSerializer, AtaCreateSerializer

from django.http import HttpResponse

logger = logging.getLogger(__name__)


class AtasViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Ata.objects.all()
    serializer_class = AtaSerializer

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return AtaCreateSerializer
        else:
            return AtaSerializer

    @action(detail=False, methods=['get'], url_path='gerar-arquivo-ata',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def gerar_arquivo_ata(self, request):

        prestacao_de_contas_uuid = request.query_params.get('prestacao-de-conta-uuid')
        ata_uuid = request.query_params.get('ata-uuid')

        if not prestacao_de_contas_uuid or not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da prestação de contas e o uuid da ata.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            prestacao_de_contas = PrestacaoConta.by_uuid(prestacao_de_contas_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto prestação de contas para o uuid {prestacao_de_contas_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ata = Ata.by_uuid(ata_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        gerar_arquivo_ata_async.delay(
            prestacao_de_contas_uuid=prestacao_de_contas_uuid,
            ata_uuid=ata_uuid,
            usuario=request.user.username,
        )

        return Response({'mensagem': 'Arquivo na fila para processamento.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='download-arquivo-ata',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def download_arquivo_ata(self, request):
        ata_uuid = request.query_params.get('ata-uuid')

        if not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da ata.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ata = Ata.by_uuid(ata_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            filename = 'ata.pdf'
            response = HttpResponse(
                open(ata.arquivo_pdf.path, 'rb'),
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

    @action(detail=False, url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def tabelas(self, request):

        result = {
            'tipos_ata': choices_to_json(Ata.ATA_CHOICES),
            'tipos_reuniao': choices_to_json(Ata.REUNIAO_CHOICES),
            'convocacoes': choices_to_json(Ata.CONVOCACAO_CHOICES),
            'pareceres': choices_to_json(Ata.PARECER_CHOICES),
        }

        return Response(result)
