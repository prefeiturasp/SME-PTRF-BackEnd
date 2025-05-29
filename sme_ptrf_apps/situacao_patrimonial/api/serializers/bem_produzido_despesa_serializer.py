from rest_framework import serializers
from sme_ptrf_apps.situacao_patrimonial.api.serializers.despesa_situacao_patrimonial_serializer import DespesaSituacaoPatrimonialSerializer
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoDespesa

class BemProduzidoDespesaSerializer(serializers.ModelSerializer):
    despesa = DespesaSituacaoPatrimonialSerializer(read_only=True)
    bem_produzido_uuid = serializers.SerializerMethodField()
    bem_produzido_despesa_uuid = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = BemProduzidoDespesa
        fields = ('bem_produzido_despesa_uuid', 'bem_produzido_uuid', 'despesa')

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
