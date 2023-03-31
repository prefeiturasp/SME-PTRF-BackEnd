from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre,
    PermissaoAPIApenasDreComLeituraOuGravacao, PermissaoAPITodosComGravacao
)

from sme_ptrf_apps.dre.models import AtaParecerTecnico, ConsolidadoDRE
from sme_ptrf_apps.dre.models import ParametrosDre
from sme_ptrf_apps.core.models import Unidade, Periodo
import logging
from sme_ptrf_apps.dre.api.serializers.ata_parecer_tecnico_serializer import (
    AtaParecerTecnicoSerializer,
    AtaParecerTecnicoCreateSerializer,
    AtaParecerTecnicoLookUpSerializer
)
from ...services import (
    informacoes_execucao_financeira_unidades_ata_parecer_tecnico_consolidado_dre
)
from django.core.exceptions import ValidationError

from ...tasks import gerar_arquivo_ata_parecer_tecnico_async

from django.http import HttpResponse

logger = logging.getLogger(__name__)


class AtaParecerTecnicoViewset(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = AtaParecerTecnico.objects.all()
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    serializer_class = AtaParecerTecnicoSerializer

    def get_serializer_class(self):
        if self.action == 'partial_update' or self.action == 'create':
            return AtaParecerTecnicoCreateSerializer
        else:
            return AtaParecerTecnicoSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated, PermissaoAPIApenasDreComLeituraOuGravacao],
            url_path='gerar-ata-parecer-tecnico')
    def gerar_ata_parecer_tecnico(self, request):
        logger.info("Iniciando geração da Ata de Parecer Técnico")

        ata_uuid = request.query_params.get('ata')
        dre_uuid = request.query_params.get('dre')
        periodo_uuid = request.query_params.get('periodo')

        if not ata_uuid or not dre_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da Ata, o uuid da Dre e o uuid do Período'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ata = AtaParecerTecnico.objects.get(uuid=ata_uuid)
        except (ValidationError, Exception):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except (ValidationError, Exception):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.filter(uuid=periodo_uuid).get()
        except (ValidationError, Exception):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto periodo para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        gerar_arquivo_ata_parecer_tecnico_async.delay(
            ata_uuid=ata_uuid,
            dre_uuid=dre_uuid,
            periodo_uuid=periodo_uuid,
            usuario=request.user.username,
        )
        return Response({'mensagem': 'Arquivo na fila para processamento.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='download-ata-parecer-tecnico',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def download_ata_parecer_tecnico(self, request):
        logger.info("Download da Ata de Parecer Técnico.")

        ata_uuid = request.query_params.get('ata')

        if not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da Ata.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ata = AtaParecerTecnico.objects.get(uuid=ata_uuid)
        except (ValidationError, Exception):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            filename = 'ata_parecer_tecnico.pdf'
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

    @action(detail=False, url_path='membros-comissao-exame-contas',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def membros_comissao_exame_contas(self, request):
        dre_uuid = self.request.query_params.get('dre')
        ata_uuid = request.query_params.get('ata')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except Unidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da ata e o identificador.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            valida_ata = AtaParecerTecnico.by_uuid(ata_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        ata = AtaParecerTecnico.objects.filter(uuid=ata_uuid).first()
        comissoes = ParametrosDre.get().comissao_exame_contas
        membros = comissoes.membros.filter(dre=dre).values("uuid", "rf", "nome", "cargo")

        lista = []
        for membro in membros:
            dado = {
                "ata": f"{ata.uuid}",
                "uuid": membro["uuid"],
                "rf": membro["rf"],
                "nome": membro["nome"],
                "cargo": membro["cargo"],
                "editavel": False
            }

            lista.append(dado)

        return Response(lista)

    @action(detail=False, url_path='info-ata',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def info_ata(self, request):
        # Determina a DRE
        dre_uuid = self.request.query_params.get('dre')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-execucao-financeira-unidades',
                'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except Unidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-execucao-financeira-unidades',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        ata_uuid = self.request.query_params.get('ata')
        ata_de_parecer_tecnico = None
        if ata_uuid:
            try:
                ata_de_parecer_tecnico = AtaParecerTecnico.objects.get(uuid=ata_uuid)
            except AtaParecerTecnico.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto Ata de Parecer Técnico para o uuid {ata_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        info = informacoes_execucao_financeira_unidades_ata_parecer_tecnico_consolidado_dre(dre=dre, periodo=periodo, ata_de_parecer_tecnico=ata_de_parecer_tecnico)

        return Response(info)

