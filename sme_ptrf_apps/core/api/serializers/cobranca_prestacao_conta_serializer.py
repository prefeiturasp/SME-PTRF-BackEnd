from rest_framework import serializers

from ...models import CobrancaPrestacaoConta, PrestacaoConta


class CobrancaPrestacaoContaListSerializer(serializers.ModelSerializer):
    prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=PrestacaoConta.objects.all()
    )

    class Meta:
        model = CobrancaPrestacaoConta
        fields = ('uuid', 'prestacao_conta', 'tipo', 'data')
