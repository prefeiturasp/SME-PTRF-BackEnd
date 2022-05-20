from rest_framework import serializers

from ...models import PrestacaoConta, DevolucaoPrestacaoConta


class DevolucaoPrestacaoContaRetrieveSerializer(serializers.ModelSerializer):
    prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=PrestacaoConta.objects.all()
    )

    class Meta:
        model = DevolucaoPrestacaoConta
        order_by = 'id'
        fields = ('uuid', 'prestacao_conta', 'data', 'data_limite_ue', 'data_retorno_ue')
