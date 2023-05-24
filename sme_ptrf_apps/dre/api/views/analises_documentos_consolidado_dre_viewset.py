import logging

from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre,
    PermissaoAPIApenasSmeComLeituraOuGravacao,
)
from ...models.analise_documento_consolidado_dre import AnaliseDocumentoConsolidadoDre
from ...models.analise_consolidado_dre import AnaliseConsolidadoDre
from ..serializers.analise_documento_consolidado_dre_serializer import AnalisesDocumentosConsolidadoDreSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class AnalisesDocumentosConsolidadoDreViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = AnaliseDocumentoConsolidadoDre.objects.all()
    serializer_class = AnalisesDocumentosConsolidadoDreSerializer

    @action(detail=False, methods=['post'],
            url_path='gravar-acerto',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def gravar_acerto(self, request):

        from ...services.analise_documento_consolidado_dre_service import CriarAcerto

        analise_atual_consolidado_uuid = request.data.get('analise_atual_consolidado')
        tipo_documento = request.data.get('tipo_documento')
        documento_uuid = request.data.get('documento', None)
        detalhamento = request.data.get('detalhamento', None)

        if not analise_atual_consolidado_uuid or not tipo_documento or not documento_uuid or not detalhamento:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da analise atual, '
                            'o tipo de documento, o documento uuid e o detalhamento do acerto'
            }
            logger.info('Erro ao Gravar Acerto: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if tipo_documento not in ['RELATORIO_CONSOLIDADO', 'ATA_PARECER_TECNICO', 'DOCUMENTO_ADICIONAL']:
            erro = {
                'erro': 'tipo_de_documento_inválido',
                'mensagem': f'O tipo de documento {tipo_documento} é inválido as opções são: '
                            f'RELATORIO_CONSOLIDADO, ATA_PARECER_TECNICO ou DOCUMENTO_ADICIONAL'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_atual_consolidado = AnaliseConsolidadoDre.objects.get(uuid=analise_atual_consolidado_uuid)
        except (AnaliseConsolidadoDre.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto AnaliseConsolidadoDre para o uuid {analise_atual_consolidado_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        analise_documento = CriarAcerto(
            analise_atual_consolidado,
            tipo_documento,
            documento_uuid,
            detalhamento
        ).retorna_acerto_documento()

        if analise_documento:
            return Response(
                AnalisesDocumentosConsolidadoDreSerializer(analise_documento, many=False).data,
                status=status.HTTP_200_OK
            )
        else:
            erro = {
                'erro': 'erro_ao_gravar_acerto',
                'mensagem': f"Não foi possível gravar o acerto para o Documento {documento_uuid} Tipo de Documento {tipo_documento}"
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'],
            url_path='marcar-como-correto',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def marcar_como_correto(self, request):

        from ...services.analise_documento_consolidado_dre_service import MarcarComoCorreto

        analise_atual_consolidado_uuid = request.data.get('analise_atual_consolidado')
        documentos = request.data.get('documentos')

        if not analise_atual_consolidado_uuid or not documentos:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da analise atual, '
                            'os uuids dos documentos e tipos dos documentos'
            }
            logger.info('Erro ao Marcar Como Correto: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_atual_consolidado = AnaliseConsolidadoDre.objects.get(uuid=analise_atual_consolidado_uuid)
        except (AnaliseConsolidadoDre.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto AnaliseConsolidadoDre para o uuid {analise_atual_consolidado_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        response = MarcarComoCorreto(
            analise_atual_consolidado=analise_atual_consolidado,
            documentos=documentos
        ).retorna_documentos_marcados_como_correto()

        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['patch'],
            url_path='marcar-como-nao-conferido',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def marcar_como_nao_conferido(self, request):
        from ...services.analise_documento_consolidado_dre_service import MarcarComoNaoConferido

        analise_atual_consolidado_uuid = request.data.get('analise_atual_consolidado')
        uuids_analises_documentos = request.data.get('uuids_analises_documentos')

        if not analise_atual_consolidado_uuid or not uuids_analises_documentos:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da analise atual, '
                            'os uuids das analises de documentos'
            }
            logger.info('Erro ao Marcar Como Não Conferido: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_atual_consolidado = AnaliseConsolidadoDre.objects.get(uuid=analise_atual_consolidado_uuid)
        except (AnaliseConsolidadoDre.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto AnaliseConsolidadoDre para o uuid {analise_atual_consolidado_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        response = MarcarComoNaoConferido(
            analise_atual_consolidado=analise_atual_consolidado,
            uuids_analises_documentos=uuids_analises_documentos
        ).retorna_documentos_nao_conferidos()

        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, methods=['get'],
            url_path='download-documento',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao])
    def download_documento(self, request):

        from ...services.analise_documento_consolidado_dre_service import DownloadDocumento

        documento_uuid = request.query_params.get('documento_uuid')
        tipo_documento = request.query_params.get('tipo_documento')

        if not documento_uuid or not tipo_documento:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid e o tipo de documento'
            }
            logger.info('Erro ao Marcar Como Correto: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if tipo_documento not in ['RELATORIO_CONSOLIDADO', 'ATA_PARECER_TECNICO']:
            erro = {
                'erro': 'tipo_de_documento_inválido',
                'mensagem': f'O tipo de documento {tipo_documento} é inválido as opções são: '
                            f'RELATORIO_CONSOLIDADO ou ATA_PARECER_TECNICO '
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        response = DownloadDocumento(
            documento_uuid=documento_uuid,
            tipo_documento=tipo_documento
        ).retorna_download_documento()

        if response:
            return response
        else:
            erro = {
                'erro': 'erro_ao_efetuar_download',
                'mensagem': f"Não foi efetuar o Download do Documento {documento_uuid} Tipo de Documento {tipo_documento}"
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)
