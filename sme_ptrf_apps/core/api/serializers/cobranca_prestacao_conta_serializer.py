from rest_framework import serializers

from ...models import CobrancaPrestacaoConta, PrestacaoConta, Associacao, Periodo


class CobrancaPrestacaoContaListSerializer(serializers.ModelSerializer):
    prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=PrestacaoConta.objects.all()
    )

    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    periodo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Periodo.objects.all()
    )

    class Meta:
        model = CobrancaPrestacaoConta
        fields = ('uuid', 'prestacao_conta', 'tipo', 'data', 'associacao', 'periodo')
