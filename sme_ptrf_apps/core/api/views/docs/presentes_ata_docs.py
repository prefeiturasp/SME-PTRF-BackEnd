from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


DOCS = dict(
    membros_e_nao_membros=extend_schema(
        description="Retorna a lista de membros e não membros presentes em uma ata.",
        parameters=[
            OpenApiParameter(
                name="ata_uuid",
                type=str,
                location=OpenApiParameter.QUERY,
                description="UUID da ata",
                required=True,
            )
        ],
        responses={200: 'result'},
        examples=[
            OpenApiExample(
                name="Exemplo de resposta",
                value={
                    'presentes_membros': [],
                    'presentes_nao_membros': [],
                    'presentes_ata_conselho_fiscal': []
                }
            )
        ]
    ),
    padrao_presentes=extend_schema(
        description="Retorna os membros padrão de uma ata para marcação de presença.",
        parameters=[
            OpenApiParameter(
                name="ata_uuid",
                type=str,
                location=OpenApiParameter.QUERY,
                description="UUID da ata",
                required=True,
            )
        ],
        responses={200: 'result'},
        examples=[
            OpenApiExample(
                name="Exemplo de resposta",
                value=[{
                    "ata": 'uuid-1234',
                    "cargo": '',
                    "identificacao": '',
                    "nome": '',
                    "editavel": False,
                    "membro": True,
                    "presente": True
                }]
            )
        ]
    ),
    presentes_padrao_conselho_fiscal=extend_schema(
        description="Retorna os membros padrão do conselho fiscal de uma ata.",
        parameters=[
            OpenApiParameter(
                name="ata_uuid",
                type=str,
                location=OpenApiParameter.QUERY,
                description="UUID da ata",
            )
        ],
        responses={200: 'result'},
        examples=[
            OpenApiExample(
                name="Exemplo de resposta",
                value={
                    "presidente_conselho_fiscal": "",
                    "conselheiro_1": "",
                    "conselheiro_2": "",
                    "conselheiro_3": "",
                    "conselheiro_4": "",
                    "conselheiro_5": "",
                }
            )
        ]
    ),
    get_nome_cargo_membro_associacao=extend_schema(
        description="Retorna o nome e cargo de um membro da associação ou participante da ata.",
        parameters=[
            OpenApiParameter(
                name="ata_uuid",
                type=str,
                location=OpenApiParameter.QUERY,
                description="UUID da ata",
            ),
            OpenApiParameter(
                name="identificador",
                type=str,
                location=OpenApiParameter.QUERY,
                description="CPF ou código de identificação do membro",
                required=True,
            ),
            OpenApiParameter(
                name="data",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
                description="Data de referência",
            )
        ],
        responses={200: 'result'},
        examples=[
            OpenApiExample(
                name="Exemplo de resposta",
                value={"mensagem": "", "nome": "", "cargo": ""}
            )
        ]
    ),
    get_participantes_ordenados_por_cargo=extend_schema(
        description="Retorna todos os participantes de uma ata ordenados pelo cargo.",
        parameters=[
            OpenApiParameter(
                name="ata_uuid",
                type=str,
                location=OpenApiParameter.QUERY,
                description="UUID da ata",
            )
        ],
        responses={200: 'result'},
        examples=[
            OpenApiExample(
                name="Exemplo de resposta",
                value=[
                    {
                        'id': 0,
                        'identificacao': "",
                        'nome': "",
                        'cargo': "",
                        'membro': "",
                        'presente': "",
                        'presidente_da_reuniao': "",
                        'secretario_da_reuniao': "",
                    }
                ]
            )
        ]
    ),
)
