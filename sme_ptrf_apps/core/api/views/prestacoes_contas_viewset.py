from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers.prestacao_conta_serializer import PrestacaoContaLookUpSerializer
from ...models import PrestacaoConta


class PrestacoesContasViewSet(mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             GenericViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = PrestacaoConta.objects.all()
    serializer_class = PrestacaoContaLookUpSerializer

    @action(detail=False, url_path='por-conta-e-periodo')
    def por_conta_e_periodo(self, request):
        conta_associacao_uuid = request.query_params.get('conta_associacao_uuid')
        periodo_uuid = request.query_params.get('periodo_uuid')
        return Response(PrestacaoContaLookUpSerializer(
            self.queryset.filter(conta_associacao__uuid=conta_associacao_uuid).filter(
                periodo__uuid=periodo_uuid).first(), many=False).data)
