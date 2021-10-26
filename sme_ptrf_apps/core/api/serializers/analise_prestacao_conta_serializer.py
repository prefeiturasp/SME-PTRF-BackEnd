from rest_framework import serializers

from ...models import AnalisePrestacaoConta, PrestacaoConta
from ...api.serializers import DevolucaoPrestacaoContaRetrieveSerializer


class AnalisePrestacaoContaRetrieveSerializer(serializers.ModelSerializer):

    prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=PrestacaoConta.objects.all()
    )

    devolucao_prestacao_conta = DevolucaoPrestacaoContaRetrieveSerializer(many=False)

    class Meta:
        model = AnalisePrestacaoConta
        fields = ('uuid', 'id', 'prestacao_conta', 'devolucao_prestacao_conta', 'status', 'criado_em', 'versao')
