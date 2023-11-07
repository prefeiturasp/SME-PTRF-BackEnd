from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from waffle.mixins import WaffleFlagMixin
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from rest_framework.permissions import IsAuthenticated
from ...models import Composicao
from ..serializers.composicao_serializer import ComposicaoSerializer


class ComposicoesViewSet(
    WaffleFlagMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    waffle_flag = "historico-de-membros"
    permission_classes = [IsAuthenticated, PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Composicao.objects.all()
    serializer_class = ComposicaoSerializer
    pagination_class = CustomPagination



