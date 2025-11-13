from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample
)

DOCS = dict(
    buscar_informacao_professor_gremio=extend_schema(
        description="Retorna informações do servidor (professor do grêmio) pelo RF usando TerceirizadasService.",
        parameters=[
            OpenApiParameter(
                name='rf',
                description='Registro Funcional (RF) do servidor',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={200: OpenApiExample(
            name="Exemplo de resposta",
            value={
                "mensagem": "buscando-servidor-nao-membro",
                "nome": "Nome do Servidor",
                "cargo": "Cargo do Servidor"
            }
        )},
    ),
    get_participantes_ordenados_por_cargo=extend_schema(
        description="Retorna todos os participantes de uma ata PAA ordenados pelo cargo.",
        parameters=[
            OpenApiParameter(
                name='ata_paa_uuid',
                description='UUID da ata PAA',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={200: OpenApiExample(
            name="Exemplo de resposta",
            value=[
                {
                    'uuid': 'uuid-1234',
                    'identificacao': '1234567',
                    'nome': 'Nome do Participante',
                    'cargo': 'Cargo',
                    'membro': True,
                    'presente': True,
                    'presidente_da_reuniao': False,
                    'secretario_da_reuniao': False,
                    'professor_gremio': False
                }
            ]
        )},
    ),
    padrao_presentes=extend_schema(
        description="Retorna os membros padrão de uma ata PAA para marcação de presença.",
        parameters=[
            OpenApiParameter(
                name='ata_paa_uuid',
                description='UUID da ata PAA',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={200: OpenApiExample(
            name="Exemplo de resposta",
            value=[{
                "ata_paa": 'uuid-1234',
                "cargo": 'Presidente da diretoria executiva',
                "identificacao": '1234567',
                "nome": 'Nome do Membro',
                "editavel": False,
                "membro": True,
                "presente": True
            }]
        )},
    ),
)

