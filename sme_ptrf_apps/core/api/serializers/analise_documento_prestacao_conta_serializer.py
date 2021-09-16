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
    tipo_documento_prestacao_conta = TipoDocumentoPrestacaoContaSerializer(many=False)
    conta_associacao = ContaAssociacaoLookUpSerializer(many=False)
    solicitacoes_de_ajuste_da_analise = SolicitacaoAcertoDocumentoRetrieveSerializer(many=True)

    class Meta:
        model = AnaliseLancamentoPrestacaoConta
        fields = (
            'analise_prestacao_conta',
            'tipo_documento_prestacao_conta',
            'conta_associacao',
            'resultado',
            'id',
            'uuid',
            'solicitacoes_de_ajuste_da_analise',
        )
