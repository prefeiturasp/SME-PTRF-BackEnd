import logging

from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import status

from django.core.exceptions import ValidationError
from django.http import HttpResponse

from waffle.mixins import WaffleFlagMixin

from drf_spectacular.utils import extend_schema_view

from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoAPITodosComLeituraOuGravacao
from sme_ptrf_apps.utils.choices_to_json import choices_to_json
from sme_ptrf_apps.paa.models import AtaPaa, Paa
from sme_ptrf_apps.paa.api.serializers.ata_paa_serializer import AtaPaaSerializer, AtaPaaCreateSerializer, AtaPaaLookUpSerializer
from sme_ptrf_apps.paa.services.ata_paa_service import validar_geracao_ata_paa
from sme_ptrf_apps.paa.tasks.gerar_ata_paa import gerar_ata_paa_async
from .docs.ata_paa_docs import DOCS


logger = logging.getLogger(__name__)


@extend_schema_view(**DOCS)
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

    @action(detail=False, methods=['get', 'post'], url_path='iniciar-ata',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def iniciar_ata(self, request):
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
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto PAA para o uuid {paa_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        ata_paa = AtaPaa.iniciar(paa=paa)

        if request.method == 'GET':
            return Response(AtaPaaLookUpSerializer(ata_paa, many=False).data, status=status.HTTP_200_OK)
        else:
            return Response(AtaPaaSerializer(ata_paa, many=False).data, status=status.HTTP_200_OK)

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

    @action(detail=False, methods=['post'], url_path='gerar-ata',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def gerar_ata(self, request):
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
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto PAA para o uuid {paa_uuid} não foi encontrado na base."
            }
            logger.error('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ata_paa = AtaPaa.objects.get(
                paa=paa,
                tipo_ata=AtaPaa.ATA_APRESENTACAO
            )
        except AtaPaa.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"Ata PAA não encontrada para o PAA {paa_uuid}. É necessário criar a ata antes de gerar."
            }
            logger.error('Erro: %r', erro)
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

        # Inicia a geração assíncrona
        try:
            gerar_ata_paa_async.apply_async(
                args=[str(ata_paa.uuid), request.user.username]
            )
            
            logger.info(f'Geração da ata PAA {ata_paa.uuid} iniciada pelo usuário {request.user.username}')
            
            return Response(
                {
                    'mensagem': 'Geração da ata final iniciada. Aguarde o processamento.',
                    'status': 'EM_PROCESSAMENTO'
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f'Erro ao iniciar geração da ata PAA: {str(e)}', exc_info=True)
            erro = {
                'erro': 'erro_ao_iniciar_geracao',
                'mensagem': f'Erro ao iniciar a geração da ata: {str(e)}'
            }
            return Response(erro, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

