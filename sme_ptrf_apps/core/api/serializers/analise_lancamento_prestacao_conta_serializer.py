from rest_framework import serializers

from ...models import SolicitacaoAcertoLancamento, AnalisePrestacaoConta, AnaliseLancamentoPrestacaoConta
from ....despesas.models import Despesa
from ....receitas.models import Receita
from .solicitacao_acerto_lancamento_serializer import SolicitacaoAcertoLancamentoRetrieveSerializer


class AnaliseLancamentoPrestacaoContaRetrieveSerializer(serializers.ModelSerializer):

    analise_prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AnalisePrestacaoConta.objects.all()
    )

    despesa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Despesa.objects.all()
    )

    receita = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Receita.objects.all()
    )

    solicitacoes_de_ajuste_da_analise = SolicitacaoAcertoLancamentoRetrieveSerializer(many=True)

    class Meta:
        model = AnaliseLancamentoPrestacaoConta
        fields = (
            'analise_prestacao_conta',
            'tipo_lancamento',
            'despesa',
            'receita',
            'resultado',
            'id',
            'uuid',
            'solicitacoes_de_ajuste_da_analise',
        )
