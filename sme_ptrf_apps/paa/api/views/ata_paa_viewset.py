"""
Módulo de API para gerenciamento dos recursos da Ata PAA.

Este módulo concentra os endpoints de iniciar ata do PAA, download do arquivo
final e da previa, listagem das tabelas e gerar ata final.
"""
import logging

from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response, Serializer
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet
from rest_framework import status

from django.core.exceptions import ValidationError
from django.http import HttpResponse

from waffle.mixins import WaffleFlagMixin

from drf_spectacular.utils import extend_schema_view

from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoAPITodosComLeituraOuGravacao
from sme_ptrf_apps.utils.choices_to_json import choices_to_json
from sme_ptrf_apps.paa.models import AtaPaa, Paa
from sme_ptrf_apps.paa.api.serializers.ata_paa_serializer import (
    AtaPaaSerializer, AtaPaaCreateSerializer, AtaPaaLookUpSerializer)
from sme_ptrf_apps.paa.services.ata_paa_service import validar_geracao_ata_paa
from sme_ptrf_apps.paa.tasks.gerar_ata_paa import gerar_ata_paa_async
from sme_ptrf_apps.paa.tasks.gerar_ata_paa_retificacao import gerar_ata_paa_retificacao_async
from .docs.ata_paa_docs import DOCS

from sme_ptrf_apps.paa.mixins.paa_bloqueia_alteracao_mixin import PaaBloqueiaAlteracaoMixin
from sme_ptrf_apps.paa.services.paa_status_bloqueia_alteracao_service import TipoBloqueioPaa

logger = logging.getLogger(__name__)

ERROR_OBJETO_NAO_ENCONTRADO = "Objeto não encontrado."


@extend_schema_view(**DOCS)
class AtaPaaViewSet(WaffleFlagMixin,
                    PaaBloqueiaAlteracaoMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    GenericViewSet):
    """
    ViewSet responsável pelo gerenciamento dos recursos da Ata PAA

    Disponibiliza operações de iniciar ata do PAA, download do arquivo
    final e da previa, listagem das tabelas e gerar ata final.
    """
    waffle_flag = "paa"
    tipo_bloqueio_paa = TipoBloqueioPaa.ATA_CONCLUIDA
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = AtaPaa.objects.all()
    serializer_class = AtaPaaSerializer

    def get_serializer_class(self) -> type[Serializer]:
        """
        Retorne o serializer apropriado para a ação executada.

        Utiliza o serializer AtaPaaCreateSerializer para a ação de atualização
        parcial e o serializer AtaPaaSerializer para as demais ações.

        Returns:
            Serializer: Classe do serializer correspondente à ação atual.
        """
        if self.action == 'partial_update':
            return AtaPaaCreateSerializer
        else:
            return AtaPaaSerializer

    @action(detail=False, methods=['get', 'post'], url_path='iniciar-ata',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def iniciar_ata(self, request: Request) -> Response:
        """
        Inicie uma nova Ata PAA.

        Args:
            request: O objeto de requisição HTTP atual.
            paa_uuid: UUID do PAA.

        Returns:
            Uma resposta indicando o sucesso ou fracasso da operação.
        """
        paa_uuid = request.query_params.get('paa_uuid')

        if not paa_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário informar o uuid do PAA. ?paa_uuid=uuid_do_paa'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            paa = Paa.objects.get(uuid=paa_uuid)
        except Paa.DoesNotExist:
            erro = {
                'erro': ERROR_OBJETO_NAO_ENCONTRADO,
                'mensagem': f"O objeto PAA para o uuid {paa_uuid} não foi encontrado na base."
            }
            logger.info('Erro iniciar_ata.nao_encontrado: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        ata_paa = AtaPaa.iniciar(paa=paa)

        if request.method == 'GET':
            return Response(AtaPaaLookUpSerializer(ata_paa, many=False).data, status=status.HTTP_200_OK)
        else:
            return Response(AtaPaaSerializer(ata_paa, many=False).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='download-arquivo-ata-paa',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def download_arquivo_ata_paa(self, request: Request) -> Response:
        """
        Baixe o arquivo da Ata PAA.

        Args:
            request: O objeto de requisição HTTP atual.
            ata_paa_uuid: UUID da Ata PAA.

        Returns:
            O arquivo da Ata PAA.
        """
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
                'erro': ERROR_OBJETO_NAO_ENCONTRADO,
                'mensagem': f"O objeto ata PAA para o uuid {ata_paa_uuid} não foi encontrado na base."
            }
            logger.info('Erro download_arquivo_ata_paa.nao_encontrado: %r', erro)
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
            logger.info("Erro download_arquivo_ata_paa.arquivo_nao_gerado: %s", str(err))
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        return response

    @action(detail=False, url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def tabelas(self, request: Request) -> Response:
        """
        Retorne as tabelas de referência para a Ata PAA.
        """
        result = {
            'tipos_ata': choices_to_json(AtaPaa.ATA_CHOICES),
            'tipos_reuniao': choices_to_json(AtaPaa.REUNIAO_CHOICES),
            'convocacoes': choices_to_json(AtaPaa.CONVOCACAO_CHOICES),
            'pareceres': choices_to_json(AtaPaa.PARECER_CHOICES),
        }

        return Response(result)

    @action(detail=False, methods=['post'], url_path='gerar-ata',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def gerar_ata(self, request: Request) -> Response:
        """
        Endpoint para gerar a ata PAA final
        """
        paa_uuid = request.data.get('paa_uuid')

        if not paa_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário informar o uuid do PAA.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            paa = Paa.objects.get(uuid=paa_uuid)
        except Paa.DoesNotExist:
            erro = {
                'erro': ERROR_OBJETO_NAO_ENCONTRADO,
                'mensagem': f"O objeto PAA para o uuid {paa_uuid} não foi encontrado na base."
            }
            logger.exception('Erro gerar_ata.paa_nao_encontrado: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        eh_retificacao = paa.status_em_retificacao
        tipo_ata = AtaPaa.ATA_RETIFICACAO if eh_retificacao else AtaPaa.ATA_APRESENTACAO

        qs = AtaPaa.objects.filter(paa=paa, tipo_ata=tipo_ata)
        # Retificação permite regerar — não exclui atas já concluídas.
        # Usa order_by('-pk').first() pois pode haver múltiplos registros (um por ciclo Rn).
        if not eh_retificacao:
            qs = qs.exclude(status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)
        ata_paa = qs.order_by('-pk').first()
        if not ata_paa:
            erro = {
                'erro': ERROR_OBJETO_NAO_ENCONTRADO,
                'mensagem': "Ata PAA não encontrada. Verifique se a Ata PAA já foi gerada."
            }
            logger.exception('Erro gerar_ata.ata_nao_encontrada: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Valida se pode gerar
        validacao = validar_geracao_ata_paa(ata_paa)

        if not validacao.get('is_valid'):
            return Response(
                {
                    'mensagem': validacao.get('mensagem'),
                    'confirmar': False
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verifica confirmação
        confirmar = bool(int(request.data.get('confirmar', 0)))
        if not confirmar:
            return Response(
                {
                    'mensagem': 'É necessário confirmar a geração da ata.',
                    'confirmar': True
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Inicia a geração assíncrona com a task correspondente ao tipo
        try:
            task = gerar_ata_paa_retificacao_async if eh_retificacao else gerar_ata_paa_async
            task.apply_async(args=[str(ata_paa.uuid), request.user.username])

            logger.info(f'Geração da ata PAA {ata_paa.uuid} iniciada pelo usuário {request.user.username}')

            return Response(
                {
                    'mensagem': 'Geração da ata final iniciada. Aguarde o processamento.',
                    'status': 'EM_PROCESSAMENTO'
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(f'Erro gerar_ata.erro_iniciar_geracao_ata: {str(e)}')
            erro = {
                'erro': 'erro_ao_iniciar_geracao',
                'mensagem': f'Erro ao iniciar a geração da ata: {str(e)}'
            }
            return Response(erro, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
