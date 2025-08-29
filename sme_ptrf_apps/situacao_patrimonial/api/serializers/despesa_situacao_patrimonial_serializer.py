from rest_framework import serializers

from sme_ptrf_apps.situacao_patrimonial.api.serializers.rateio_situacao_patrimonial_serializer import RateioSituacaoPatrimonialSerializer
from sme_ptrf_apps.despesas.api.serializers.tipo_documento_serializer import TipoDocumentoListSerializer
from sme_ptrf_apps.despesas.api.serializers.tipo_transacao_serializer import TipoTransacaoSerializer
from sme_ptrf_apps.despesas.models import Despesa
from sme_ptrf_apps.core.models import Associacao, Periodo
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoDespesa

class DespesaSituacaoPatrimonialSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    tipo_documento = TipoDocumentoListSerializer()
    tipo_transacao = TipoTransacaoSerializer()
    rateios = serializers.SerializerMethodField()
    recursos_proprios = serializers.SerializerMethodField()
    
    periodo_referencia = serializers.SerializerMethodField(method_name="get_periodo_referencia", required=False, allow_null=True)
    
    def get_periodo_referencia(self, despesa):
        if not despesa.data_documento:
            return None

        periodo = Periodo.da_data(despesa.data_documento)
        return periodo.referencia if periodo else None

    def get_recursos_proprios(self, despesa):
        if not despesa.valor_recursos_proprios or despesa.valor_recursos_proprios <= 0:
            return None
            
        bem_produzido_uuid = self.context.get('bem_produzido_uuid')
        valor_utilizado = 0
        
        if bem_produzido_uuid:
            try:
                bem_produzido_despesa = BemProduzidoDespesa.objects.get(
                    bem_produzido__uuid=bem_produzido_uuid,
                    despesa=despesa
                )
                valor_utilizado = float(bem_produzido_despesa.valor_recurso_proprio_utilizado or 0)
            except BemProduzidoDespesa.DoesNotExist:
                pass
                
        return {
            'valor_disponivel': float(despesa.valor_recursos_proprios),
            'valor_utilizado': valor_utilizado
        }

    class Meta:
        model = Despesa
        fields = (
            'uuid', 'associacao', 'numero_documento', 'status', 'tipo_documento', 
            'data_documento', 'cpf_cnpj_fornecedor', 'nome_fornecedor', 'valor_total',
            'valor_ptrf', 'data_transacao', 'tipo_transacao', 'documento_transacao',
            'rateios', 'periodo_referencia', 'recursos_proprios'
        )

    def get_rateios(self, despesa):
        rateios = despesa.rateios.all()
        serializer = RateioSituacaoPatrimonialSerializer(
            rateios,
            many=True,
            context=self.context
        )
        return serializer.data
