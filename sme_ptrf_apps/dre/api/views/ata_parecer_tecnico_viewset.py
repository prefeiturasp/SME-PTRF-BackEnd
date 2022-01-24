from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre,
    PermissaoAPIApenasDreComLeituraOuGravacao
)

from sme_ptrf_apps.dre.models import AtaParecerTecnico
from sme_ptrf_apps.dre.models import ParametrosDre
from sme_ptrf_apps.core.models import Unidade, PrestacaoConta, TipoConta, Periodo
import logging
from sme_ptrf_apps.dre.api.serializers.ata_parecer_tecnico_serializer import (
    AtaParecerTecnicoSerializer,
    AtaParecerTecnicoCreateSerializer,
    AtaParecerTecnicoLookUpSerializer
)
from ...services import (
    informacoes_execucao_financeira_unidades_ata_parecer_tecnico
)
from django.core.exceptions import ValidationError

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

        info = informacoes_execucao_financeira_unidades_ata_parecer_tecnico(dre=dre, periodo=periodo)

        return Response(info)


    @action(detail=False, methods=['get'], url_path='status-ata',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def status_ata(self, request):
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

        ata = AtaParecerTecnico.objects.filter(dre=dre).filter(periodo=periodo).last()

        if not ata:
            erro = {
                'mensagem': 'Ainda não existe uma ata de parecer tecnico para essa DRE.'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        return Response(AtaParecerTecnicoLookUpSerializer(ata, many=False).data,
                        status=status.HTTP_200_OK)

