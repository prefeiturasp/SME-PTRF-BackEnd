import logging

from waffle.mixins import WaffleFlagMixin

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe

from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido
from sme_ptrf_apps.situacao_patrimonial.api.serializers import BemProduzidoSerializer

logger = logging.getLogger(__name__)


class BemProduzidoViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "situacao-patrimonial"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = BemProduzido.objects.all().order_by('id')
    serializer_class = BemProduzidoSerializer
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        qs = self.queryset
        associacao = self.request.query_params.get('associacao_uuid', None)

        if associacao is not None:
            qs = qs.filter(associacao__uuid=associacao)

        return qs
