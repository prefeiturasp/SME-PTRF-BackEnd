from rest_framework import serializers
from sme_ptrf_apps.situacao_patrimonial.api.serializers.despesa_situacao_patrimonial_serializer import DespesaSituacaoPatrimonialSerializer
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoDespesa

class BemProduzidoDespesaSerializer(serializers.ModelSerializer):
    despesa = DespesaSituacaoPatrimonialSerializer(read_only=True)

    class Meta:
        model = BemProduzidoDespesa
        fields = ('despesa',)
