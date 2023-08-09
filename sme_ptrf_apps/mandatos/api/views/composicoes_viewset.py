from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from rest_framework.permissions import IsAuthenticated
from ...models import Composicao
from ..serializers.composicao_serializer import ComposicaoSerializer


class ComposicoesViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    permission_classes = [IsAuthenticated, PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Composicao.objects.all()
    serializer_class = ComposicaoSerializer
    pagination_class = CustomPagination



