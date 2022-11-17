import logging

from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from sme_ptrf_apps.users.permissoes import PermissaoApiDre, PermissaoAPIApenasDreComLeituraOuGravacao
from ...models.analise_consolidado_dre import AnaliseConsolidadoDre
from ..serializers.analise_consolidado_dre_serializer import AnaliseConsolidadoDreRetriveSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)


class AnalisesConsolidadoDreViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = AnaliseConsolidadoDre.objects.all()
    serializer_class = AnaliseConsolidadoDreRetriveSerializer
