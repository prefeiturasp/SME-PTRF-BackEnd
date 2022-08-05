import logging

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from ...models import Lauda
from ..serializers.lauda_serializer import LaudaSerializer


from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre,
)

logger = logging.getLogger(__name__)


class LaudaViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = Lauda.objects.all()
    serializer_class = LaudaSerializer
