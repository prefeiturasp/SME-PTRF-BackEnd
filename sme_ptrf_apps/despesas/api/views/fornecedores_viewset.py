from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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

    def list(self, request, *args, **kwargs):

        cpf_cnpj = self.request.query_params.get('cpf_cnpj')

        if cpf_cnpj == "00.000.000/0000-00":
            context = [{
                'cpf_cnpj': '00.000.000/0000-00',
                'nome': 'Despesa sem comprovação fiscal'
            }]
            return Response(context)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            return Response(FornecedorSerializer(queryset, many=True).data)

