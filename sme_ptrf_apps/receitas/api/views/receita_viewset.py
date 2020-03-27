from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from sme_ptrf_apps.core.api.serializers.acao_associacao_serializer import \
    AcaoAssociacaoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.conta_associacao_serializer import \
    ContaAssociacaoLookUpSerializer
from sme_ptrf_apps.receitas.models import Receita

from ..serializers import ReceitaCreateSerializer, TipoReceitaSerializer


class ReceitaViewSet(mixins.CreateModelMixin,
                     GenericViewSet):
    lookup_field = 'uuid'
    permission_classes = [AllowAny]
    queryset = Receita.objects.all()
    serializer_class = ReceitaCreateSerializer

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
