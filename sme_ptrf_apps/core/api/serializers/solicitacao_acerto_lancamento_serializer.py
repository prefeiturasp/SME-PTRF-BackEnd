from rest_framework import serializers

from ...models import SolicitacaoAcertoLancamento, AnaliseLancamentoPrestacaoConta
from ..serializers.tipo_acerto_lancamento_serializer import TipoAcertoLancamentoSerializer
from ..serializers.solicitacao_devolucao_ao_tesouro_serializer import SolicitacaoDevolucaoAoTesouroRetrieveSerializer


class SolicitacaoAcertoLancamentoRetrieveSerializer(serializers.ModelSerializer):
    analise_lancamento = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AnaliseLancamentoPrestacaoConta.objects.all()
    )

    tipo_acerto = TipoAcertoLancamentoSerializer(many=False)
    # devolucao_ao_tesouro = DevolucaoAoTesouroRetrieveSerializer(many=False)
    devolucao_ao_tesouro = SolicitacaoDevolucaoAoTesouroRetrieveSerializer(source='solicitacao_devolucao_ao_tesouro', many=False)

    class Meta:
        model = SolicitacaoAcertoLancamento
        fields = (
            'analise_lancamento',
            'tipo_acerto',
            'detalhamento',
            'devolucao_ao_tesouro',
            'id',
            'uuid',
            'copiado',
            'status_realizacao',
            'justificativa',
            'esclarecimentos',
        )

