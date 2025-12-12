from ...serializers.programa_pdde_serializer import ProgramaPddeSerializer, ProgramasPddeSomatorioTotalSerializer
from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse, OpenApiExample
)

DOCS = dict(
    list=extend_schema(
        description=(
            "Retorna uma lista paginada de todos os programas PDDE cadastrados, ordenados por nome. "
            "Suporta filtro por nome (case-insensitive)."),
        responses={
            200: ProgramaPddeSerializer(many=True),
        }
    ),
    retrieve=extend_schema(
        description="Retorna os detalhes de um programa PDDE específico pelo UUID.",
        responses={
            200: ProgramaPddeSerializer,
        }
    ),
    create=extend_schema(
        description="Cria um novo programa PDDE.",
        request=ProgramaPddeSerializer,
        responses={
            201: ProgramaPddeSerializer,
            400: "Erros de validação"
        },
        examples=[
            OpenApiExample(
                'Nome não informado',
                status_codes=[400],
                value={
                    'nome': ['Nome do Programa PDDE não foi informado.']
                }
            ),
            OpenApiExample(
                'Nome duplicado',
                status_codes=[400],
                value={
                    'erro': 'Duplicated',
                    'detail': 'Erro ao criar Programa PDDE. Já existe um Programa PDDE cadastrado com este nome.'
                }
            )
        ]
    ),
    partial_update=extend_schema(
        description="Atualiza parcialmente um programa PDDE. Se o nome for alterado, ele deve continuar sendo único.",
        request=ProgramaPddeSerializer,
        responses={
            200: ProgramaPddeSerializer,
            400: "Erros de validação",
        },
        examples=[
            OpenApiExample(
                'Nome duplicado',
                status_codes=[400],
                value={
                    'erro': 'Duplicated',
                    'detail': 'Erro ao atualizar Programa PDDE. Já existe um Programa PDDE cadastrado com este nome.'
                }
            )
        ]
    ),
    destroy=extend_schema(
        description="Exclui um programa PDDE. Não é possível excluir programas que estejam vinculados a ações PDDE.",
        responses={
            204: OpenApiResponse(description="Sem retorno"),
            400: "Não é possível excluir",
        },
        examples=[
            OpenApiExample(
                'Vínculo de Ações PDDE',
                status_codes=[400],
                value={
                    'erro': 'ProtectedError',
                    'mensagem': 'Não é possível excluir. Este programa ainda está vinculado há alguma ação.'
                }
            )
        ]
    ),
    somatorio_total_por_programas=extend_schema(
        description=(
            "Retorna os totais consolidados por programa PDDE relacionados a um PAA específico. "
            "Inclui somatórios de valores e quantidades."),
        parameters=[
            OpenApiParameter(
                name='paa_uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='UUID do PAA (Plano de Aplicação Anual)'
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Tamanho da página (padrão: 1000)'
            ),
        ],
        responses={
            200: ProgramasPddeSomatorioTotalSerializer,
            400: "Parâmetros inválidos",
        },
        examples=[
            OpenApiExample(
                'PAA não informado',
                status_codes=[400],
                value={
                    'erro': 'NotFound',
                    'mensagem': 'PAA não foi informado.'
                }
            )
        ]
    ),
)
