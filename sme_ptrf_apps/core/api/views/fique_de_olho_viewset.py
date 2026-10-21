from rest_framework import mixins, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action

from ..serializers import FiqueDeOlhoSerializer
from ...models import Recurso, FiqueDeOlho, TipoTextoFiqueDeOlhoChoices
from ..utils.pagination import CustomPagination

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    inline_serializer
)


@extend_schema_view(
    list=extend_schema(
        description=(
            "Retorna a lista de fique de olho. "
            "Permite filtrar por **tipo_de_texto**, **recurso**"
        ),
        parameters=[
            OpenApiParameter("tipo_de_texto", str, OpenApiParameter.QUERY,
                             description="Filtra por tipo de texto"),
            OpenApiParameter("recurso", str, OpenApiParameter.QUERY, description="Filtra por recurso"),
        ],
        responses={200: FiqueDeOlhoSerializer(many=True)},
    ),
    tabelas=extend_schema(
        description=(
            "Retorna os tipos de texto disponíveis"
        ),
        parameters=[],
        responses={
            200: inline_serializer(
                name="TabelaFiqueDeOlho",
                fields={
                    "tipos_de_texto": serializers.ListField(child=serializers.CharField()),
                },
            ),
        },
    )
)
class FiqueDeOlhoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                         mixins.UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = FiqueDeOlho.objects.all()
    serializer_class = FiqueDeOlhoSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = FiqueDeOlho.objects.all()

        recurso_uuid = self.request.query_params.get('recurso_uuid')
        if recurso_uuid is not None:
            recurso = Recurso.objects.filter(uuid=recurso_uuid).first()

            if recurso is None:
                raise ValidationError({'detail': 'Recurso não encontrado.'})
            qs = FiqueDeOlho.filter_by_recurso(recurso, qs)

        tipo_de_texto = self.request.query_params.get('tipo_texto')
        if tipo_de_texto is not None:
            qs = FiqueDeOlho.filter_by_tipo_texto(tipo_de_texto, qs)

        return qs.order_by('id')

    @action(detail=False, url_path='tabelas',
            permission_classes=[IsAuthenticated])
    def tabelas(self, request):
        result = {
            "tipos_de_texto": TipoTextoFiqueDeOlhoChoices.choices,
        }

        return Response(result, status=status.HTTP_200_OK)
