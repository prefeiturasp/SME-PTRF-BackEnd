from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from rest_framework.permissions import IsAuthenticated
from ...models import OcupanteCargo
from ..serializers import OcupanteCargoSerializer

class OcupantesCargosViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    permission_classes = [IsAuthenticated, PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = OcupanteCargo.objects.all()
    serializer_class = OcupanteCargoSerializer
    pagination_class = CustomPagination
