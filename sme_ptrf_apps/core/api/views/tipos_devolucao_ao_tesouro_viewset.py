from rest_framework import mixins

from rest_framework.permissions import AllowAny

from rest_framework.viewsets import GenericViewSet

from ..serializers.tipo_devolucao_ao_tesouro_serializer import TipoDevolucaoAoTesouroSerializer
from ...models import TipoDevolucaoAoTesouro

class TiposDevolucaoAoTesouroViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      GenericViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = TipoDevolucaoAoTesouro.objects.all()
    serializer_class = TipoDevolucaoAoTesouroSerializer
