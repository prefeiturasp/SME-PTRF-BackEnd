import logging

from django.db.models import Q
from waffle.mixins import WaffleFlagMixin
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django.core.exceptions import ValidationError

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import (
    PermissaoAPIApenasSmeComLeituraOuGravacao
)
from sme_ptrf_apps.paa.api.serializers.periodo_paa_serializer import PeriodoPaaSerializer
from sme_ptrf_apps.paa.models import PeriodoPaa

logger = logging.getLogger(__name__)


class PeriodoPaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = []# [IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao]
    lookup_field = 'uuid'
    queryset = PeriodoPaa.objects.all().order_by('-data_inicial')
    serializer_class = PeriodoPaaSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = self.queryset

        filtro_referencia = self.request.query_params.get('referencia', None)

        if filtro_referencia is not None:
            qs = qs.filter(referencia__unaccent__icontains=filtro_referencia)

        return qs
