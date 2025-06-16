import logging

from waffle.mixins import WaffleFlagMixin

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter


from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe

from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoItem
from sme_ptrf_apps.situacao_patrimonial.api.serializers import BemProduzidoItemSerializer, BemProduzidoItemCreateSerializer

logger = logging.getLogger(__name__)

class BemProduzidoItemViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "situacao-patrimonial"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = BemProduzidoItem.objects.all().order_by('id')
    serializer_class = BemProduzidoItemSerializer
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_fields = ('bem_produzido__uuid',)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BemProduzidoItemCreateSerializer
        return BemProduzidoItemSerializer