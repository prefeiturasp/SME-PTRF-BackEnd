import logging

from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse)

from django.core.exceptions import ValidationError
from django.http import HttpResponse

from waffle.mixins import WaffleFlagMixin

from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoAPITodosComLeituraOuGravacao
from sme_ptrf_apps.utils.choices_to_json import choices_to_json
from sme_ptrf_apps.paa.models import AtaPaa
from sme_ptrf_apps.paa.api.serializers.ata_paa_serializer import AtaPaaSerializer, AtaPaaCreateSerializer


logger = logging.getLogger(__name__)


class AtaPaaViewSet(WaffleFlagMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    GenericViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = AtaPaa.objects.all()
    serializer_class = AtaPaaSerializer

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return AtaPaaCreateSerializer
        else:
            return AtaPaaSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='ata-paa-uuid', description='UUID da ata PAA', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={
            (200, 'application/pdf'): OpenApiTypes.BINARY,
        },
        description="Retorna um arquivo PDF - Ata PAA."
    )
    @action(detail=False, methods=['get'], url_path='download-arquivo-ata-paa',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def download_arquivo_ata_paa(self, request):
        ata_paa_uuid = request.query_params.get('ata-paa-uuid')

        if not ata_paa_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da ata PAA.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ata_paa = AtaPaa.by_uuid(ata_paa_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata PAA para o uuid {ata_paa_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            filename = 'ata-paa.pdf'
            response = HttpResponse(
                open(ata_paa.arquivo_pdf.path, 'rb'),
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

    @extend_schema(
        parameters=[],
        responses={200: OpenApiResponse(
            response={
                'type': 'object',
                'properties': {
                    "tipo_ata": {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {'id': {'type': 'string'}, 'nome': {'type': 'string'}}
                        },
                    },
                    "tipos_reuniao": {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {'id': {'type': 'string'}, 'nome': {'type': 'string'}}
                        },
                    },
                    "convocacoes": {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {'id': {'type': 'string'}, 'nome': {'type': 'string'}}
                        },
                    },
                    "pareceres": {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {'id': {'type': 'string'}, 'nome': {'type': 'string'}}
                        },
                    },
                },
            }
        )},
    )
    @action(detail=False, url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def tabelas(self, request):

        result = {
            'tipos_ata': choices_to_json(AtaPaa.ATA_CHOICES),
            'tipos_reuniao': choices_to_json(AtaPaa.REUNIAO_CHOICES),
            'convocacoes': choices_to_json(AtaPaa.CONVOCACAO_CHOICES),
            'pareceres': choices_to_json(AtaPaa.PARECER_CHOICES),
        }

        return Response(result)

