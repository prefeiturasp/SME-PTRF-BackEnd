from ...serializers.valores_reprogramados_serializer import ValoresReprogramadosListSerializer
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
)

DOCS = dict(
    list=extend_schema(
        summary="Listar valores reprogramados",
        description=(
            "Lista os valores reprogramados por DRE, com possibilidade de filtragem "
            "por nome, tipo de unidade ou status."
        ),
        parameters=[
            OpenApiParameter(name="dre_uuid", description="UUID da DRE.", required=True, type=str),
            OpenApiParameter(name="search", description="Busca parcial por nome da associação/unidade ou Código EOL.",
                             required=False, type=str),
            OpenApiParameter(name="tipo_unidade", description="Filtrar pelo tipo da unidade.",
                             required=False, type=str),
            OpenApiParameter(name="status", description="Lista de status separados por vírgula.",
                             required=False, type=str),
        ],
        responses={200: ValoresReprogramadosListSerializer},
    ),
    tabelas=extend_schema(
        description="Retorna as opções de status dos valores reprogramados disponíveis.",
        responses={200: "result"},
        examples=[
            OpenApiExample(
                "Exemplo de resposta",
                value={"status": [
                    {"id": "NAO_FINALIZADO", "nome": "Nao Finalizado"},
                    {"id": "EM_CONFERENCIA_DRE", "nome": "Em conferência DRE"},
                    {"id": "EM_CORRECAO_UE", "nome": "Em correção UE"},
                    {"id": "VALORES_CORRETOS", "nome": "Valores Corretos"},
                ]},
            ),
        ],
    ),
    lista_associacoes=extend_schema(
        description=(
            "Retorna todas as associações vinculadas à DRE informada, "
            "aplicando filtros opcionais por nome, tipo ou status."
        ),
        parameters=[
            OpenApiParameter(name="dre_uuid", description="UUID da DRE.", required=True, type=str),
            OpenApiParameter(name="search", description="Busca parcial por nome da associação.",
                             required=False, type=str),
            OpenApiParameter(name="tipo_unidade", description="Filtrar pelo tipo da unidade.",
                             required=False, type=str),
            OpenApiParameter(name="status", description="Lista de status separados por vírgula.",
                             required=False, type=str),
        ],
        responses={200: "result"},
        examples=[
            OpenApiExample(
                "Exemplo de resposta",
                value={"valores_reprogramados": [
                    {
                        "associacao": {},
                        "periodo": {},
                        "total_conta_um": 0,
                        "nome_conta_um": "conta_um",
                        "total_conta_dois": 0,
                        "nome_conta_dois": "conta_dois",
                    }
                ]},
            ),
        ]
    ),
    salvar_valores_reprogramados=extend_schema(
        description=(
            "Salva os valores reprogramados de uma associação. "
            "Necessita de UUID da associação, visão e dados do formulário."
        ),
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "associacao_uuid": {"type": "string"},
                    "dadosForm": {"type": "object"},
                    "visao": {"type": "string"},
                },
            }
        },
        responses={
            201: {
                "type": "object",
                "properties": {
                    "contas": {"type": "array", "items": {"type": "object"}},
                    "associacao": {"type": "object"},

                },
            },
        },
    ),
    concluir=extend_schema(
        description=(
            "Conclui o processo de reprogramação dos valores de uma associação. "
            "Requer os mesmos dados do endpoint de salvamento."
        ),
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "associacao_uuid": {"type": "string"},
                    "dadosForm": {"type": "object"},
                    "visao": {"type": "string"},
                },
            }
        },
        responses={
            201: {
                "type": "object",
                "properties": {
                    "contas": {"type": "array", "items": {"type": "object"}},
                    "associacao": {"type": "object"},

                },
            },
        },
    ),
    get_valores_reprogramados=extend_schema(
        description="Retorna os valores reprogramados e a estrutura de uma associação específica.",
        parameters=[OpenApiParameter(name="associacao_uuid", required=True, type=str)],
        responses={
            201: {
                "type": "object",
                "properties": {
                    "contas": {"type": "array", "items": {"type": "object"}},
                    "associacao": {"type": "object"},

                },
            },
        },
    ),
    get_status_valores_reprogramados=extend_schema(
        description="Retorna o status atual da reprogramação de valores de uma associação.",
        parameters=[OpenApiParameter(name="associacao_uuid", required=True, type=str)],
        responses={200: "result"},
        examples=[
            OpenApiExample(
                "Exemplo de resposta",
                value={"status": {
                    "texto": "Aguardando conferência da DRE",
                    "cor": 2,  # Laranja
                    "periodo_fechado": False
                }},
            ),
        ]
    ),
)
