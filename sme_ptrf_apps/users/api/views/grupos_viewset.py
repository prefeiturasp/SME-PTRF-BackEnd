from django_filters import rest_framework as filters
from django.core.exceptions import ValidationError
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from ..serializers import GrupoSerializer
from ...models import Grupo

class GruposViewSet(mixins.ListModelMixin, GenericViewSet):
    # TODO: Voltar a usar IsAuthenticated
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    lookup_field = 'id'
    queryset = Grupo.objects.all().order_by('name')
    serializer_class = GrupoSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    search_fields = ['name', 'descricao', ]
    filter_fields = ('visoes__id', 'visoes__nome')

    def get_queryset(self, *args, **kwargs):
        """
        Uso do parâmetro visao_base:
        "SME" - Considera os grupos de todas as visões (SME, DRE e UE)

        "DRE" - Considera os grupos de DRE e UE

        "UE"  - Considera os grupos de UE apenas
        """
        qs = self.queryset
        qs = qs.exclude(visoes=None)

        visao_base= self.request.query_params.get('visao_base')

        if visao_base and visao_base not in ['SME', 'DRE', 'UE']:
            raise ValidationError({"visao_base": "O valor do parâmetro visao_base deve ser SME, DRE ou UE"})

        if not visao_base or visao_base == 'SME':
            return qs

        if visao_base  == 'UE':
            return qs.filter(visoes__nome=visao_base)

        if visao_base  == 'DRE':
            return qs.filter(visoes__nome__in=['DRE', 'UE'])

    @extend_schema(parameters=[
        OpenApiParameter(
            name='visao_base',
            description='"UE", "DRE" ou "SME". Para exibirapenas grupos da visão e suas subordinadas. ',
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
