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

    pode_reprocessar_relatorio_apos_acertos = serializers.SerializerMethodField('get_pode_reprocessar_relatorio_apos_acertos')

    def get_pode_reprocessar_relatorio_apos_acertos(self, obj):
        return obj.status_versao_apresentacao_apos_acertos == AnalisePrestacaoConta.STATUS_FALHA_AO_GERAR

    class Meta:
        model = AnalisePrestacaoConta
        fields = ('uuid', 'id', 'prestacao_conta', 'devolucao_prestacao_conta', 'status', 'criado_em',
                'versao', 'versao_pdf_apresentacao_apos_acertos', 'pode_reprocessar_relatorio_apos_acertos')
