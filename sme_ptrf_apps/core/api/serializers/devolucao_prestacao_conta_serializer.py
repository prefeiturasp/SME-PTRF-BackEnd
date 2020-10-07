from rest_framework import serializers

from ...models import PrestacaoConta, DevolucaoPrestacaoConta
from ...api.serializers import CobrancaPrestacaoContaListSerializer


class DevolucaoPrestacaoContaRetrieveSerializer(serializers.ModelSerializer):
    prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=PrestacaoConta.objects.all()
    )

    cobrancas_da_devolucao = CobrancaPrestacaoContaListSerializer(many=True)

    class Meta:
        model = DevolucaoPrestacaoConta
        order_by = 'id'
        fields = ('uuid', 'prestacao_conta', 'data', 'data_limite_ue', 'cobrancas_da_devolucao')
