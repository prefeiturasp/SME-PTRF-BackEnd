import logging

from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.sme.tasks import exportar_materiais_e_servicos_async, \
    exportar_receitas_async, exportar_saldos_finais_periodo_async, exportar_relacao_bens_async, \
    exportar_status_prestacoes_contas_async, exportar_devolucoes_ao_tesouro_async, exportar_rateios_async
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
        url_path='status-prestacoes-contas',
        permission_classes=permission_classes
    )
    def status_prestacoes_contas(self, request):
        exportar_status_prestacoes_contas_async.delay(
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
    @action(
        detail=False, methods=['get'],
        url_path='devolucao-ao-tesouro-prestacoes-contas',
        permission_classes=permission_classes
    )
    def devolucao_ao_tesouro_prestacao_conta(self, request):
        exportar_devolucoes_ao_tesouro_async.delay(
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
        url_path='rateios',
        permission_classes=permission_classes
    )
    def rateios(self, request):
        exportar_rateios_async.delay(
            data_inicio=request.query_params.get('data_inicio'),
            data_final=request.query_params.get('data_final'),
            username=request.user.username
        )

        return Response(
            {'response': "Arquivo gerado com sucesso, enviado para a central de download"},
            status=HTTP_201_CREATED
        )
