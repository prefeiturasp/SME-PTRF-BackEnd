import logging

from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.sme.tasks import exportar_materiais_e_servicos_async, \
    exportar_receitas_async, exportar_saldos_finais_periodo_async, exportar_relacao_bens_async
from sme_ptrf_apps.users.permissoes import PermissaoAPIApenasSmeComLeituraOuGravacao


logger = logging.getLogger(__name__)


class ExportacoesDadosViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao]
    lookup_field = 'uuid'
    queryset = ArquivoDownload.objects.all()

    @action(
        detail=False, methods=['get'],
        url_path='creditos',
        permission_classes=permission_classes
        )
    def creditos(self, request):
        exportar_receitas_async.delay(
            data_inicio=request.query_params.get('data_inicio'),
            data_final=request.query_params.get('data_final'),
            username=request.user.username
        )

        return Response(
            {'response': "Arquivo gerado com sucesso, enviado para a central de download"},
            status=HTTP_201_CREATED
        )

    @action(
        detail=False, methods=['get'],
        url_path='materiais-e-servicos',
        permission_classes=permission_classes
        )
    def materiais_e_servicos(self, request):
        exportar_materiais_e_servicos_async.delay(
            data_inicio=request.query_params.get('data_inicio'),
            data_final=request.query_params.get('data_final'),
            username=request.user.username
        )

        return Response(
            {'response': "Arquivo gerado com sucesso, enviado para a central de download"},
            status=HTTP_201_CREATED
        )

    @action(
        detail=False, methods=['get'],
        url_path='saldos-finais-periodos',
        permission_classes=permission_classes
    )
    def saldos_finais_periodos(self, request):
        exportar_saldos_finais_periodo_async.delay(
            data_inicio=request.query_params.get('data_inicio'),
            data_final=request.query_params.get('data_final'),
            username=request.user.username
        )

        return Response(
            {'response': "Arquivo gerado com sucesso, enviado para a central de download"},
            status=HTTP_201_CREATED
        )

    @action(
        detail=False, methods=['get'],
        url_path='relacao-bens',
        permission_classes=permission_classes
    )
    def relacao_bens(self, request):
        exportar_relacao_bens_async.delay(
            data_inicio=request.query_params.get('data_inicio'),
            data_final=request.query_params.get('data_final'),
            username=request.user.username
        )

        return Response(
            {'response': "Arquivo gerado com sucesso, enviado para a central de download"},
            status=HTTP_201_CREATED
        )
