from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ...models import AnoAnaliseRegularidade

from ..serializers.ano_analise_regularidade_serializer import AnoAnaliseRegularidadeListSerializer

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre,
)


class AnosAnaliseRegularidadeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'ano'
    queryset = AnoAnaliseRegularidade.objects.all().order_by('-ano')
    serializer_class = AnoAnaliseRegularidadeListSerializer
