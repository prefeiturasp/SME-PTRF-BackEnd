from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
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
from ...services import atualiza_repasse_para_pendente

class ReceitaViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    lookup_field = 'uuid'
    permission_classes = [AllowAny]
    queryset = Receita.objects.all().order_by('-data')
    serializer_class = ReceitaListaSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    ordering_fields = ('data',)
    search_fields = ('descricao',)
    filter_fields = ('associacao__uuid', 'tipo_receita', 'acao_associacao__uuid', 'conta_associacao__uuid')

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ReceitaListaSerializer
        else:
            return ReceitaCreateSerializer

    def get_queryset(self):
        user = self.request.user
        return Receita.objects.filter(associacao__usuario=user).all().order_by('-data')

    @action(detail=False, url_path='tabelas')
    def tabelas(self, request):

        def get_valores_from(serializer):
            valores = serializer.Meta.model.get_valores(user=request.user)
            return serializer(valores, many=True).data if valores else []

        result = {
            'tipos_receita': get_valores_from(TipoReceitaSerializer),
            'acoes_associacao': get_valores_from(AcaoAssociacaoLookUpSerializer),
            'contas_associacao': get_valores_from(ContaAssociacaoLookUpSerializer)
        }

        return Response(result)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.tipo_receita.e_repasse:
            atualiza_repasse_para_pendente(instance.acao_associacao)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
