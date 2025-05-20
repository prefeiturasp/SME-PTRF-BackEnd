from rest_framework import serializers
from sme_ptrf_apps.despesas.api.serializers.despesa_serializer import DespesaSerializer
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoDespesa
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido
from sme_ptrf_apps.despesas.models import Despesa

class BemProduzidoDespesaSerializer(serializers.ModelSerializer):
    despesa = DespesaSerializer(read_only=True)

    class Meta:
        model = BemProduzidoDespesa
        fields = ('uuid', 'despesa')
