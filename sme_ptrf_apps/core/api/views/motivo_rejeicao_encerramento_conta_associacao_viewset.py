from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from ..serializers import MotivoRejeicaoEncerramentoContaAssociacaoSerializer
from ...models import MotivoRejeicaoEncerramentoContaAssociacao
from ..utils.pagination import CustomPagination

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter('nome', OpenApiTypes.STR, OpenApiParameter.QUERY)
        ],
        responses={
            200: MotivoRejeicaoEncerramentoContaAssociacaoSerializer(many=True)
        }
    )
)
class MotivoRejeicaoEncerramentoContaAssociacaoViewset(mixins.ListModelMixin,
                                                       mixins.RetrieveModelMixin,
                                                       mixins.CreateModelMixin,
                                                       mixins.UpdateModelMixin,
                                                       mixins.DestroyModelMixin,
                                                       GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = MotivoRejeicaoEncerramentoContaAssociacao.objects.all()
    serializer_class = MotivoRejeicaoEncerramentoContaAssociacaoSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = MotivoRejeicaoEncerramentoContaAssociacao.objects.all()

        nome = self.request.query_params.get('nome')

        if nome is not None:
            qs = qs.filter(nome__unaccent__icontains=nome)

        return qs
