from rest_framework import serializers
from sme_ptrf_apps.core.api.serializers.unidade_serializer import DreSerializer
from sme_ptrf_apps.core.api.serializers import PeriodoLookUpSerializer
from ..serializers.relatorio_consolidado_dre_serializer import RelatorioConsolidadoDreSerializer
from ...models import ConsolidadoDRE


class ConsolidadoDreSerializer(serializers.ModelSerializer):
    dre = DreSerializer()
    periodo = PeriodoLookUpSerializer()

    class Meta:
        model = ConsolidadoDRE
        fields = ('uuid', 'dre', 'periodo', 'status')


class ConsolidadoDreComDocumentosSerializer(serializers.ModelSerializer):
    relatorios_consolidados_dre_do_consolidado_dre = RelatorioConsolidadoDreSerializer(many=True)

    class Meta:
        model = ConsolidadoDRE
        fields = ('uuid', 'status', 'relatorios_consolidados_dre_do_consolidado_dre')
