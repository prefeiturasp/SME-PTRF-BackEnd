from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers.despesa_serializer import DespesaSerializer, DespesaCreateSerializer
from ..serializers.tipo_aplicacao_recurso_serializer import TipoAplicacaoRecursoSerializer
from ..serializers.tipo_custeio_serializer import TipoCusteioSerializer
from ..serializers.tipo_documento_serializer import TipoDocumentoSerializer
from ..serializers.tipo_transacao_serializer import TipoTransacaoSerializer

from ....core.api.serializers.acao_associacao_serializer import AcaoAssociacaoLookUpSerializer
from ....core.api.serializers.conta_associacao_serializer import ContaAssociacaoLookUpSerializer

from ...models import Despesa


class DespesasViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         GenericViewSet):

    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = Despesa.objects.all()
    serializer_class = DespesaSerializer

    def get_queryset(self):
        return self.queryset

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return DespesaSerializer
        else:
            return DespesaCreateSerializer

    @action(detail=False, url_path='tabelas')
    def tabelas(self, request):

        def get_valores_from(serializer):
            valores = serializer.Meta.model.get_valores()
            return serializer(valores, many=True).data if valores else []

        result = {
            'tipos_aplicacao_recurso': get_valores_from(TipoAplicacaoRecursoSerializer),
            'tipos_custeio': get_valores_from(TipoCusteioSerializer),
            'tipos_documento': get_valores_from(TipoDocumentoSerializer),
            'tipos_transacao': get_valores_from(TipoTransacaoSerializer),
            'acoes_associacao': get_valores_from(AcaoAssociacaoLookUpSerializer),
            'contas_associacao': get_valores_from(ContaAssociacaoLookUpSerializer)
        }

        return Response(result)
