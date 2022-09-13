from rest_framework import serializers
from ...models import RelatorioConsolidadoDRE
from sme_ptrf_apps.core.api.serializers import TipoContaSerializer


class RelatorioConsolidadoDreSerializer(serializers.ModelSerializer):
    tipo_conta = TipoContaSerializer(many=False, required=False, allow_null=True)

    class Meta:
        model = RelatorioConsolidadoDRE
        fields = ('uuid', 'status', 'arquivo', 'versao', 'tipo_conta')
