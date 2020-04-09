from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny

from ..serializers.especificacao_material_servico_serializer import EspecificacaoMaterialServicoLookUpSerializer
from ...models import EspecificacaoMaterialServico


class EspecificacaoMaterialServicoViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'id'
    queryset = EspecificacaoMaterialServico.objects.all()
    serializer_class = EspecificacaoMaterialServicoLookUpSerializer
    permission_classes = [AllowAny]
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    ordering_fields = ('descricao',)
    search_fields = ('uuid', 'id', 'descricao')
    filter_fields = ('aplicacao_recurso', 'tipo_custeio')

    def get_serializer_class(self):
        return EspecificacaoMaterialServicoLookUpSerializer
