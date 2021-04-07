from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from sme_ptrf_apps.users.permissoes import PermissaoApiDre

from sme_ptrf_apps.core.api.serializers import CobrancaPrestacaoContaListSerializer
from sme_ptrf_apps.core.models import CobrancaPrestacaoConta


class CobrancasPrestacoesContasViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    serializer_class = CobrancaPrestacaoContaListSerializer
    queryset = CobrancaPrestacaoConta.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('prestacao_conta__uuid', 'tipo', 'devolucao_prestacao__uuid', 'associacao__uuid', 'periodo__uuid')
