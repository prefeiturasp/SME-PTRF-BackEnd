from rest_framework import serializers

from django.db.models import Sum

from sme_ptrf_apps.despesas.api.serializers.rateio_despesa_serializer import RateioDespesaSerializer
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoDespesa, BemProduzidoRateio
from sme_ptrf_apps.despesas.models import RateioDespesa

class BemProduzidoRateioSerializer(serializers.ModelSerializer):
    bem_produzido_despesa = serializers.SlugRelatedField(queryset=BemProduzidoDespesa.objects.all(), slug_field='uuid')
    rateio = RateioDespesaSerializer(read_only=True)
    valor_disponivel = serializers.SerializerMethodField()

    class Meta:
        model = BemProduzidoRateio
        fields = ('uuid','bem_produzido_despesa', 'rateio', 'valor_disponivel')
        read_only_fields = ['valor_disponivel']
        
    def get_valor_disponivel(self, obj):
      total_utilizado = BemProduzidoRateio.objects.filter(rateio=obj.rateio).aggregate(
          total=Sum('valor_utilizado')
      )['total'] or 0

      valor_total_rateio = obj.rateio.valor_rateio

      return valor_total_rateio - total_utilizado