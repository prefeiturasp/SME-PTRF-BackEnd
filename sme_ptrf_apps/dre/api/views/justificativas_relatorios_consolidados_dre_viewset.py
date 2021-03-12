from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from sme_ptrf_apps.dre.api.serializers.justificativa_relatorio_consolidado_dre_serializer import JustificativaRelatorioConsolidadoDreRetrieveSerializer
from sme_ptrf_apps.dre.models import JustificativaRelatorioConsolidadoDRE
from sme_ptrf_apps.users.permissoes import PermissaoApiDre


class JustificativasRelatoriosConsolidadosDreViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    serializer_class = JustificativaRelatorioConsolidadoDreRetrieveSerializer
    queryset = JustificativaRelatorioConsolidadoDRE.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('dre__uuid', 'tipo_conta__uuid', 'periodo__uuid')
