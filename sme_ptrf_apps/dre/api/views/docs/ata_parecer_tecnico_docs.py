from sme_ptrf_apps.dre.api.serializers.ata_parecer_tecnico_serializer import AtaParecerTecnicoSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiExample, OpenApiTypes

DOCS = dict(
    list=extend_schema(
        description="Retorna a lista de atas de parecer técnico cadastradas no sistema.",
        responses={
            200: OpenApiResponse(response=AtaParecerTecnicoSerializer,
                                 description="Lista de atas retornada com sucesso."),
        },
    ),
    gerar_ata_parecer_tecnico=extend_schema(
        description=(
            "Gera de forma assíncrona o arquivo PDF da ata de parecer técnico.\n\n"
            "É necessário informar os UUIDs da **ata**, **dre** e **período** como parâmetros de query."
        ),
        parameters=[
            OpenApiParameter(name="ata", description="UUID da Ata de Parecer Técnico", required=True, type=str),
            OpenApiParameter(name="dre", description="UUID da DRE responsável", required=True, type=str),
            OpenApiParameter(name="periodo", description="UUID do período de referência", required=True, type=str),
        ],
        responses={
            200: 'result',
        },
        examples=[
            OpenApiExample(
                'Resposta',
                value={'mensagem': 'Arquivo na fila para processamento.'},
            )
        ]
    ),
    download_ata_parecer_tecnico=extend_schema(
        description=(
            "Permite realizar o download do arquivo PDF da Ata de Parecer Técnico previamente gerada. "
            "O parâmetro `ata` (UUID) é obrigatório."
        ),
        parameters=[
            OpenApiParameter(name="ata", description="UUID da Ata de Parecer Técnico", required=True, type=str),
        ],
        responses={
            (200, 'application/pdf'): OpenApiTypes.BINARY,
        },
    ),
    membros_comissao_exame_contas=extend_schema(
        summary="Listar Membros da Comissão de Exame de Contas",
        description=(
            "Retorna os membros da comissão de exame de contas vinculados a uma DRE e associados a "
            "uma determinada Ata. Os parâmetros obrigatórios são:\n"
            "- `dre`: UUID da DRE\n"
            "- `ata`: UUID da Ata"
        ),
        parameters=[
            OpenApiParameter(name="dre", description="UUID da DRE", required=True, type=str),
            OpenApiParameter(name="ata", description="UUID da Ata de Parecer Técnico", required=True, type=str),
        ],
        responses={200: "Membros da Comissão de Exame de Contas"},
        examples=[
            OpenApiExample(
                'Resposta',
                value=[
                    {
                        "ata": "uuid-1",
                        "uuid": "uuid-2",
                        "rf": "Cod rf",
                        "nome": "João da Silva",
                        "cargo": "Presidente",
                        "editavel": False
                    }
                ],
            )
        ]
    ),
    info_ata=extend_schema(
        description=(
            "Retorna informações consolidadas da execução financeira das unidades relacionadas a "
            "uma Ata de Parecer Técnico. Os parâmetros obrigatórios são:\n"
            "- `dre`: UUID da DRE\n"
            "- `periodo`: UUID do período\n"
            "Parâmetro opcional:\n"
            "- `ata`: UUID da Ata de Parecer Técnico"
        ),
        parameters=[
            OpenApiParameter(name="dre", description="UUID da DRE", required=True, type=str),
            OpenApiParameter(name="periodo", description="UUID do período", required=True, type=str),
            OpenApiParameter(name="ata", description="UUID da Ata de Parecer Técnico", required=False, type=str),
        ],
        responses={200: AtaParecerTecnicoSerializer(many=False)},
    ),
)