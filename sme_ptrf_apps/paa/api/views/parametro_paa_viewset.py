import logging

from waffle.mixins import WaffleFlagMixin
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from sme_ptrf_apps.paa.models import ParametroPaa

logger = logging.getLogger(__name__)


class ParametrosPaaViewSet(WaffleFlagMixin, GenericViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = ParametroPaa.objects.all()
    pagination_class = CustomPagination

    @action(detail=False, methods=['get'], url_path='mes-elaboracao-paa')
    def mes_elaboracao_paa(self, request):
        texto = ParametroPaa.get().mes_elaboracao_paa
        return Response({'detail': texto}, status=status.HTTP_200_OK)
