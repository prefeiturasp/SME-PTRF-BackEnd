from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.api.serializers.acao_associacao_serializer import \
    AcaoAssociacaoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.conta_associacao_serializer import \
    ContaAssociacaoLookUpSerializer
from sme_ptrf_apps.receitas.models import Receita

from ..serializers import (ReceitaCreateSerializer, ReceitaListaSerializer,
                           TipoReceitaSerializer)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ReceitaViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    lookup_field = 'uuid'
    permission_classes = [AllowAny]
    queryset = Receita.objects.all().order_by('-data')
    serializer_class = ReceitaListaSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    ordering_fields = ('data',)
    search_fields = ('uuid', 'id', 'descricao')
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ReceitaListaSerializer
        else:
            return ReceitaCreateSerializer

    @action(detail=False, url_path='tabelas')
    def tabelas(self, request):

        def get_valores_from(serializer):
            valores = serializer.Meta.model.get_valores()
            return serializer(valores, many=True).data if valores else []

        result = {
            'tipos_receita': get_valores_from(TipoReceitaSerializer),
            'acoes_associacao': get_valores_from(AcaoAssociacaoLookUpSerializer),
            'contas_associacao': get_valores_from(ContaAssociacaoLookUpSerializer)
        }

        return Response(result)
