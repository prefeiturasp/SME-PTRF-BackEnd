from rest_framework import serializers

from sme_ptrf_apps.despesas.api.serializers.especificacao_material_servico_serializer import EspecificacaoMaterialServicoSerializer
from sme_ptrf_apps.despesas.models.especificacao_material_servico import EspecificacaoMaterialServico
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido, BemProduzidoItem

class BemProduzidoItemSerializer(serializers.ModelSerializer):
    bem_produzido = serializers.SlugRelatedField(queryset=BemProduzido.objects.all(), slug_field='uuid')
    especificacao_do_bem = EspecificacaoMaterialServicoSerializer(read_only=True)

    class Meta:
        model = BemProduzidoItem
        fields = ('uuid', 'bem_produzido', 'num_processo_incorporacao', 'quantidade',
                  'valor_individual', 'especificacao_do_bem')

class BemProduzidoItemCreateSerializer(serializers.ModelSerializer):
    especificacao_do_bem = serializers.SlugRelatedField(
        queryset=EspecificacaoMaterialServico.objects.all(),
        slug_field='uuid',
        required=True,
        allow_null=False
    )
    num_processo_incorporacao = serializers.CharField(required=True)
    quantidade = serializers.IntegerField(required=True)
    valor_individual = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

    class Meta:
        model = BemProduzidoItem
        fields = (
            'uuid',
            'num_processo_incorporacao',
            'quantidade',
            'valor_individual',
            'especificacao_do_bem',
        )

class BemProduzidoRascunhoItemSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=False, allow_null=True)
    especificacao_do_bem = serializers.SlugRelatedField(
        queryset=EspecificacaoMaterialServico.objects.all(),
        slug_field='uuid',
        required=False,
        allow_null=True
    )
    num_processo_incorporacao = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    quantidade = serializers.IntegerField(required=False, allow_null=True)
    valor_individual = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)

    def to_internal_value(self, data):
        clean_data = {k: v for k, v in data.items() if v is not None and v != ""}

        if 'especificacao_do_bem' in clean_data and isinstance(clean_data['especificacao_do_bem'], dict):
            clean_data['especificacao_do_bem'] = clean_data['especificacao_do_bem'].get('uuid')
        
        return super().to_internal_value(clean_data)

    class Meta:
        model = BemProduzidoItem
        fields = (
            'uuid',
            'num_processo_incorporacao',
            'quantidade',
            'valor_individual',
            'especificacao_do_bem',
        )