from rest_framework import serializers

from ...models import ComentarioAnalisePrestacao, PrestacaoConta


class ComentarioAnalisePrestacaoRetrieveSerializer(serializers.ModelSerializer):
    prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=PrestacaoConta.objects.all()
    )

    class Meta:
        model = ComentarioAnalisePrestacao
        order_by = 'ordem'
        fields = ('uuid', 'prestacao_conta', 'ordem', 'comentario')
