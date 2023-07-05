from rest_framework import serializers

from ...models import AnaliseContaPrestacaoConta, PrestacaoConta, AnalisePrestacaoConta
from ...api.serializers import ContaAssociacaoDadosSerializer


class AnaliseContaPrestacaoContaRetrieveSerializer(serializers.ModelSerializer):
    prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=PrestacaoConta.objects.all()
    )

    analise_prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AnalisePrestacaoConta.objects.all()
    )

    conta_associacao = ContaAssociacaoDadosSerializer(many=False)

    class Meta:
        model = AnaliseContaPrestacaoConta
        fields = (
            'uuid', 'prestacao_conta', 'conta_associacao', 'data_extrato', 'saldo_extrato', 'analise_prestacao_conta',
            'solicitar_envio_do_comprovante_do_saldo_da_conta',
            'observacao_solicitar_envio_do_comprovante_do_saldo_da_conta'
        )
