from rest_framework import serializers
from ...models.analise_consolidado_dre import AnaliseConsolidadoDre
from ...models.consolidado_dre import ConsolidadoDRE


class AnaliseConsolidadoDreSerializer(serializers.ModelSerializer):
    consolidado_dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=ConsolidadoDRE.objects.all()
    )

    class Meta:
        model = AnaliseConsolidadoDre
        order_by = 'id'
        fields = ('uuid', 'consolidado_dre',)
