from rest_framework import serializers

from ...models import SolicitacaoDevolucaoAoTesouro
from ...api.serializers.tipo_devolucao_ao_tesouro_serializer import TipoDevolucaoAoTesouroSerializer
from ....despesas.api.serializers.despesa_serializer import DespesaListSerializer


class SolicitacaoDevolucaoAoTesouroRetrieveSerializer(serializers.ModelSerializer):
    prestacao_conta = serializers.SerializerMethodField('get_prestacao_conta')
    tipo = TipoDevolucaoAoTesouroSerializer(many=False)
    data = serializers.SerializerMethodField('get_data')
    despesa = serializers.SerializerMethodField('get_despesa')
    visao_criacao = serializers.SerializerMethodField('get_visao_criacao')

    def get_prestacao_conta(self, obj):
        if (
            obj.solicitacao_acerto_lancamento and
            obj.solicitacao_acerto_lancamento.analise_lancamento and
            obj.solicitacao_acerto_lancamento.analise_lancamento.analise_prestacao_conta and
            obj.solicitacao_acerto_lancamento.analise_lancamento.analise_prestacao_conta.prestacao_conta
        ):
            return obj.solicitacao_acerto_lancamento.analise_lancamento.analise_prestacao_conta.prestacao_conta.uuid
        else:
            return None

    def get_data(self, obj):
        # Existe apenas por compatibilidade. Sempre retornará uma data nula.
        return None

    def get_despesa(self, obj):
        if (
            obj.solicitacao_acerto_lancamento and
            obj.solicitacao_acerto_lancamento.analise_lancamento and
            obj.solicitacao_acerto_lancamento.analise_lancamento.despesa
        ):
            despesa = obj.solicitacao_acerto_lancamento.analise_lancamento.despesa
        else:
            despesa = None
        return DespesaListSerializer(despesa, many=False).data

    def get_visao_criacao(self, obj):
        # Existe apenas por compatibilidade. Sempre retornará 'DRE'.
        return "DRE"

    class Meta:
        model = SolicitacaoDevolucaoAoTesouro
        order_by = 'id'
        fields = (
            'uuid',
            'prestacao_conta',
            'tipo',
            'data',
            'despesa',
            'devolucao_total',
            'valor',
            'motivo',
            'visao_criacao'
        )
