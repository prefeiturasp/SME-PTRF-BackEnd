import logging
from waffle import flag_is_active
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.sme.tasks import (
    exportar_associacoes_async,
    exportar_atas_async,
    exportar_documentos_despesas_async,
    exportar_materiais_e_servicos_async,
    exportar_receitas_async,
    exportar_saldos_finais_periodo_async,
    exportar_relacao_bens_async,
    exportar_status_prestacoes_contas_async,
    exportar_devolucoes_ao_tesouro_async,
    exportar_rateios_async,
    exportar_demonstativos_financeiros_async,
    exportar_dados_conta_async,
    exportar_repasses_async,
    exportar_dados_membros_apm_async,
    exportar_dados_membros_apm_legado_async,
    exportar_processos_sei_regularidade_async,
    exportar_processos_sei_prestacao_contas_async,
    exportar_unidades_async
)

from sme_ptrf_apps.users.permissoes import (
    PermissaoAPIApenasSmeComLeituraOuGravacao,
    PermissaoAPIApenasDreComLeituraOuGravacao,
)
from sme_ptrf_apps.sme.api.serializers import ExportacaoDadosSerializer


logger = logging.getLogger(__name__)


class ExportacoesDadosViewSet(GenericViewSet):
    permission_classes = [
        IsAuthenticated
        & (
            PermissaoAPIApenasSmeComLeituraOuGravacao
            | PermissaoAPIApenasDreComLeituraOuGravacao
        )
    ]
    lookup_field = "uuid"
    queryset = ArquivoDownload.objects.all()

    @action(
        detail=False,
        methods=["get"],
        url_path="demonstrativos-financeiros",
        permission_classes=permission_classes,
    )
    def demonstrativos_financeiros(self, request):
        exportar_demonstativos_financeiros_async.delay(
            data_inicio=request.query_params.get("data_inicio"),
            data_final=request.query_params.get("data_final"),
            username=request.user.username,
            dre_uuid=request.query_params.get("dre_uuid"),
        )

        return Response(
            {
                "response": "O arquivo está sendo gerado e será enviado para a central de download após conclusão."
            },
            status=HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="creditos",
        permission_classes=permission_classes,
    )
    def creditos(self, request):
        exportar_receitas_async.delay(
            data_inicio=request.query_params.get("data_inicio"),
            data_final=request.query_params.get("data_final"),
            username=request.user.username,
            dre_uuid=request.query_params.get("dre_uuid"),
        )

        return Response(
            {
                "response": "Arquivo gerado com sucesso, enviado para a central de download"
            },
            status=HTTP_201_CREATED,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='data_inicio',
                description='Filtro de início de data de criação',
                required=False,
                allow_blank=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='data_final',
                description='Filtro de fim de data de criação',
                required=False,
                allow_blank=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='dre_uui',
                description='Filtro de uuid de DRE',
                required=False,
                allow_blank=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
        description="parâmetros de URL",
        responses={200: "Success"},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="unidades",
        permission_classes=permission_classes,
    )
    def unidades(self, request):
        exportar_unidades_async.delay(
            data_inicio=request.query_params.get("data_inicio"),
            data_final=request.query_params.get("data_final"),
            username=request.user.username,
            dre_uuid=request.query_params.get("dre_uuid", None),
        )

        return Response(
            {
                "response": "Arquivo gerado com sucesso, enviado para a central de download"
            },
            status=HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="materiais-e-servicos",
        permission_classes=permission_classes,
    )
    def materiais_e_servicos(self, request):
        exportar_materiais_e_servicos_async.delay(
            data_inicio=request.query_params.get("data_inicio"),
            data_final=request.query_params.get("data_final"),
            username=request.user.username,
        )

        return Response(
            {
                "response": "Arquivo gerado com sucesso, enviado para a central de download"
            },
            status=HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="status-prestacoes-contas",
        permission_classes=permission_classes,
    )
    def status_prestacoes_contas(self, request):
        exportar_status_prestacoes_contas_async.delay(
            data_inicio=request.query_params.get("data_inicio"),
            data_final=request.query_params.get("data_final"),
            username=request.user.username,
            dre_uuid=request.query_params.get("dre_uuid"),
        )

        return Response(
            {
                "response": "Arquivo gerado com sucesso, enviado para a central de download"
            },
            status=HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="saldos-finais-periodos",
        permission_classes=permission_classes,
    )
    def saldos_finais_periodos(self, request):
        serializer = ExportacaoDadosSerializer(data=request.query_params)

        if serializer.is_valid():
            exportar_saldos_finais_periodo_async.delay(
                data_inicio=request.query_params.get("data_inicio"),
                data_final=request.query_params.get("data_final"),
                username=request.user.username,
                dre_uuid=request.query_params.get("dre_uuid"),
            )
        else:
            erro = {
                "erro": "Um ou mais parâmetros inválidos.",
                "mensagem": " ".join(
                    [message[0] for message in serializer.errors.values()]
                ),
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "response": "Arquivo gerado com sucesso, enviado para a central de download"
            },
            status=HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="relacao-bens",
        permission_classes=permission_classes,
    )
    def relacao_bens(self, request):
        exportar_relacao_bens_async.delay(
            data_inicio=request.query_params.get("data_inicio"),
            data_final=request.query_params.get("data_final"),
            username=request.user.username,
            dre_uuid=request.query_params.get("dre_uuid"),
        )

        return Response(
            {
                "response": "Arquivo gerado com sucesso, enviado para a central de download"
            },
            status=HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="devolucao-ao-tesouro-prestacoes-contas",
        permission_classes=permission_classes,
    )
    def devolucao_ao_tesouro_prestacao_conta(self, request):
        exportar_devolucoes_ao_tesouro_async.delay(
            data_inicio=request.query_params.get("data_inicio"),
            data_final=request.query_params.get("data_final"),
            username=request.user.username,
            dre_uuid=request.query_params.get("dre_uuid"),
        )

        return Response(
            {
                "response": "Arquivo gerado com sucesso, enviado para a central de download"
            },
            status=HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="rateios",
        permission_classes=permission_classes,
    )
    def rateios(self, request):
        exportar_rateios_async.delay(
            data_inicio=request.query_params.get("data_inicio"),
            data_final=request.query_params.get("data_final"),
            username=request.user.username,
            dre_uuid=request.query_params.get("dre_uuid"),
        )

        return Response(
            {
                "response": "Arquivo gerado com sucesso, enviado para a central de download"
            },
            status=HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="atas-prestacoes-contas",
        permission_classes=permission_classes,
    )
    def atas(self, request):
        exportar_atas_async.delay(
            data_inicio=request.query_params.get("data_inicio"),
            data_final=request.query_params.get("data_final"),
            username=request.user.username,
            dre_uuid=request.query_params.get("dre_uuid"),
        )

        return Response(
            {
                "response": "O arquivo está sendo gerado e será enviado para a central de download após conclusão."
            },
            status=HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="documentos-despesas",
        permission_classes=permission_classes,
    )
    def documentos_despesas(self, request):
        exportar_documentos_despesas_async.delay(
            data_inicio=request.query_params.get("data_inicio"),
            data_final=request.query_params.get("data_final"),
            username=request.user.username,
            dre_uuid=request.query_params.get("dre_uuid"),
        )

        return Response(
            {
                "response": "Arquivo gerado com sucesso, enviado para a central de download"
            },
            status=HTTP_201_CREATED,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="data_inicio",
                type=OpenApiTypes.DATE,
                description="Data de início",
                required=False,
            ),
            OpenApiParameter(
                name="data_final",
                type=OpenApiTypes.DATE,
                description="Data final",
                required=False,
            ),
        ]
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="contas-associacao",
        permission_classes=permission_classes,
    )
    def contas_associacao(self, request):
        exportar_dados_conta_async.delay(
            data_inicio=request.query_params.get("data_inicio"),
            data_final=request.query_params.get("data_final"),
            username=request.user.username,
            dre_uuid=request.query_params.get("dre_uuid"),
        )

        return Response(
            {
                "response": "O arquivo está sendo gerado e será enviado para a central de download após conclusão."
            },
            status=HTTP_201_CREATED,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="data_inicio",
                type=OpenApiTypes.DATE,
                description="Data de início",
                required=False,
            ),
            OpenApiParameter(
                name="data_final",
                type=OpenApiTypes.DATE,
                description="Data final",
                required=False,
            ),
        ]
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="repasses",
        permission_classes=permission_classes,
    )
    def repasses(self, request):
        exportar_repasses_async.delay(
            data_inicio=request.query_params.get("data_inicio"),
            data_final=request.query_params.get("data_final"),
            username=request.user.username,
            dre_uuid=request.query_params.get("dre_uuid"),
        )

        return Response(
            {
                "response": "O arquivo está sendo gerado e será enviado para a central de download após conclusão."
            },
            status=HTTP_201_CREATED,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="data_inicio",
                type=OpenApiTypes.DATE,
                description="Data de início",
                required=False,
            ),
            OpenApiParameter(
                name="data_final",
                type=OpenApiTypes.DATE,
                description="Data final",
                required=False,
            ),
        ]
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="dados_membros_apm",
        permission_classes=permission_classes,
    )
    def dados_membros_apm(self, request):
        if flag_is_active(self.request, "historico-de-membros"):
            exportar_dados_membros_apm_async.delay(
                data_inicio=request.query_params.get("data_inicio"),
                data_final=request.query_params.get("data_final"),
                username=request.user.username,
            )
        else:
            exportar_dados_membros_apm_legado_async.delay(
                data_inicio=request.query_params.get("data_inicio"),
                data_final=request.query_params.get("data_final"),
                username=request.user.username,
            )

        return Response(
            {
                "response": "O arquivo está sendo gerado e será enviado para a central de download após conclusão."
            },
            status=HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="processos-sei-regularidade",
        permission_classes=permission_classes,
    )
    def processos_sei_regularidade(self, request):
        exportar_processos_sei_regularidade_async.delay(
            username=request.user.username,
        )

        return Response(
            {
                "response": "O arquivo está sendo gerado e será enviado para a central de download após conclusão."
            },
            status=HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="processos-sei-prestacao-contas",
        permission_classes=permission_classes,
    )
    def processos_sei_prestacao_contas(self, request):
        exportar_processos_sei_prestacao_contas_async.delay(
            username=request.user.username,
            dre_uuid=request.query_params.get("dre_uuid"),
        )

        return Response(
            {
                "response": "O arquivo está sendo gerado e será enviado para a central de download após conclusão."
            },
            status=HTTP_201_CREATED,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='data_inicio',
                description='Filtro de início de data de criação',
                required=False,
                allow_blank=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='data_final',
                description='Filtro de fim de data de criação',
                required=False,
                allow_blank=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='dre_uui',
                description='Filtro de uuid de DRE',
                required=False,
                allow_blank=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
        description="Parâmetros de URL",
        responses={200: "Success"},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="associacoes",
        permission_classes=permission_classes,
    )
    def associacoes(self, request):
        exportar_associacoes_async.delay(
            username=request.user.username,
            dre_uuid=request.query_params.get("dre_uuid"),
            data_inicio=request.query_params.get("data_inicio"),
            data_final=request.query_params.get("data_final"),
        )

        return Response(
            {
                "response": "O arquivo está sendo gerado e será enviado para a central de download após conclusão."
            },
            status=HTTP_201_CREATED,
        )
