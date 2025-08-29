from rest_framework import serializers
from sme_ptrf_apps.core.models.periodo import Periodo
from sme_ptrf_apps.despesas.models.rateio_despesa import RateioDespesa
from sme_ptrf_apps.despesas.models.despesa import Despesa
from sme_ptrf_apps.core.api.serializers.associacao_serializer import AssociacaoSerializer
from sme_ptrf_apps.core.api.serializers.conta_associacao_serializer import ContaAssociacaoSerializer
from sme_ptrf_apps.core.api.serializers.acao_associacao_serializer import AcaoAssociacaoSerializer
from sme_ptrf_apps.despesas.api.serializers.especificacao_material_servico_serializer import EspecificacaoMaterialServicoSerializer
from sme_ptrf_apps.despesas.api.serializers.tipo_custeio_serializer import TipoCusteioSerializer
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoDespesa, BemProduzidoRateio

class RateioDespesaSerializer(serializers.ModelSerializer):
    associacao = AssociacaoSerializer()
    conta_associacao = ContaAssociacaoSerializer()
    acao_associacao = AcaoAssociacaoSerializer()
    especificacao_material_servico = EspecificacaoMaterialServicoSerializer()
    tipo_custeio = TipoCusteioSerializer()
    
    def to_representation(self, instance):
        data = {
            'num_documento': instance.despesa.numero_documento,
            'data_documento': instance.despesa.data_documento,
            'acao': instance.acao_associacao.acao.nome,
            'especificacao_do_bem': instance.especificacao_material_servico.descricao if instance.especificacao_material_servico else None,
            'valor': instance.valor_rateio,
        }
        bem_produzido_despesa = self.context.get('bem_produzido_despesa')
        valor_utilizado = None
        if bem_produzido_despesa:
            rateio_bem = BemProduzidoRateio.objects.filter(
                rateio=instance, bem_produzido_despesa=bem_produzido_despesa
            ).first()
            if rateio_bem:
                valor_utilizado = rateio_bem.valor_utilizado
        data['valor_utilizado'] = valor_utilizado
        return data

    class Meta:
        model = RateioDespesa
        fields = '__all__'

class BemProduzidoDespesaSerializer(serializers.ModelSerializer):
    rateios = serializers.SerializerMethodField()
    despesa_uuid = serializers.SerializerMethodField()

    def get_rateios(self, instance):
        return RateioDespesaSerializer(
            instance.despesa.rateios.all(),
            many=True,
            context={'bem_produzido_despesa': instance}
        ).data

    def get_despesa_uuid(self, instance):
        return getattr(instance.despesa, 'uuid', None)

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

    def get_data_aquisicao_producao(self, instance):
        """Retorna a data do documento mais recente das despesas relacionadas"""
        datas_documentos = []
        for despesa in instance.bem_produzido.despesas.all():
            if despesa.despesa.data_documento:
                datas_documentos.append(despesa.despesa.data_documento)
        
        if datas_documentos:
            return max(datas_documentos)
        return None

    def get_periodo_mais_recente(self, instance):
        """Retorna o período mais recente das despesas relacionadas (com base em data_transacao)"""
        periodos = []
        for bem_prod_desp in instance.bem_produzido.despesas.all():
            desp = bem_prod_desp.despesa
            periodo = getattr(desp, 'periodo_da_despesa', None)
            if periodo:
                periodos.append(periodo)
        if periodos:
            periodo_mais_recente = max(periodos, key=lambda p: p.data_fim_realizacao_despesas)
            return periodo_mais_recente.referencia
        return None

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
                'tipo': 'Adquirido',
                'despesa_uuid': instance.despesa.uuid
            }
        else:  # É BemProduzidoItem
            return {
                'uuid': instance.uuid,
                'status': instance.bem_produzido.status,
                'numero_documento': self.get_num_documentos(instance),
                'especificacao_do_bem': instance.especificacao_do_bem.descricao if instance.especificacao_do_bem else None,
                'data_aquisicao_producao': self.get_data_aquisicao_producao(instance),
                'num_processo_incorporacao': instance.num_processo_incorporacao,
                'periodo': self.get_periodo_mais_recente(instance),
                'quantidade': instance.quantidade,
                'valor_total': instance.valor_total,
                'despesas': BemProduzidoDespesaSerializer(instance.bem_produzido.despesas.all(), many=True).data,
                'tipo': 'Produzido',
                'bem_produzido_uuid': instance.bem_produzido.uuid
            }
