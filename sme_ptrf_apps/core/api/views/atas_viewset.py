import logging

from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse, OpenApiExample)

from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta
from sme_ptrf_apps.core.services.ata_service import validar_campos_ata
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

    @extend_schema(
        parameters=[
            OpenApiParameter(name='associacao_uuid', description='UUID da Associação', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='periodo_uuid', description='UUID do Período', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='conta-associacao', description='UUID da Conta da Associação', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiResponse(
            response={
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        "nome_fornecedor": {"type": "string"},
                        "cpf_cnpj_fornecedor": {"type": "string"},
                        "tipo_documento": {"type": "string"},
                        "numero_documento": {"type": "string"},
                        "data_documento": {"type": "string"},
                        "tipo_transacao": {"type": "string"},
                        "data_transacao": {"type": "string"},
                        "valor_total": {"type": "integer"},
                        "motivos_pagamento_antecipado": {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    "motivo": {"type": "string"},
                                }
                            }
                        },
                        "outros_motivos_pagamento_antecipado": {"type": "string"},
                    },
                }
            }
        )},
    )
    @action(detail=False, methods=['get'], url_path='ata-despesas-com-pagamento-antecipado',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def ata_despesas_com_pagamento_antecipado(self, request):

        from ...services.ata_dados_service import get_despesas_com_pagamento_antecipado

        ata_uuid = request.query_params.get('ata-uuid')

        if not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid ata.'
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

        despesas_com_pagamento_antecipado = get_despesas_com_pagamento_antecipado(ata)

        return Response(despesas_com_pagamento_antecipado, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='prestacao-de-conta-uuid', description='UUID da prestação de contas', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='ata-uuid', description='UUID da ata', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: 'Arquivo na fila para processamento.'},
        examples=[
            OpenApiExample(
                'Resposta',
                value={'mensagem': 'Arquivo na fila para processamento.'}
            )
        ],
        description='Envia demonstrativo financeiro para processamento.'
    )
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
            PrestacaoConta.by_uuid(prestacao_de_contas_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': (
                    f"O objeto prestação de contas para o uuid {prestacao_de_contas_uuid} não foi encontrado na base.")
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

        ata_valida = validar_campos_ata(ata)
        if not ata_valida['is_valid']:
            return Response({
                'campos_invalidos': ata_valida['campos']},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        gerar_arquivo_ata_async.delay(
            prestacao_de_contas_uuid=prestacao_de_contas_uuid,
            ata_uuid=ata_uuid,
            usuario=request.user.username,
        )

        return Response({
            'mensagem': 'Arquivo na fila para processamento.'},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(name='ata-uuid', description='UUID da ata', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={
            (200, 'application/pdf'): OpenApiTypes.BINARY,
        },
        description="Retorna um arquivo PDF - Ata."
    )
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
            'tipos_ata': choices_to_json(Ata.ATA_CHOICES),
            'tipos_reuniao': choices_to_json(Ata.REUNIAO_CHOICES),
            'convocacoes': choices_to_json(Ata.CONVOCACAO_CHOICES),
            'pareceres': choices_to_json(Ata.PARECER_CHOICES),
        }

        return Response(result)
