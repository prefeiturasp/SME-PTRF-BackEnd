from rest_framework import serializers

from django.db.models import Sum

from sme_ptrf_apps.situacao_patrimonial.api.serializers.despesa_situacao_patrimonial_serializer import DespesaSituacaoPatrimonialSerializer
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoDespesa

class BemProduzidoDespesaSerializer(serializers.ModelSerializer):
    despesa = DespesaSituacaoPatrimonialSerializer(read_only=True)
    bem_produzido_uuid = serializers.SerializerMethodField()
    bem_produzido_despesa_uuid = serializers.UUIDField(source='uuid', read_only=True)
    valor_recurso_proprio_disponivel = serializers.SerializerMethodField()

    class Meta:
        model = BemProduzidoDespesa
        fields = ('bem_produzido_despesa_uuid', 'bem_produzido_uuid', 'despesa', 'valor_recurso_proprio_utilizado', 'valor_recurso_proprio_disponivel')

    def get_bem_produzido_uuid(self, obj):
        return str(obj.bem_produzido.uuid)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        despesa_serializer = DespesaSituacaoPatrimonialSerializer(
            instance.despesa,
            context={'bem_produzido_uuid': str(instance.bem_produzido.uuid)}
        )
        representation['despesa'] = despesa_serializer.data
        return representation

    def get_valor_recurso_proprio_disponivel(self, obj):
        despesa = obj.despesa
        if not despesa:
            return None

        valor_total = despesa.valor_recursos_proprios or 0

        soma_utilizado = (
            BemProduzidoDespesa.objects
            .filter(despesa=despesa)
            .aggregate(total=Sum('valor_recurso_proprio_utilizado'))['total'] or 0
        )

        return valor_total - soma_utilizado