from rest_framework import serializers

from ...models import JustificativaRelatorioConsolidadoDRE, ConsolidadoDRE
from sme_ptrf_apps.core.models import Periodo, TipoConta, Unidade

class JustificativaRelatorioConsolidadoDreRetrieveSerializer(serializers.ModelSerializer):
    dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Unidade.objects.all()
    )

    tipo_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=TipoConta.objects.all()
    )

    periodo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Periodo.objects.all()
    )

    consolidado_dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=ConsolidadoDRE.objects.all(),
        allow_null=True
    )

    class Meta:
        model = JustificativaRelatorioConsolidadoDRE
        fields = ('uuid', 'dre', 'tipo_conta', 'periodo', 'texto', 'consolidado_dre')
