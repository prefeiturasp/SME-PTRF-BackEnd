from rest_framework import mixins

from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet

from ..serializers.tipo_devolucao_ao_tesouro_serializer import TipoDevolucaoAoTesouroSerializer
from ...models import TipoDevolucaoAoTesouro
from sme_ptrf_apps.users.permissoes import PermissaoApiUe


class TiposDevolucaoAoTesouroViewSet(mixins.ListModelMixin,
                                     mixins.RetrieveModelMixin,
                                     GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = TipoDevolucaoAoTesouro.objects.all()
    serializer_class = TipoDevolucaoAoTesouroSerializer
