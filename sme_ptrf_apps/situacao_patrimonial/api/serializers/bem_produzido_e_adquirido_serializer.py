from rest_framework import serializers
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoDespesa
from sme_ptrf_apps.core.models.periodo import Periodo


class BemProduzidoRateioSerializer(serializers.Serializer):
    uuid = serializers.SlugField()
    num_documento = serializers.CharField()
    data_documento = serializers.CharField()
    especificacao_do_bem = serializers.CharField()
    valor = serializers.CharField()
    valor_utilizado = serializers.CharField()
    recursos_proprios = serializers.CharField()
    acao = serializers.CharField()

    def to_representation(self, instance):
        return {
            'num_documento': instance.rateio.despesa.numero_documento,
            'data_documento': instance.rateio.despesa.data_documento,
            'acao': instance.rateio.acao_associacao.acao.nome,
            'especificacao_do_bem': instance.rateio.especificacao_material_servico.descricao if instance.rateio.especificacao_material_servico else None,
            'valor': instance.rateio.valor_rateio,
            'valor_utilizado': instance.valor_utilizado,
        }


class BemProduzidoDespesaSerializer(serializers.ModelSerializer):
    rateios = BemProduzidoRateioSerializer(many=True)

    class Meta:
        model = BemProduzidoDespesa
        fields = '__all__'


class BemProduzidoEAdquiridoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tipo = serializers.CharField()
    status = serializers.CharField()
    numero_documento = serializers.CharField()
    especificacao_do_bem = serializers.CharField()
    data_aquisicao_producao = serializers.CharField()
    num_processo_incorporacao = serializers.CharField()
    periodo = serializers.CharField()

    def get_num_documentos(self, instance):
        documentos = []
        for despesa in instance.bem_produzido.despesas.all():
            if despesa.despesa.numero_documento:
                documentos.append(str(despesa.despesa.numero_documento))
        return ', '.join(documentos)

    def to_representation(self, instance):
        """Normaliza os dados independente do model origem"""
        if hasattr(instance, 'despesa'):  # É RateioDespesa
            return {
                'uuid': instance.uuid,
                'status': instance.status,
                'numero_documento': instance.despesa.numero_documento,
                'especificacao_do_bem': instance.especificacao_material_servico.descricao if instance.especificacao_material_servico else None,
                'data_aquisicao_producao': instance.despesa.data_documento,
                'num_processo_incorporacao': instance.numero_processo_incorporacao_capital,
                'periodo': Periodo.da_data(instance.despesa.data_documento).referencia if Periodo.da_data(instance.despesa.data_documento) else None,
                'quantidade': instance.quantidade_itens_capital,
                'valor_total': instance.valor_rateio,
                'tipo': 'Adquirido'
            }
        else:  # É BemProduzidoItem
            return {
                'uuid': instance.uuid,
                'status': instance.bem_produzido.status,
                'numero_documento': self.get_num_documentos(instance),
                'especificacao_do_bem': instance.especificacao_do_bem.descricao if instance.especificacao_do_bem else None,
                'data_aquisicao_producao': instance.criado_em,
                'num_processo_incorporacao': instance.num_processo_incorporacao,
                'periodo': Periodo.da_data(instance.criado_em).referencia if Periodo.da_data(instance.criado_em) else None,
                'quantidade': instance.quantidade,
                'valor_total': instance.valor_total,
                'despesas': BemProduzidoDespesaSerializer(instance.bem_produzido.despesas.all(), many=True).data,
                'tipo': 'Produzido',
                'bem_produzido_uuid': instance.bem_produzido.uuid
            }
