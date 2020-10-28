from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated

from ..serializers.fornecedor_serializer import FornecedorSerializer
from ...models import Fornecedor


class FornecedoresViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    ordering_fields = ('nome',)
    search_fields = ('uuid', 'nome',)
    filter_fields = ('uuid', 'cpf_cnpj')

    def get_serializer_class(self):
        return FornecedorSerializer
