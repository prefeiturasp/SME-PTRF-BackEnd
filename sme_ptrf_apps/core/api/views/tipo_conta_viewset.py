from rest_framework import mixins

from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet

from ..serializers.tipo_conta_serializer import TipoContaSerializer
from ...models import TipoConta
from sme_ptrf_apps.users.permissoes import PermissaoDashboardDre


class TiposContaViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoDashboardDre]
    lookup_field = 'uuid'
    queryset = TipoConta.objects.all()
    serializer_class = TipoContaSerializer
