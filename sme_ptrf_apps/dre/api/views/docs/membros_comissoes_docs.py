from ...serializers.membro_comissao_serializer import MembroComissaoListSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter


DOCS = dict(
    list=extend_schema(
        description=(
            "Retorna a lista de membros das comissões, com possibilidade de filtro por DRE, comissão e nome ou RF.\n\n"
            "Filtros disponíveis:\n"
            "- **dre__uuid**: UUID da DRE associada ao membro.\n"
            "- **comissao_uuid**: UUID da comissão.\n"
            "- **nome_ou_rf**: Nome (parcial, insensível a acentos) ou RF (registro funcional) do membro."
        ),
        parameters=[
            OpenApiParameter(name="dre__uuid", description="UUID da DRE do membro", required=False, type=str),
            OpenApiParameter(name="comissao_uuid", description="UUID da comissão associada", required=False, type=str),
            OpenApiParameter(name="nome_ou_rf", description="Nome ou RF do membro", required=False, type=str),
        ],
        responses={
            200: OpenApiResponse(
                response=MembroComissaoListSerializer,
                description="Lista de membros retornada com sucesso"),
        },
    ),
)
