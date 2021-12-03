from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from ...models import Comissao

from ..serializers.comissao_serializer import ComissaoSerializer

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre,
)


class ComissoesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = Comissao.objects.all()
    serializer_class = ComissaoSerializer
