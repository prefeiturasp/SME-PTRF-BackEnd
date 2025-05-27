from rest_framework import serializers

from sme_ptrf_apps.situacao_patrimonial.api.serializers.rateio_situacao_patrimonial_serializer import RateioSituacaoPatrimonialSerializer
from sme_ptrf_apps.despesas.api.serializers.tipo_documento_serializer import TipoDocumentoListSerializer
from sme_ptrf_apps.despesas.api.serializers.tipo_transacao_serializer import TipoTransacaoSerializer
from sme_ptrf_apps.despesas.models import Despesa
from sme_ptrf_apps.core.models import Associacao, Periodo

class DespesaSituacaoPatrimonialSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    tipo_documento = TipoDocumentoListSerializer()
    tipo_transacao = TipoTransacaoSerializer()
    rateios = RateioSituacaoPatrimonialSerializer(many=True)
    
    periodo_referencia = serializers.SerializerMethodField(method_name="get_periodo_referencia", required=False, allow_null=True)
    
    def get_periodo_referencia(self, despesa):
        if not despesa.data_documento:
            return None

        periodo = Periodo.da_data(despesa.data_documento)
        return periodo.referencia if periodo else None

    class Meta:
        model = Despesa
        fields = (
        'uuid', 'associacao', 'numero_documento', 'status', 'tipo_documento', 'data_documento', 'cpf_cnpj_fornecedor',
        'nome_fornecedor', 'valor_total', 'valor_ptrf', 'data_transacao', 'tipo_transacao', 'documento_transacao',
        'rateios', 'periodo_referencia')