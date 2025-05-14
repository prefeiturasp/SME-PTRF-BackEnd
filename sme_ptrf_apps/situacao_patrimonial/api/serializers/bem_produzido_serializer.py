from rest_framework import serializers

from sme_ptrf_apps.despesas.api.serializers.especificacao_material_servico_serializer import EspecificacaoMaterialServicoSerializer
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido, BemProduzidoDespesa
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.situacao_patrimonial.api.serializers.bem_produzido_despesa_serializer import BemProduzidoDespesaSerializer 
from sme_ptrf_apps.despesas.models import EspecificacaoMaterialServico


class BemProduzidoSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(queryset=Associacao.objects.all(), slug_field='uuid')
    especificacao_do_bem = EspecificacaoMaterialServicoSerializer(read_only=True)
    despesas = BemProduzidoDespesaSerializer(read_only=True, many=True)

    class Meta:
        model = BemProduzido
        fields = ('uuid','associacao', 'num_processo_incorporacao', 'quantidade', 'valor_individual', 'status', 'despesas', 'especificacao_do_bem')
        read_only_fields = ['despesas']
