from rest_framework import serializers

from ...models import SolicitacaoAcertoDocumento, AnalisePrestacaoConta, AnaliseLancamentoPrestacaoConta

from .solicitacao_acerto_documento_serializer import SolicitacaoAcertoDocumentoRetrieveSerializer
from .tipo_documento_prestacao_conta_serializer import TipoDocumentoPrestacaoContaSerializer
from .conta_associacao_serializer import ContaAssociacaoLookUpSerializer


class AnaliseDocumentoPrestacaoContaRetrieveSerializer(serializers.ModelSerializer):

    analise_prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AnalisePrestacaoConta.objects.all()
    )
    documento = serializers.SerializerMethodField('get_nome_documento')
    tipo_documento_prestacao_conta = TipoDocumentoPrestacaoContaSerializer(many=False)
    conta_associacao = ContaAssociacaoLookUpSerializer(many=False)
    solicitacoes_de_ajuste_da_analise = SolicitacaoAcertoDocumentoRetrieveSerializer(many=True)

    def get_nome_documento(self, obj):
        _documento = obj.tipo_documento_prestacao_conta
        _conta_associacao = obj.conta_associacao
        return f'{_documento.nome} {_conta_associacao.tipo_conta.nome}' if _conta_associacao else _documento.nome

    class Meta:
        model = AnaliseLancamentoPrestacaoConta
        fields = (
            'analise_prestacao_conta',
            'documento',
            'tipo_documento_prestacao_conta',
            'conta_associacao',
            'resultado',
            'id',
            'uuid',
            'solicitacoes_de_ajuste_da_analise',
        )
