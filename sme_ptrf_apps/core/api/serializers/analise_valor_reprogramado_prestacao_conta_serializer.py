from rest_framework import serializers

from ...models import AnaliseValorReprogramadoPrestacaoConta, AnalisePrestacaoConta, ContaAssociacao, AcaoAssociacao
from ..serializers import AcaoAssociacaoAjustesValoresIniciasSerializer
from ..serializers import ContaAssociacaoLookUpSerializer


class AnaliseValorReprogramadoPrestacaoContaSerializer(serializers.ModelSerializer):

    analise_prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AnalisePrestacaoConta.objects.all()
    )

    conta_associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=ContaAssociacao.objects.all()
    )

    acao_associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AcaoAssociacao.objects.all()
    )

    class Meta:
        model = AnaliseValorReprogramadoPrestacaoConta
        fields = (
        'uuid', 'analise_prestacao_conta', 'conta_associacao', 'acao_associacao', 'valor_saldo_reprogramado_correto',
        'novo_saldo_reprogramado_custeio', 'novo_saldo_reprogramado_capital', 'novo_saldo_reprogramado_livre')


class AjustesSaldosIniciaisSerializer(serializers.ModelSerializer):

    analise_prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AnalisePrestacaoConta.objects.all()
    )
    conta_associacao = ContaAssociacaoLookUpSerializer()
    acao_associacao = AcaoAssociacaoAjustesValoresIniciasSerializer()

    class Meta:
        model = AnaliseValorReprogramadoPrestacaoConta
        fields = (
        'uuid', 'analise_prestacao_conta', 'conta_associacao', 'acao_associacao','valor_saldo_reprogramado_correto',
        'novo_saldo_reprogramado_custeio', 'novo_saldo_reprogramado_capital', 'novo_saldo_reprogramado_livre')
