from rest_framework import serializers
from ...models.comentario_analise_consolidado_dre import ComentarioAnaliseConsolidadoDRE
from ...models.consolidado_dre import ConsolidadoDRE


class ComentarioAnaliseConsolidadoDRESerializer(serializers.ModelSerializer):
    consolidado_dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=ConsolidadoDRE.objects.all()
    )

    class Meta:
        model = ComentarioAnaliseConsolidadoDRE
        order_by = 'ordem'
        fields = ('uuid', 'consolidado_dre', 'ordem', 'comentario', 'notificado', 'notificado_em')
