from rest_framework import serializers
from sme_ptrf_apps.core.api.serializers.unidade_serializer import DreSerializer
from sme_ptrf_apps.core.api.serializers import PeriodoLookUpSerializer
from ..serializers.relatorio_consolidado_dre_serializer import RelatorioConsolidadoDreSerializer
from ..serializers.ata_parecer_tecnico_serializer import AtaParecerTecnicoLookUpSerializer
from ...models import ConsolidadoDRE


class ConsolidadoDreSerializer(serializers.ModelSerializer):
    dre = DreSerializer()
    periodo = PeriodoLookUpSerializer()

    class Meta:
        model = ConsolidadoDRE
        fields = ('uuid', 'dre', 'periodo', 'status', 'versao')


class ConsolidadoDreComDocumentosSerializer(serializers.ModelSerializer):
    from ..serializers.lauda_serializer import LaudaLookupSerializer
    relatorios_consolidados_dre_do_consolidado_dre = RelatorioConsolidadoDreSerializer(many=True)
    atas_de_parecer_tecnico_do_consolidado_dre = AtaParecerTecnicoLookUpSerializer(many=True)
    laudas_do_consolidado_dre = LaudaLookupSerializer(many=True)

    class Meta:
        model = ConsolidadoDRE
        fields = (
            'uuid',
            'status',
            'relatorios_consolidados_dre_do_consolidado_dre',
            'atas_de_parecer_tecnico_do_consolidado_dre',
            'laudas_do_consolidado_dre',
        )
