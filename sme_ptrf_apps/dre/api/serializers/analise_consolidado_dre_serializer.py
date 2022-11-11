import datetime
from rest_framework import serializers
from ...models.analise_consolidado_dre import AnaliseConsolidadoDre
from ...models.consolidado_dre import ConsolidadoDRE
from ..serializers.analise_documento_consolidado_dre_serializer import AnalisesDocumentosConsolidadoDreSerializer
from ..serializers.comentario_analise_consolidado_dre_serializer import ComentarioAnaliseConsolidadoDRESerializer
from ..serializers.relatorio_consolidado_dre_serializer import RelatorioConsolidadoDreSerializer

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


class AnaliseConsolidadoDreRetriveSerializer(serializers.ModelSerializer):
    consolidado_dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=ConsolidadoDRE.objects.all()
    )
    analises_de_documentos_da_analise_do_consolidado = AnalisesDocumentosConsolidadoDreSerializer(many=True)
    comentarios_de_analise_do_consolidado_dre = serializers.SerializerMethodField('get_comentarios_de_analise_do_consolidado')
    analises_de_documentos_do_relatorio_consolidao_dre = serializers.SerializerMethodField('get_analise_relatorio_consolidao_dre')

    def get_analise_relatorio_consolidao_dre(self, obj):
        return RelatorioConsolidadoDreSerializer(obj.consolidado_dre).data

    def get_comentarios_de_analise_do_consolidado(self, obj):
        return ComentarioAnaliseConsolidadoDRESerializer(obj.consolidado_dre.comentarios_de_analise_do_consolidado_dre, many=True).data

    class Meta:
        model = AnaliseConsolidadoDre
        order_by = 'id'
        fields = (
            'uuid',
            'consolidado_dre',
            'analises_de_documentos_da_analise_do_consolidado',
            'data_devolucao',
            'data_limite',
            'data_retorno_analise',
            'comentarios_de_analise_do_consolidado_dre',
            'analises_de_documentos_do_relatorio_consolidao_dre',
            'relatorio_acertos_pdf',
            'relatorio_acertos_versao',
            'relatorio_acertos_status',
            'relatorio_acertos_gerado_em'
        )
