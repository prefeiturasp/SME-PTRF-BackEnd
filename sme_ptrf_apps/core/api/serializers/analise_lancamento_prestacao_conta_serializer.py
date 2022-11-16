from rest_framework import serializers

from ...models import AnalisePrestacaoConta, AnaliseLancamentoPrestacaoConta
from ....despesas.models import Despesa
from ....receitas.models import Receita


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

    solicitacoes_de_ajuste_da_analise = serializers.SerializerMethodField('get_solicitacoes_ajuste')

    def get_solicitacoes_ajuste(self, obj):
        return obj.solicitacoes_de_acertos_agrupado_por_categoria()

    solicitacoes_de_ajuste_da_analise_total = serializers.SerializerMethodField('get_solicitacoes_ajuste_total')

    def get_solicitacoes_ajuste_total(self, obj):
        return obj.solicitacoes_de_acertos_total()

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
            'solicitacoes_de_ajuste_da_analise_total',
            'solicitacoes_de_ajuste_da_analise',
            'status_realizacao',
            'devolucao_tesouro_atualizada',
            'requer_atualizacao_devolucao_ao_tesouro',
            'lancamento_atualizado',
            'requer_atualizacao_lancamento',
            'lancamento_excluido',
            'requer_exclusao_lancamento',
            'requer_ajustes_externos',
            'requer_esclarecimentos',
        )

