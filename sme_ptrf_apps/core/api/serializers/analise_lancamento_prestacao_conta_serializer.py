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

    # remover esse bloco após testes
    # solicitacoes_de_ajuste_da_analise = SolicitacaoAcertoLancamentoRetrieveSerializer(many=True)

    solicitacoes_de_ajuste_da_analise = serializers.SerializerMethodField('get_solicitacoes_ajuste')

    def get_solicitacoes_ajuste(self, obj):
        return obj.solicitacoes_de_acertos_agrupado_por_categoria()

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
            'status_realizacao',
            'justificativa',
            'devolucao_tesouro_atualizada',
            'requer_atualizacao_devolucao_ao_tesouro',
            'lancamento_atualizado',
            'requer_atualizacao_lancamento',
            'lancamento_excluido',
            'requer_exclusao_lancamento',
            'requer_ajustes_externos',
            'requer_esclarecimentos',
            'esclarecimentos',
        )


class AnaliseLancamentoPrestacaoContaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnaliseLancamentoPrestacaoConta
        fields = (
            'justificativa',
        )
