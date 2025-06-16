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
