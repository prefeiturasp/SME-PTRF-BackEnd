from rest_framework import serializers

from ...models import DocumentoAdicional, RelatorioConsolidadoDRE, AtaParecerTecnico
from ...models.analise_consolidado_dre import AnaliseConsolidadoDre
from ...models.analise_documento_consolidado_dre import AnaliseDocumentoConsolidadoDre


class AnalisesDocumentosConsolidadoDreSerializer(serializers.ModelSerializer):
    analise_consolidado_dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AnaliseConsolidadoDre.objects.all()
    )

    documento_adicional = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=DocumentoAdicional.objects.all()
    )

    relatorio_consolidao_dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=RelatorioConsolidadoDRE.objects.all()
    )

    ata_parecer_tecnico = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AtaParecerTecnico.objects.all()
    )

    class Meta:
        model = AnaliseDocumentoConsolidadoDre
        order_by = 'id'
        fields = (
            'analise_consolidado_dre',
            'ata_parecer_tecnico',
            'documento_adicional',
            'relatorio_consolidao_dre',
            'detalhamento',
            'resultado',
            'uuid',
        )
