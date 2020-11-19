from rest_framework import serializers

from ...models import PrestacaoConta, DevolucaoAoTesouro
from ...api.serializers.tipo_devolucao_ao_tesouro_serializer import TipoDevolucaoAoTesouroSerializer
from ....despesas.api.serializers.despesa_serializer import DespesaListSerializer


class DevolucaoAoTesouroRetrieveSerializer(serializers.ModelSerializer):
    prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=PrestacaoConta.objects.all()
    )

    tipo = TipoDevolucaoAoTesouroSerializer(many=False)
    despesa = DespesaListSerializer(many=False)

    class Meta:
        model = DevolucaoAoTesouro
        order_by = 'id'
        fields = (
            'uuid',
            'prestacao_conta',
            'tipo',
            'data',
            'despesa',
            'devolucao_total',
            'valor',
            'motivo',
            'visao_criacao'
        )
